import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export interface DialogData {
    ipAddress: string;
    status: string;
    ritm: string;
    comment: string;
    source: string;
}

@Component({
    selector: 'app-ipam-assignment-dialog',
    templateUrl: './ipam-assignment-dialog.component.html',
    styleUrls: ['./ipam-assignment-dialog.component.scss']
})
export class IpamAssignmentDialogComponent {
    form: FormGroup;
    statuses = ['Assigned', 'Unassigned', 'Reserved'];

    constructor(
        public dialogRef: MatDialogRef<IpamAssignmentDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: DialogData,
        private fb: FormBuilder
    ) {
        this.form = this.fb.group({
            status: [data.status || 'Unassigned'],
            ritm: [data.ritm || '', [Validators.required, Validators.pattern(/^RITM\d{7}$/)]],
            comment: [data.comment || '', Validators.required],
            source: [data.source || '', Validators.required]
        });
    }

    onNoClick(): void {
        this.dialogRef.close();
    }

    save(): void {
        if (this.form.valid) {
            this.dialogRef.close(this.form.value);
        }
    }
}
