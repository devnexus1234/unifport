import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { IpamAuditLog, IpamService } from '../../services/ipam.service';

@Component({
    selector: 'app-ipam-audit-log-dialog',
    templateUrl: './ipam-audit-log-dialog.component.html',
    styleUrls: ['./ipam-audit-log-dialog.component.scss']
})
export class IpamAuditLogDialogComponent implements OnInit {
    displayedColumns: string[] = ['timestamp', 'user', 'action', 'ip', 'changes'];
    dataSource = new MatTableDataSource<IpamAuditLog>([]);
    isLoading = true;

    @ViewChild(MatPaginator) paginator!: MatPaginator;

    constructor(
        private ipamService: IpamService,
        public dialogRef: MatDialogRef<IpamAuditLogDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: { segmentId?: number, ipAddress?: string }
    ) { }

    ngOnInit(): void {
        this.loadLogs();
    }

    loadLogs() {
        this.isLoading = true;
        this.ipamService.getAuditLogs(this.data.segmentId, this.data.ipAddress).subscribe({
            next: (logs) => {
                this.dataSource.data = logs;
                this.dataSource.paginator = this.paginator;
                this.isLoading = false;
            },
            error: (err) => {
                console.error('Failed to load audit logs', err);
                this.isLoading = false;
            }
        });
    }
}
