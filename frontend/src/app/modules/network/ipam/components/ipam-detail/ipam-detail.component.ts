import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { IpamService, IpamIp, IpamAllocationUpdate } from '../../services/ipam.service';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import { IpamAssignmentDialogComponent } from '../ipam-assignment-dialog/ipam-assignment-dialog.component';
import { IpamAuditLogDialogComponent } from '../ipam-audit-log-dialog/ipam-audit-log-dialog.component';

@Component({
    selector: 'app-ipam-detail',
    templateUrl: './ipam-detail.component.html',
    styleUrls: ['./ipam-detail.component.scss']
})
export class IpamDetailComponent implements OnInit {
    segmentId!: number;
    displayedColumns: string[] = [
        'sr_no', 'segment_name', 'segment', 'status', 'source', 'ip_address',
        'entity', 'location', 'environment', 'segment_description', 'comments', 'actions'
    ];
    dataSource: MatTableDataSource<IpamIp>;

    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;

    constructor(
        private route: ActivatedRoute,
        private ipamService: IpamService,
        private dialog: MatDialog
    ) {
        this.dataSource = new MatTableDataSource<IpamIp>([]);
    }

    statuses: string[] = ['Assigned', 'Unassigned', 'Reserved'];
    entities: string[] = [];
    locations: string[] = [];
    environments: string[] = [];

    @ViewChild('input') input: any;

    filterValues: any = {
        global: '',
        status: '',
        entity: '',
        location: '',
        environment: ''
    };

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            this.segmentId = +params['id'];
            this.loadIps();
        });
        this.dataSource.filterPredicate = this.createFilter();
    }

    resetFilters() {
        this.filterValues = {
            global: '',
            status: '',
            entity: '',
            location: '',
            environment: ''
        };
        this.dataSource.filter = JSON.stringify(this.filterValues);
        if (this.input) {
            this.input.nativeElement.value = '';
        }
    }

    loadIps() {
        this.ipamService.getSegmentIps(this.segmentId).subscribe({
            next: (data) => {
                this.dataSource.data = data;
                this.dataSource.paginator = this.paginator;
                this.dataSource.sort = this.sort;

                // Extract unique values for filters
                this.entities = [...new Set(data.map(item => item.entity).filter(Boolean))].sort();
                this.locations = [...new Set(data.map(item => item.location).filter(Boolean))].sort();
                this.environments = [...new Set(data.map(item => item.environment).filter(Boolean))].sort();
            },
            error: (err) => console.error('Error fetching IPs', err)
        });
    }

    createFilter(): (data: IpamIp, filter: string) => boolean {
        return (data: IpamIp, filter: string): boolean => {
            const searchTerms = JSON.parse(filter);

            const matchGlobal = !searchTerms.global ||
                Object.values(data).some(val =>
                    String(val).toLowerCase().includes(searchTerms.global.toLowerCase())
                );

            const matchStatus = !searchTerms.status || data.status === searchTerms.status;
            const matchEntity = !searchTerms.entity || data.entity === searchTerms.entity;
            const matchLocation = !searchTerms.location || data.location === searchTerms.location;
            const matchEnvironment = !searchTerms.environment || data.environment === searchTerms.environment;

            return matchGlobal && matchStatus && matchEntity && matchLocation && matchEnvironment;
        };
    }

    applyFilter(event: any, type: string) {
        let value = '';
        if (type === 'global') {
            value = (event.target as HTMLInputElement).value;
        } else {
            value = (event as any).value || (event.target as HTMLInputElement)?.value || '';
        }

        this.filterValues[type] = value.trim();
        this.dataSource.filter = JSON.stringify(this.filterValues);

        if (this.dataSource.paginator) {
            this.dataSource.paginator.firstPage();
        }
    }

    openAssignmentDialog(ip: IpamIp) {
        const dialogRef = this.dialog.open(IpamAssignmentDialogComponent, {
            width: '400px',
            data: {
                ipAddress: ip.ip_address,
                status: ip.status,
                ritm: ip.ritm,
                comment: ip.comment,
                source: ip.source
            }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                this.updateIp(ip.ip_address, result);
            }
        });
    }

    updateIp(ipAddress: string, data: IpamAllocationUpdate) {
        this.ipamService.updateAllocation(this.segmentId, ipAddress, data).subscribe({
            next: (updatedIp) => {
                // Update local data
                const index = this.dataSource.data.findIndex(x => x.ip_address === ipAddress);
                if (index !== -1) {
                    const newData = [...this.dataSource.data];
                    // newData[index] = { ...newData[index], ...updatedIp }; // Merge basic info + updated
                    // API returns full object
                    newData[index] = updatedIp;
                    this.dataSource.data = newData;
                }
            },
            error: (err) => console.error('Error updating IP', err)
        });
    }

    openAuditLogs() {
        this.dialog.open(IpamAuditLogDialogComponent, {
            width: '1000px',
            data: { segmentId: this.segmentId }
        });
    }
}
