import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { MorningChecklistService, AggregatedValidatedItem, ValidationHistoryItem } from '../../services/morning-checklist.service';

@Component({
    selector: 'app-validated-hostnames',
    templateUrl: './validated-hostnames.component.html',
    styleUrls: ['./validated-hostnames.component.scss']
})
export class ValidatedHostnamesComponent implements OnInit {
    filters: { start_date?: string; end_date?: string; application_name?: string; asset_owner?: string; validated_by?: string; sort_by?: string } = {
        sort_by: 'validated_at'
    };
    items: AggregatedValidatedItem[] = [];
    loading = false;
    history: ValidationHistoryItem[] = [];
    selectedHostname = '';

    @ViewChild('historyDialog') historyDialog!: TemplateRef<any>;

    constructor(
        private service: MorningChecklistService,
        private snackBar: MatSnackBar,
        private dialog: MatDialog
    ) { }

    ngOnInit(): void {
        this.loadValidated();
    }

    loadValidated() {
        this.loading = true;
        this.service.getValidatedList(this.filters).subscribe({
            next: (resp) => {
                this.items = resp.items || [];
                this.loading = false;
            },
            error: () => {
                this.loading = false;
                this.snackBar.open('Unable to load validated hostnames', 'Dismiss', { duration: 3000 });
            }
        });
    }

    openHistory(hostname: string) {
        this.selectedHostname = hostname;
        this.service.getValidationHistory(hostname).subscribe({
            next: (resp) => {
                this.history = resp.history || [];
                this.dialog.open(this.historyDialog, { width: '700px' });
            },
            error: () => this.snackBar.open('Failed to load history', 'Dismiss', { duration: 3000 })
        });
    }

    undoValidation(hostname: string, date: string) {
        if (!confirm(`Are you sure you want to undo validation for ${hostname}?`)) {
            return;
        }

        this.loading = true;
        this.service.undoValidation(hostname, date).subscribe({
            next: () => {
                this.snackBar.open(`Validation undone for ${hostname}`, 'Dismiss', { duration: 3000 });
                this.loadValidated();
            },
            error: (err) => {
                this.loading = false;
                this.snackBar.open('Failed to undo validation', 'Dismiss', { duration: 3000 });
                console.error(err);
            }
        });
    }
}
