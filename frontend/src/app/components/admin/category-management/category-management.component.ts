import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogueService, CatalogueCategory } from '../../../services/catalogue.service';
import { CategoryFormComponent } from '../category-form/category-form.component';

@Component({
  selector: 'app-category-management',
  templateUrl: './category-management.component.html',
  styleUrls: ['./category-management.component.scss']
})
export class CategoryManagementComponent implements OnInit {
  categories: CatalogueCategory[] = [];
  displayedColumns: string[] = ['name', 'icon', 'order', 'state', 'reorder', 'actions'];
  isLoading = false;

  constructor(
    private catalogueService: CatalogueService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
    this.loadCategories();
  }

  loadCategories() {
    this.isLoading = true;
    this.catalogueService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading categories:', error);
        this.isLoading = false;
        this.snackBar.open('Error loading categories', 'Close', { duration: 3000 });
      }
    });
  }

  openCreateDialog() {
    const dialogRef = this.dialog.open(CategoryFormComponent, {
      width: '500px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
      }
    });
  }

  openEditDialog(category: CatalogueCategory) {
    const dialogRef = this.dialog.open(CategoryFormComponent, {
      width: '500px',
      data: { mode: 'edit', category }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        // Notify that categories have been updated to refresh header dropdown
        this.catalogueService.refreshCategories();
      }
    });
  }

  deleteCategory(category: CatalogueCategory) {
    if (confirm(`Are you sure you want to delete ${category.name}?`)) {
      // Store current scroll position to prevent page jump
      const scrollContainer = document.querySelector('.mat-mdc-tab-body-content') as HTMLElement;
      const scrollTop = scrollContainer ? scrollContainer.scrollTop : 0;
      const windowScrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
      
      this.catalogueService.deleteCategory(category.id).subscribe({
        next: () => {
          this.snackBar.open('Category deleted', 'Close', { duration: 3000 });
          this.loadCategories();
          // Refresh header dropdown to remove deleted category
          this.catalogueService.refreshCategories();
          // Prevent page scroll - restore positions immediately and after DOM update
          requestAnimationFrame(() => {
            if (scrollContainer) {
              scrollContainer.scrollTop = scrollTop;
            }
            window.scrollTo(0, windowScrollTop);
            // Double-check after a brief delay
            setTimeout(() => {
              if (scrollContainer) {
                scrollContainer.scrollTop = scrollTop;
              }
              window.scrollTo(0, windowScrollTop);
            }, 10);
          });
        },
        error: (error) => {
          console.error('Error deleting category:', error);
          const errorMessage = error?.error?.detail || error?.message || 'Error deleting category';
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
        }
      });
    }
  }

  toggleActive(category: CatalogueCategory) {
    const updatedStatus = !category.is_active;
    // Optimistic update
    category.is_active = updatedStatus;

    this.catalogueService.updateCategory(category.id, { is_active: updatedStatus }).subscribe({
      next: () => {
        this.snackBar.open(`Category ${updatedStatus ? 'activated' : 'deactivated'}`, 'Close', { duration: 3000 });
        // Notify that categories have been updated to refresh header dropdown
        this.catalogueService.refreshCategories();
      },
      error: (error) => {
        // Revert on error
        category.is_active = !updatedStatus;
        this.snackBar.open('Error updating category state', 'Close', { duration: 3000 });
        console.error('Error updating category:', error);
      }
    });
  }

  moveUp(category: CatalogueCategory) {
    const currentIndex = this.categories.findIndex(c => c.id === category.id);
    if (currentIndex > 0) {
      const previousCategory = this.categories[currentIndex - 1];
      const newOrder = previousCategory.display_order;
      const previousOrder = category.display_order;
      
      // Swap orders
      this.catalogueService.reorderCategory(category.id, newOrder).subscribe({
        next: () => {
          this.catalogueService.reorderCategory(previousCategory.id, previousOrder).subscribe({
            next: () => {
              this.loadCategories();
            },
            error: (error) => {
              console.error('Error reordering category:', error);
              this.snackBar.open('Error reordering category', 'Close', { duration: 3000 });
            }
          });
        },
        error: (error) => {
          console.error('Error reordering category:', error);
          this.snackBar.open('Error reordering category', 'Close', { duration: 3000 });
        }
      });
    }
  }

  moveDown(category: CatalogueCategory) {
    const currentIndex = this.categories.findIndex(c => c.id === category.id);
    if (currentIndex < this.categories.length - 1) {
      const nextCategory = this.categories[currentIndex + 1];
      const newOrder = nextCategory.display_order;
      const previousOrder = category.display_order;
      
      // Swap orders
      this.catalogueService.reorderCategory(category.id, newOrder).subscribe({
        next: () => {
          this.catalogueService.reorderCategory(nextCategory.id, previousOrder).subscribe({
            next: () => {
              this.loadCategories();
            },
            error: (error) => {
              console.error('Error reordering category:', error);
              this.snackBar.open('Error reordering category', 'Close', { duration: 3000 });
            }
          });
        },
        error: (error) => {
          console.error('Error reordering category:', error);
          this.snackBar.open('Error reordering category', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
