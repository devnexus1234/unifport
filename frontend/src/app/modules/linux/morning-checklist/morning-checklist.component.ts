import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import {
    MorningChecklistService,
    SummaryResponse,
    SummaryGroup,
    HostnameDetail,
    AggregatedValidatedItem,
    CommandDiff
} from './services/morning-checklist.service';
import { CommentDialogComponent } from './components/comment-dialog/comment-dialog.component';

@Component({
    selector: 'app-morning-checklist',
    templateUrl: './morning-checklist.component.html',
    styleUrls: ['./morning-checklist.component.scss']
})
export class MorningChecklistComponent implements OnInit {
    dates: string[] = [];
    availableDates: Date[] = [];
    selectedDate: Date | null = null;
    minDate: Date = new Date();
    maxDate: Date = new Date();
    summary?: SummaryResponse;
    groups: SummaryGroup[] = [];
    filters: { application_name?: string; asset_owner?: string; show_errors_only?: boolean } = {};
    applicationOwnerMap: Record<string, string[]> = {};
    availableOwners: string[] = [];
    loadingDates = false;
    loadingSummary = false;
    loadingDetails = false;
    selectedStatus: 'success' | 'error' | null = null;
    detailRows: HostnameDetail[] = [];
    selectedHostname: string = '';
    selectedHostnameDetails: CommandDiff[] = [];
    loadingHostnameDetails = false;
    previousDate: Date | null = null;
    selectedTabIndex = 0;

    // Validated items
    validatedItems: AggregatedValidatedItem[] = [];
    loadingValidated = false;

    // Selection
    selectedHostnames: Set<string> = new Set();
    selectedGroups: Set<SummaryGroup> = new Set();

    @ViewChild('hostnameDetailsDialog') hostnameDetailsDialog!: TemplateRef<any>;

    constructor(
        private service: MorningChecklistService,
        private snackBar: MatSnackBar,
        private dialog: MatDialog,
        private router: Router
    ) { }

    ngOnInit(): void {
        this.loadDates();
        this.loadApplicationOwnerMap();
    }

    onTabChange(index: number) {
        if (index === 2) {
            this.loadValidatedHostnames();
        }
    }

    loadDates() {
        this.loadingDates = true;

        // Set min and max dates first (today to 7 days ago)
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        this.maxDate = new Date(today); // Today is the maximum
        this.minDate = new Date(today);
        this.minDate.setDate(today.getDate() - 6); // 7 days ago (including today = 7 days total)

        this.service.getDates().subscribe({
            next: (dates) => {
                this.dates = dates || [];
                this.loadingDates = false;

                // Convert string dates to Date objects for the date picker
                this.availableDates = this.dates.map(d => new Date(d));

                if (this.dates.length > 0) {
                    this.selectedDate = new Date(this.dates[0]);
                } else {
                    this.selectedDate = new Date(today);
                }

                if (this.selectedDate) {
                    this.loadSummary();
                }
            },
            error: (error) => {
                console.error('Error loading dates:', error);
                this.loadingDates = false;
                // Even if dates fail to load, allow date selection in the range
                this.selectedDate = new Date(today);
                this.snackBar.open('Unable to load available dates, but you can still select dates', 'Dismiss', { duration: 3000 });
            }
        });
    }

    dateFilter = (d: Date | null): boolean => {
        // Allow any date within the min/max range (today to 7 days ago)
        // The [min] and [max] inputs on the datepicker handle the range constraints.
        return true;
    }

    onDateChange(date: Date | null) {
        if (date) {
            // Normalize the date to avoid timezone issues
            const normalizedDate = new Date(date);
            normalizedDate.setHours(0, 0, 0, 0);
            this.selectedDate = normalizedDate;
            this.loadSummary();
        }
    }

    loadApplicationOwnerMap() {
        this.service.getApplicationOwnerMapping().subscribe({
            next: (map) => {
                this.applicationOwnerMap = map;
                if (this.filters.application_name) {
                    this.availableOwners = map[this.filters.application_name] || [];
                }
            }
        });
    }

    onApplicationChange() {
        this.availableOwners = this.filters.application_name ? (this.applicationOwnerMap[this.filters.application_name] || []) : [];
        if (!this.availableOwners.includes(this.filters.asset_owner || '')) {
            this.filters.asset_owner = undefined;
        }
        this.loadSummary();
        if (this.selectedTabIndex === 2) {
            this.loadValidatedHostnames();
        }
    }

    resetFilters() {
        this.filters = {
            application_name: undefined,
            asset_owner: undefined,
            show_errors_only: false
        };
        this.availableOwners = [];
        this.loadSummary();
        if (this.selectedTabIndex === 2) {
            this.loadValidatedHostnames();
        }
    }

    loadSummary() {
        if (!this.selectedDate) return;
        // Convert Date object to YYYY-MM-DD string, handling timezone correctly
        const year = this.selectedDate.getFullYear();
        const month = String(this.selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(this.selectedDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        this.loadingSummary = true;
        this.service.getSummary(dateStr, this.filters).subscribe({
            next: (data) => {
                this.summary = data;
                this.groups = data.groups || [];
                this.loadingSummary = false;
                this.detailRows = [];
                this.selectedStatus = null;
                this.selectedGroups.clear(); // Clear group selection
            },
            error: (error) => {
                console.error('Error loading summary:', error);
                this.loadingSummary = false;
                this.snackBar.open('Failed to load summary', 'Dismiss', { duration: 3000 });
            }
        });
        this.loadChecklistValidationStatus();
    }

    // Checklist Validation (Sign-off)
    checklistValidation: { validate_by: string, validated_at: string, validate_comment?: string } | null = null;
    loadingChecklistValidation = false;

    loadChecklistValidationStatus() {
        if (!this.selectedDate) return;
        this.loadingChecklistValidation = true;
        const dateStr = this.formatDateForAPI(this.selectedDate);

        this.service.getChecklistValidationStatus(dateStr).subscribe({
            next: (status) => {
                this.checklistValidation = status;
                this.loadingChecklistValidation = false;
            },
            error: () => {
                this.checklistValidation = null;
                this.loadingChecklistValidation = false;
            }
        });
    }

    validateChecklist() {
        if (!this.selectedDate) return;

        const dialogRef = this.dialog.open(CommentDialogComponent, {
            width: '400px',
            data: { title: 'Sign-off Checklist', message: 'Add optional comment for checklist sign-off', required: false }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result !== undefined) {
                const comment = result;
                // const user = 'self'; // In a real app, this should come from auth service
                const user = 'self';
                const dateStr = this.formatDateForAPI(this.selectedDate!);

                this.service.validateChecklist(dateStr, user, comment || undefined).subscribe({
                    next: () => {
                        this.snackBar.open('Checklist validated successfully', 'Dismiss', { duration: 2000 });
                        this.loadChecklistValidationStatus();
                    },
                    error: () => this.snackBar.open('Failed to validate checklist', 'Dismiss', { duration: 3000 })
                });
            }
        });
    }

    loadValidatedHostnames() {
        if (!this.selectedDate) return;
        this.loadingValidated = true;
        const filters: any = {};

        const dateStr = this.formatDateForAPI(this.selectedDate);
        filters.start_date = dateStr;
        filters.end_date = dateStr;

        // Apply filters if present
        if (this.filters.application_name) filters.application_name = this.filters.application_name;
        if (this.filters.asset_owner) filters.asset_owner = this.filters.asset_owner;

        this.service.getValidatedList(filters).subscribe({
            next: (response) => {
                this.validatedItems = response.items;
                this.loadingValidated = false;
            },
            error: (err) => {
                console.error('Error loading validated items', err);
                this.loadingValidated = false;
                this.snackBar.open('Failed to load validated hostnames', 'Dismiss', { duration: 3000 });
            }
        });
    }

    selectedReachability: string | null = null;
    // ...

    viewDetails(status: 'success' | 'error' | null, group?: SummaryGroup, mc_status?: string) {
        if (!this.selectedDate) return;

        this.selectedStatus = status;
        this.selectedReachability = mc_status || null;
        this.loadingDetails = true;
        this.selectedTabIndex = 1; // Switch to Details tab

        const filters: any = { ...this.filters };
        if (group) {
            filters.application_name = group.application_name;
            filters.asset_owner = group.asset_owner || undefined;
        }

        const dateStr = this.formatDateForAPI(this.selectedDate);
        // If mc_status is set, we don't pass status (success/error) unless intended.
        // Usually if clicking reachability, we want ALL items with that status regardless of diff.
        const statusParam = mc_status ? undefined : (status || undefined);

        this.service.getDetails(dateStr, statusParam, filters, mc_status).subscribe({
            next: (rows) => {
                this.detailRows = rows;
                this.loadingDetails = false;
                this.selectedHostnames.clear(); // Clear selection when loading new details
            },
            error: () => {
                this.loadingDetails = false;
                this.snackBar.open('Failed to load details', 'Dismiss', { duration: 3000 });
            }
        });
    }

    showReachabilityDetails(type: 'total' | 'reachable' | 'failed' | 'unreachable') {
        this.viewDetails(null, undefined, type);
    }



    showHostnameDetails(hostname: string, checkDate?: string) {
        const targetDate = checkDate ? new Date(checkDate) : this.selectedDate;

        if (!targetDate) return;
        this.selectedHostname = hostname;
        this.loadingHostnameDetails = true;

        // Calculate previous date (D-1) based on TARGET date
        const prevDate = new Date(targetDate);
        prevDate.setDate(prevDate.getDate() - 1);
        this.previousDate = prevDate;

        // Format target date for API, handling timezone
        const year = targetDate.getFullYear();
        const month = String(targetDate.getMonth() + 1).padStart(2, '0');
        const day = String(targetDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;

        this.service.getDiff(hostname, dateStr).subscribe({
            next: (diffs) => {
                this.selectedHostnameDetails = diffs;
                this.loadingHostnameDetails = false;
                this.dialog.open(this.hostnameDetailsDialog, {
                    width: '90%',
                    maxWidth: '1200px',
                    maxHeight: '90vh'
                });
            },
            error: () => {
                this.loadingHostnameDetails = false;
                this.snackBar.open('Failed to load hostname details', 'Dismiss', { duration: 3000 });
            }
        });
    }

    formatPreviousDateString(): string {
        if (!this.previousDate) return '';
        const year = this.previousDate.getFullYear();
        const month = String(this.previousDate.getMonth() + 1).padStart(2, '0');
        const day = String(this.previousDate.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    getSideBySideDiff(diff: CommandDiff): { left: { line: string, type: string }, right: { line: string, type: string } }[] {
        const rows: { left: { line: string, type: string }, right: { line: string, type: string } }[] = [];

        // If no diff, just show current output on both sides (or just one side? No, side-by-side usually implies comparison)
        // Actually if no diff, current and previous should be same.
        if (!diff.diff || diff.diff.length === 0) {
            const currentLines = (diff.current_output || '').split('\n');
            const previousLines = (diff.previous_output || '').split('\n');
            const maxLines = Math.max(currentLines.length, previousLines.length);

            for (let i = 0; i < maxLines; i++) {
                rows.push({
                    left: { line: previousLines[i] || '', type: 'context' },
                    right: { line: currentLines[i] || '', type: 'context' }
                });
            }
            return rows;
        }

        // Parse unified diff
        // A simplified parser that tries to align blocks.
        // We iterate through the diff lines.
        // - lines starting with ' ' are context -> add to both
        // - lines starting with '-' are del -> add to left, right is empty (for now)
        // - lines starting with '+' are add -> add to right, left is empty (for now)
        // To align, we collect a block of deletes and a block of adds.

        let i = 0;
        while (i < diff.diff.length) {
            const line = diff.diff[i];

            if (line.startsWith('@@')) {
                rows.push({
                    left: { line: line, type: 'meta' },
                    right: { line: line, type: 'meta' }
                });
                i++;
            } else if (line.startsWith(' ')) {
                const content = line.substring(1);
                rows.push({
                    left: { line: content, type: 'context' },
                    right: { line: content, type: 'context' }
                });
                i++;
            } else if (line.startsWith('-') || line.startsWith('+')) {
                // Collect a block of changes
                const dels: string[] = [];
                const adds: string[] = [];

                while (i < diff.diff.length) {
                    const l = diff.diff[i];
                    if (l.startsWith('-')) {
                        dels.push(l.substring(1));
                        i++;
                    } else if (l.startsWith('+')) {
                        adds.push(l.substring(1));
                        i++;
                    } else {
                        break;
                    }
                }

                // Now add them to rows side-by-side
                const maxBlock = Math.max(dels.length, adds.length);
                for (let j = 0; j < maxBlock; j++) {
                    rows.push({
                        left: { line: dels[j] || '', type: dels[j] !== undefined ? 'del' : 'empty' },
                        right: { line: adds[j] || '', type: adds[j] !== undefined ? 'add' : 'empty' }
                    });
                }
            } else {
                // Fallback for unexpected lines (header etc)
                i++;
            }
        }

        return rows;
    }

    validateHost(hostname: string) {
        if (!this.selectedDate) return;

        const dialogRef = this.dialog.open(CommentDialogComponent, {
            width: '400px',
            data: { title: 'Validate Hostname', message: `Add optional comment for ${hostname}`, required: false }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result !== undefined) {
                const comment = result;
                const user = 'self';
                const dateStr = this.formatDateForAPI(this.selectedDate!);
                this.service.validateHost(hostname, dateStr, user, comment || undefined).subscribe({
                    next: () => {
                        this.snackBar.open('Hostname validated', 'Dismiss', { duration: 2000 });
                        this.loadSummary();
                        this.loadValidatedHostnames();
                        if (this.selectedStatus) this.viewDetails(this.selectedStatus);
                    },
                    error: () => this.snackBar.open('Validation failed', 'Dismiss', { duration: 3000 })
                });
            }
        });
    }

    undoValidation(hostname: string, date: string) {
        if (!confirm(`Are you sure you want to undo validation for ${hostname}?`)) {
            return;
        }

        this.service.undoValidation(hostname, date).subscribe({
            next: () => {
                this.snackBar.open(`Validation undone for ${hostname}`, 'Dismiss', { duration: 3000 });
                this.loadSummary();
                this.loadValidatedHostnames();
                if (this.selectedStatus) this.viewDetails(this.selectedStatus);
            },
            error: (err) => {
                this.snackBar.open('Failed to undo validation', 'Dismiss', { duration: 3000 });
                console.error(err);
            }
        });
    }

    bulkValidate() {
        if (!this.selectedDate) return;
        if (!this.filters.application_name) {
            this.snackBar.open('Select application to bulk validate', 'Dismiss', { duration: 3000 });
            return;
        }

        const dialogRef = this.dialog.open(CommentDialogComponent, {
            width: '400px',
            data: { title: 'Bulk Validate All', message: 'Provide reason for bulk validating ALL displayed items', required: true }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result !== undefined) {
                const comment = result;
                const user = 'self';
                const dateStr = this.formatDateForAPI(this.selectedDate!);
                this.service
                    .validateAll(dateStr, this.filters.application_name!, user, this.filters.asset_owner, comment || undefined)
                    .subscribe({
                        next: () => {
                            this.snackBar.open('Bulk validation completed', 'Dismiss', { duration: 2000 });
                            this.loadSummary();
                            this.loadValidatedHostnames();
                            if (this.selectedStatus) this.viewDetails(this.selectedStatus);
                        },
                        error: () => this.snackBar.open('Bulk validation failed', 'Dismiss', { duration: 3000 })
                    });
            }
        });
    }

    // Selection Logic
    toggleSelection(hostname: string) {
        if (this.selectedHostnames.has(hostname)) {
            this.selectedHostnames.delete(hostname);
        } else {
            this.selectedHostnames.add(hostname);
        }
    }

    isAllSelected(): boolean {
        if (this.detailRows.length === 0) return false;
        // Check if all rows that CAN be selected ARE selected (e.g. error rows)
        // If we are showing "success" rows, maybe we don't allow selection? 
        // Assuming selection is allowed for any displayed row if we want to validate it.
        // Usually we only validate ERRORS.
        // Let's assume we can validate any row (maybe to force validation even if success?)
        const total = this.detailRows.length;
        const selected = this.detailRows.filter(r => this.selectedHostnames.has(r.hostname)).length;
        return selected === total;
    }

    masterToggle() {
        if (this.isAllSelected()) {
            this.selectedHostnames.clear();
        } else {
            this.detailRows.forEach(row => this.selectedHostnames.add(row.hostname));
        }
    }

    validateSelectedHostnames() {
        if (this.selectedHostnames.size === 0) return;
        if (!this.selectedDate) return;

        const dialogRef = this.dialog.open(CommentDialogComponent, {
            width: '400px',
            data: { title: 'Validate Selected', message: `Validate ${this.selectedHostnames.size} selected items?`, required: true }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result !== undefined) {
                const comment = result;
                const user = 'self';
                const dateStr = this.formatDateForAPI(this.selectedDate!);

                this.service.validateSelected(dateStr, Array.from(this.selectedHostnames), user, comment).subscribe({
                    next: () => {
                        this.snackBar.open('Selected items validated', 'Dismiss', { duration: 2000 });
                        this.selectedHostnames.clear();
                        this.loadSummary();
                        this.loadValidatedHostnames();
                        if (this.selectedStatus) this.viewDetails(this.selectedStatus);
                    },
                    error: () => this.snackBar.open('Failed to validate selected items', 'Dismiss', { duration: 3000 })
                });
            }
        });
    }

    // Group Selection Logic
    toggleGroupSelection(group: SummaryGroup) {
        if (group.error_count === 0) return;

        if (this.selectedGroups.has(group)) {
            this.selectedGroups.delete(group);
        } else {
            this.selectedGroups.add(group);
        }
    }

    isAllGroupsSelected(): boolean {
        const groupsWithErrors = this.groups.filter(g => g.error_count > 0);
        if (groupsWithErrors.length === 0) return false;

        const total = groupsWithErrors.length;
        const selected = this.groups.filter(g => this.selectedGroups.has(g)).length;
        return selected === total;
    }

    masterGroupToggle() {
        if (this.isAllGroupsSelected()) {
            this.selectedGroups.clear();
        } else {
            this.groups.filter(g => g.error_count > 0).forEach(g => this.selectedGroups.add(g));
        }
    }

    validateSelectedGroups() {
        if (this.selectedGroups.size === 0) return;
        if (!this.selectedDate) return;

        const dialogRef = this.dialog.open(CommentDialogComponent, {
            width: '400px',
            data: { title: 'Validate Selected Groups', message: `Validate ${this.selectedGroups.size} selected groups?`, required: true }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result !== undefined) {
                const comment = result;
                const user = 'self';
                const dateStr = this.formatDateForAPI(this.selectedDate!);

                this.service.validateGroups(dateStr, Array.from(this.selectedGroups), user, comment).subscribe({
                    next: () => {
                        this.snackBar.open('Selected groups validated', 'Dismiss', { duration: 2000 });
                        this.selectedGroups.clear();
                        this.loadSummary();
                        this.loadValidatedHostnames();
                    },
                    error: () => this.snackBar.open('Failed to validate selected groups', 'Dismiss', { duration: 3000 })
                });
            }
        });
    }

    undoChecklistValidation() {
        if (!this.selectedDate) return;
        const dateStr = this.formatDateForAPI(this.selectedDate);

        if (confirm(`Are you sure you want to undo the checklist validation for ${dateStr}? This will re-open the checklist.`)) {
            this.loadingChecklistValidation = true;
            this.service.undoChecklistValidation(dateStr).subscribe({
                next: () => {
                    this.snackBar.open('Checklist validation undone', 'Dismiss', { duration: 3000 });
                    this.loadChecklistValidationStatus();
                    this.loadingChecklistValidation = false;
                },
                error: (err) => {
                    console.error('Error undoing checklist validation', err);
                    this.snackBar.open('Failed to undo checklist validation', 'Dismiss', { duration: 3000 });
                    this.loadingChecklistValidation = false;
                }
            });
        }
    }

    exportSummary() {
        if (!this.selectedDate) return;
        const dateStr = this.formatDateForAPI(this.selectedDate);
        this.service.exportSummary(dateStr, this.filters).subscribe({
            next: (blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `morning-checklist-${dateStr}.xlsx`;
                a.click();
                window.URL.revokeObjectURL(url);
            },
            error: () => this.snackBar.open('Export failed', 'Dismiss', { duration: 3000 })
        });
    }

    getSelectedDateString(): string {
        if (!this.selectedDate) return '';
        const year = this.selectedDate.getFullYear();
        const month = String(this.selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(this.selectedDate.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    formatDateForAPI(date: Date | null): string {
        if (!date) return '';
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    goBack() {
        this.router.navigate(['/dashboard']);
    }
}
