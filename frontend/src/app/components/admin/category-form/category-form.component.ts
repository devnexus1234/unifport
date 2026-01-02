import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogueService, CatalogueCategory } from '../../../services/catalogue.service';

@Component({
  selector: 'app-category-form',
  templateUrl: './category-form.component.html',
  styleUrls: ['./category-form.component.scss']
})
export class CategoryFormComponent implements OnInit {
  categoryForm: FormGroup;
  isLoading = false;
  mode: 'create' | 'edit' = 'create';

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<CategoryFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private catalogueService: CatalogueService,
    private snackBar: MatSnackBar
  ) {
    this.mode = data.mode || 'create';
    this.categoryForm = this.fb.group({
      name: ['', [Validators.required]],
      description: [''],
      icon: [''],
      display_order: [0]
    });
  }

  ngOnInit() {
    if (this.mode === 'edit' && this.data.category) {
      const category = this.data.category;
      this.categoryForm.patchValue({
        name: category.name,
        description: category.description,
        icon: category.icon,
        display_order: category.display_order
      });
    }
  }

  onSubmit() {
    if (this.categoryForm.valid) {
      this.isLoading = true;
      const formData = this.categoryForm.value;

      if (this.mode === 'create') {
        this.catalogueService.createCategory(formData).subscribe({
          next: () => {
            this.snackBar.open('Category created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open(
              error.error?.detail || 'Error creating category',
              'Close',
              { duration: 5000 }
            );
          }
        });
      } else {
        this.catalogueService.updateCategory(this.data.category.id, formData).subscribe({
          next: () => {
            this.snackBar.open('Category updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open(
              error.error?.detail || 'Error updating category',
              'Close',
              { duration: 5000 }
            );
          }
        });
      }
    }
  }

  onCancel() {
    this.dialogRef.close(false);
  }
}
