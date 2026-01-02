import { Component, OnInit } from '@angular/core';
import { CatalogueService, Catalogue } from '../../../services/catalogue.service';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogueFormComponent } from '../catalogue-form/catalogue-form.component';

@Component({
  selector: 'app-catalogue-list',
  templateUrl: './catalogue-list.component.html',
  styleUrls: ['./catalogue-list.component.scss']
})
export class CatalogueListComponent implements OnInit {
  catalogues: Catalogue[] = [];
  displayedColumns: string[] = ['name', 'menu', 'enabled', 'route', 'reorder', 'actions'];
  isLoading = false;

  constructor(
    private catalogueService: CatalogueService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadCatalogues();
  }

  loadCatalogues() {
    this.isLoading = true;
    this.catalogueService.getAllCatalogues().subscribe({
      next: (catalogues) => {
        this.catalogues = catalogues;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading catalogues:', error);
        this.isLoading = false;
        this.snackBar.open('Error loading catalogues', 'Close', { duration: 3000 });
      }
    });
  }

  openCreateDialog() {
    const dialogRef = this.dialog.open(CatalogueFormComponent, {
      width: '600px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCatalogues();
      }
    });
  }

  openEditDialog(catalogue: Catalogue) {
    const dialogRef = this.dialog.open(CatalogueFormComponent, {
      width: '600px',
      data: { mode: 'edit', catalogue }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result.catalogue) {
          // Update specific catalogue in array without full refresh
          const index = this.catalogues.findIndex(c => c.id === result.catalogue.id);
          if (index !== -1) {
            this.catalogues[index] = result.catalogue;
            // Create new array reference to trigger change detection
            this.catalogues = [...this.catalogues];
          } else {
            // If not found, reload all
            this.loadCatalogues();
          }
        } else {
          // Fallback to full reload if no catalogue data returned
          this.loadCatalogues();
        }
      }
    });
  }

  toggleEnabled(catalogue: Catalogue) {
    const newEnabledState = !catalogue.is_enabled;
    this.catalogueService.updateCatalogue(catalogue.id, {
      is_enabled: newEnabledState
    }).subscribe({
      next: (updatedCatalogue) => {
        this.snackBar.open(
          `Catalogue ${newEnabledState ? 'enabled' : 'disabled'}`,
          'Close',
          { duration: 3000 }
        );
        // Update specific catalogue in array without full refresh
        const index = this.catalogues.findIndex(c => c.id === catalogue.id);
        if (index !== -1) {
          this.catalogues[index] = updatedCatalogue;
          // Create new array reference to trigger change detection
          this.catalogues = [...this.catalogues];
        }
        // Notify that catalogues have been updated to refresh menu/catalogues display
        this.catalogueService.refreshCategories();
      },
      error: (error) => {
        this.snackBar.open('Error updating catalogue', 'Close', { duration: 3000 });
      }
    });
  }

  deleteCatalogue(catalogue: Catalogue) {
    if (confirm(`Are you sure you want to delete ${catalogue.name}?`)) {
      // Store current scroll position to prevent page jump
      const scrollContainer = document.querySelector('.mat-mdc-tab-body-content') as HTMLElement;
      const scrollTop = scrollContainer ? scrollContainer.scrollTop : 0;
      const windowScrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
      
      this.catalogueService.deleteCatalogue(catalogue.id).subscribe({
        next: () => {
          this.snackBar.open('Catalogue deleted', 'Close', { duration: 3000 });
          this.loadCatalogues();
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
          console.error('Error deleting catalogue:', error);
          const errorMessage = error.error?.detail || error.message || 'Error deleting catalogue';
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
        }
      });
    }
  }

  moveUp(catalogue: Catalogue) {
    const currentIndex = this.catalogues.findIndex(c => c.id === catalogue.id);
    if (currentIndex > 0) {
      const previousCatalogue = this.catalogues[currentIndex - 1];
      const newOrder = previousCatalogue.display_order;
      const previousOrder = catalogue.display_order;
      
      // Swap orders
      this.catalogueService.reorderCatalogue(catalogue.id, newOrder).subscribe({
        next: () => {
          this.catalogueService.reorderCatalogue(previousCatalogue.id, previousOrder).subscribe({
            next: () => {
              this.loadCatalogues();
            },
            error: (error) => {
              console.error('Error reordering catalogue:', error);
              this.snackBar.open('Error reordering catalogue', 'Close', { duration: 3000 });
            }
          });
        },
        error: (error) => {
          console.error('Error reordering catalogue:', error);
          this.snackBar.open('Error reordering catalogue', 'Close', { duration: 3000 });
        }
      });
    }
  }

  moveDown(catalogue: Catalogue) {
    const currentIndex = this.catalogues.findIndex(c => c.id === catalogue.id);
    if (currentIndex < this.catalogues.length - 1) {
      const nextCatalogue = this.catalogues[currentIndex + 1];
      const newOrder = nextCatalogue.display_order;
      const previousOrder = catalogue.display_order;
      
      // Swap orders
      this.catalogueService.reorderCatalogue(catalogue.id, newOrder).subscribe({
        next: () => {
          this.catalogueService.reorderCatalogue(nextCatalogue.id, previousOrder).subscribe({
            next: () => {
              this.loadCatalogues();
            },
            error: (error) => {
              console.error('Error reordering catalogue:', error);
              this.snackBar.open('Error reordering catalogue', 'Close', { duration: 3000 });
            }
          });
        },
        error: (error) => {
          console.error('Error reordering catalogue:', error);
          this.snackBar.open('Error reordering catalogue', 'Close', { duration: 3000 });
        }
      });
    }
  }
}

