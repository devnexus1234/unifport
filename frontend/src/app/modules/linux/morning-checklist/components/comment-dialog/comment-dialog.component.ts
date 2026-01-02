import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface CommentDialogData {
    title?: string;
    message?: string;
    required?: boolean;
    comment?: string;
}

@Component({
    selector: 'app-comment-dialog',
    templateUrl: './comment-dialog.component.html',
    styles: [`
    .full-width {
      width: 100%;
    }
  `]
})
export class CommentDialogComponent {
    comment: string = '';

    constructor(
        public dialogRef: MatDialogRef<CommentDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: CommentDialogData
    ) {
        if (data.comment) {
            this.comment = data.comment;
        }
    }
}
