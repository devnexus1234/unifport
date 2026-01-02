import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';

import { IpamRoutingModule } from './ipam-routing.module';
import { IpamListComponent } from './components/ipam-list/ipam-list.component';
import { IpamDetailComponent } from './components/ipam-detail/ipam-detail.component';
import { IpamAssignmentDialogComponent } from './components/ipam-assignment-dialog/ipam-assignment-dialog.component';
import { IpamAuditLogDialogComponent } from './components/ipam-audit-log-dialog/ipam-audit-log-dialog.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@NgModule({
    declarations: [
        IpamListComponent,
        IpamDetailComponent,
        IpamAssignmentDialogComponent,
        IpamAuditLogDialogComponent
    ],
    imports: [
        CommonModule,
        IpamRoutingModule,
        FormsModule,
        ReactiveFormsModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
        MatInputModule,
        MatFormFieldModule,
        MatButtonModule,
        MatIconModule,
        MatDialogModule,
        MatDialogModule,
        MatSelectModule,
        MatTooltipModule,
        MatProgressSpinnerModule
    ]
})
export class IpamModule { }
