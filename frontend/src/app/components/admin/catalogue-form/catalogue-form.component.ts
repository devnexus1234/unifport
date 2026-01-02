import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogueService, Catalogue, CatalogueCategory } from '../../../services/catalogue.service';
// RoleService import removed

@Component({
  selector: 'app-catalogue-form',
  templateUrl: './catalogue-form.component.html',
  styleUrls: ['./catalogue-form.component.scss']
})
export class CatalogueFormComponent implements OnInit {
  catalogueForm: FormGroup;
  categories: CatalogueCategory[] = [];
  // menus property removed
  isLoading = false;
  mode: 'create' | 'edit' = 'create';

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<CatalogueFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private catalogueService: CatalogueService,
    private snackBar: MatSnackBar
  ) {
    this.mode = data.mode || 'create';
    this.catalogueForm = this.fb.group({
      name: ['', [Validators.required]],
      description: [''],
      // menu_id removed
      category_id: ['', [Validators.required]],
      api_endpoint: [''],
      frontend_route: [''],
      icon: [''],
      display_order: [0],
      is_enabled: [false]
    });
  }

  ngOnInit() {
    this.loadCategories();
    // this.loadMenus(); // No longer needed

    // Auto-generate route from name when creating
    if (this.mode === 'create') {
      this.catalogueForm.get('name')?.valueChanges.subscribe(name => {
        if (name && !this.catalogueForm.get('frontend_route')?.value) {
          const generatedRoute = this.generateRouteFromName(name);
          this.catalogueForm.patchValue({ frontend_route: generatedRoute }, { emitEvent: false });
        }
      });
    }

    if (this.mode === 'edit' && this.data.catalogue) {
      const catalogue = this.data.catalogue;
      this.catalogueForm.patchValue({
        name: catalogue.name,
        description: catalogue.description,
        // menu_id: catalogue.menu_id,
        category_id: catalogue.category_id,
        api_endpoint: catalogue.api_endpoint,
        frontend_route: catalogue.frontend_route,
        icon: catalogue.icon,
        display_order: catalogue.display_order,
        is_enabled: catalogue.is_enabled
      });
    }
  }

  private generateRouteFromName(name: string): string {
    return name
      .toLowerCase()
      .trim()
      .replace(/\s+/g, '-')  // Replace spaces with hyphens
      .replace(/[^a-z0-9-]/g, '')  // Remove special characters
      .replace(/-+/g, '-')  // Replace multiple hyphens with single hyphen
      .replace(/^-|-$/g, '');  // Remove leading/trailing hyphens
  }

  loadCategories() {
    // Use getActiveCategories to fetch only active categories
    this.catalogueService.getActiveCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  // loadMenus removed

  onSubmit() {
    if (this.catalogueForm.valid) {
      this.isLoading = true;
      const formData = { ...this.catalogueForm.value };

      // Ensure frontend_route is set (auto-generate if not provided)
      if (!formData.frontend_route && formData.name) {
        formData.frontend_route = this.generateRouteFromName(formData.name);
      }

      // Ensure route starts with /catalogues/
      if (formData.frontend_route) {
        // Remove leading slash if present, then add /catalogues/ prefix
        const routeName = formData.frontend_route.startsWith('/')
          ? formData.frontend_route.substring(1)
          : formData.frontend_route;
        // Remove /catalogues prefix if already present to avoid duplication
        const cleanRoute = routeName.startsWith('catalogues/')
          ? routeName.substring('catalogues/'.length)
          : routeName;
        formData.frontend_route = `/catalogues/${cleanRoute}`;
      }

      if (this.mode === 'create') {
        this.catalogueService.createCatalogue(formData).subscribe({
          next: () => {
            this.snackBar.open('Catalogue created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open(
              error.error?.detail || 'Error creating catalogue',
              'Close',
              { duration: 5000 }
            );
          }
        });
      } else {
        this.catalogueService.updateCatalogue(this.data.catalogue.id, formData).subscribe({
          next: (updatedCatalogue) => {
            this.snackBar.open('Catalogue updated successfully', 'Close', { duration: 3000 });
            // Pass updated catalogue data back to parent
            this.dialogRef.close({ success: true, catalogue: updatedCatalogue });
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open(
              error.error?.detail || 'Error updating catalogue',
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

