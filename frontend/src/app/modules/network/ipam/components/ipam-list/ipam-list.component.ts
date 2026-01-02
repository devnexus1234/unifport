import { Component, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { IpamService, IpamSegment } from '../../services/ipam.service';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { IpamAuditLogDialogComponent } from '../ipam-audit-log-dialog/ipam-audit-log-dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
    selector: 'app-ipam-list',
    templateUrl: './ipam-list.component.html',
    styleUrls: ['./ipam-list.component.scss']
})
export class IpamListComponent implements OnInit, OnDestroy {
    displayedColumns: string[] = [
        'sr_no', 'id', 'entity', 'environment',
        'segment', 'status', 'location', 'network_zone'
    ];
    dataSource: MatTableDataSource<IpamSegment>;
    isSyncing = false;
    private pollInterval: any;

    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;

    constructor(
        private ipamService: IpamService,
        private router: Router,
        public dialog: MatDialog,
        private snackBar: MatSnackBar
    ) {
        this.dataSource = new MatTableDataSource<IpamSegment>([]);
    }

    entities: string[] = [];
    environments: string[] = [];
    locations: string[] = [];

    @ViewChild('input') input: any;

    filterValues: any = {
        global: '',
        entity: '',
        environment: '',
        location: ''
    };

    ngOnInit(): void {
        this.loadSegments();
        this.dataSource.filterPredicate = this.createFilter();
        this.checkSyncStatus(); // Check if sync is running on load
    }

    ngOnDestroy(): void {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
    }

    resetFilters() {
        this.filterValues = {
            global: '',
            entity: '',
            environment: '',
            location: ''
        };
        this.dataSource.filter = JSON.stringify(this.filterValues);
        if (this.input) {
            this.input.nativeElement.value = '';
        }
    }

    loadSegments() {
        this.ipamService.getSegments().subscribe({
            next: (data) => {
                this.dataSource.data = data;
                this.dataSource.paginator = this.paginator;
                this.dataSource.sort = this.sort;

                // Extract unique values for filters
                this.entities = [...new Set(data.map(item => item.entity).filter(Boolean))].sort();
                this.environments = [...new Set(data.map(item => item.environment).filter(Boolean))].sort();
                this.locations = [...new Set(data.map(item => item.location).filter(Boolean))].sort();
            },
            error: (err) => console.error('Error fetching segments', err)
        });
    }

    createFilter(): (data: IpamSegment, filter: string) => boolean {
        return (data: IpamSegment, filter: string): boolean => {
            const searchTerms = JSON.parse(filter);

            const matchGlobal = !searchTerms.global ||
                Object.values(data).some(val =>
                    String(val).toLowerCase().includes(searchTerms.global.toLowerCase())
                );

            const matchEntity = !searchTerms.entity || data.entity === searchTerms.entity;
            const matchEnvironment = !searchTerms.environment || data.environment === searchTerms.environment;
            const matchLocation = !searchTerms.location || data.location === searchTerms.location;

            return matchGlobal && matchEntity && matchEnvironment && matchLocation;
        };
    }

    applyFilter(event: any, type: string) {
        let value = '';
        if (type === 'global') {
            value = (event.target as HTMLInputElement).value;
        } else {
            // For selects, the event value is passed directly if we handle it there, 
            // but here we are using (selectionChange) which passes a MatSelectChange object 
            // OR (input) for text.
            // We'll simplify: The HTML will call this with the raw value for selects.
            value = (event as any).value || (event.target as HTMLInputElement)?.value || '';
        }

        this.filterValues[type] = value.trim();
        this.dataSource.filter = JSON.stringify(this.filterValues);

        if (this.dataSource.paginator) {
            this.dataSource.paginator.firstPage();
        }
    }

    viewSegment(segment: IpamSegment) {
        this.router.navigate(['/catalogues/network/ipam/segment', segment.id]);
    }

    openAuditLogs() {
        this.dialog.open(IpamAuditLogDialogComponent, {
            width: '1000px',
            data: {} // No filters = global logs
        });
    }

    onSync(): void {
        this.isSyncing = true;
        this.ipamService.syncSegments().subscribe({
            next: (response) => {
                this.snackBar.open('Sync started in background...', 'Close', { duration: 3000 });
                this.startPolling();
            },
            error: (err) => {
                console.error('Trigger sync failed', err);
                if (err.status === 409) {
                    this.snackBar.open('Sync is already in progress', 'Close', { duration: 3000 });
                    this.startPolling(); // Ensure we are tracking it
                } else {
                    this.snackBar.open('Sync failed to start: ' + (err.error?.detail || err.message), 'Close', { duration: 5000 });
                    this.isSyncing = false;
                }
            }
        });
    }

    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(() => {
            this.checkSyncStatus();
        }, 2000);
    }

    checkSyncStatus() {
        this.ipamService.getSyncStatus().subscribe({
            next: (status) => {
                this.isSyncing = status.is_running;

                if (!status.is_running) {
                    if (this.pollInterval) {
                        clearInterval(this.pollInterval);
                        this.pollInterval = null;

                        // If we were polling (implied by pollInterval exists or just finished), check result
                        if (status.status === 'COMPLETED') {
                            this.snackBar.open(`Sync Completed! Synced: ${status.result?.synced || 0}, Errors: ${status.result?.errors || 0}`, 'Close', { duration: 5000 });
                            this.loadSegments();
                        } else if (status.status === 'FAILED') {
                            this.snackBar.open(`Sync Failed: ${status.error}`, 'Close', { duration: 5000 });
                        }
                    }
                } else {
                    // Make sure UI reflects running state if we just loaded page
                    this.isSyncing = true;
                }
            },
            error: (err) => console.error('Error checking sync status', err)
        });
    }
}
