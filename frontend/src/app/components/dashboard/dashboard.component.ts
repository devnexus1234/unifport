import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { MenuService, MenuItem, CatalogueItem } from '../../services/menu.service';
import { DashboardService, DashboardSummary, DashboardHealth } from '../../services/dashboard.service';
import { AuthService } from '../../services/auth.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  selectedMenu: MenuItem | null = null;
  catalogues: CatalogueItem[] = [];
  isLoading = false;
  isLoadingSummary = false;
  isLoadingHealth = false;
  summary: DashboardSummary | null = null;
  health: DashboardHealth | null = null;
  showCatalogues = false;
  isAdmin = false;
  private categorySubscription?: Subscription;

  constructor(
    private menuService: MenuService,
    private dashboardService: DashboardService,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) { }

  ngOnInit() {
    this.isAdmin = this.authService.isAdmin();

    // Subscribe to query params for direct linking to categories
    this.route.queryParams.subscribe(params => {
      const categoryName = params['category'];
      if (categoryName && !this.menuService.getSelectedCategory()) {
        this.menuService.getMenu().subscribe(response => {
          const category = response.menu.find(c => c.name.toLowerCase() === categoryName.toLowerCase());
          if (category) {
            this.menuService.selectCategory(category);
          }
        });
      }
    });

    // Subscribe to category selection changes
    this.categorySubscription = this.menuService.selectedCategory$.subscribe(category => {
      if (category) {
        this.selectedMenu = category;
        this.catalogues = category.catalogues || [];
        this.showCatalogues = true;
      } else {
        // No category selected, show dashboard summary
        this.showCatalogues = false;
        this.loadDashboardData();
      }
    });

    // Load initial state
    const currentCategory = this.menuService.getSelectedCategory();
    if (currentCategory) {
      this.selectedMenu = currentCategory;
      this.catalogues = currentCategory.catalogues || [];
      this.showCatalogues = true;
    } else {
      // Show dashboard by default
      if (!this.showCatalogues) {
        this.loadDashboardData();
      }
    }
  }

  ngOnDestroy() {
    if (this.categorySubscription) {
      this.categorySubscription.unsubscribe();
    }
  }

  loadDashboardData() {
    this.loadSummary();
    this.loadHealth();
  }

  loadSummary() {
    this.isLoadingSummary = true;
    this.dashboardService.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
        this.isLoadingSummary = false;
      },
      error: (error) => {
        console.error('Error loading summary:', error);
        this.isLoadingSummary = false;
      }
    });
  }

  loadHealth() {
    this.isLoadingHealth = true;
    this.dashboardService.getHealth().subscribe({
      next: (health) => {
        this.health = health;
        this.isLoadingHealth = false;
      },
      error: (error) => {
        console.error('Error loading health:', error);
        this.isLoadingHealth = false;
      }
    });
  }

  /**
   * Extract route name from full route path
   * Converts "/catalogues/example" to "example" or returns route as-is if already just the name
   */
  getRouteName(route: string | undefined): string {
    if (!route) return '#';
    // If route starts with /catalogues/, extract the name part
    if (route.startsWith('/catalogues/')) {
      return route.replace('/catalogues/', '');
    }
    if (route.startsWith('catalogues/')) {
      return route.replace('catalogues/', '');
    }
    // If route starts with /, remove it
    if (route.startsWith('/')) {
      return route.substring(1);
    }
    return route;
  }

  /**
   * Navigate to catalogue route
   */
  navigateToCatalogue(catalogue: CatalogueItem) {
    if (!catalogue.route) return;
    const routeName = this.getRouteName(catalogue.route);
    // If routeName contains slashes, we need to split it so Angular router doesn't encode the slash
    if (routeName.includes('/')) {
      const segments = routeName.split('/');
      this.router.navigate(['/catalogues', ...segments]);
    } else {
      this.router.navigate(['/catalogues', routeName]);
    }
  }

  /**
   * Go back to dashboard summary view
   */
  goBackToDashboard() {
    this.menuService.selectCategory(null);
    this.showCatalogues = false;
    this.selectedMenu = null;
    this.catalogues = [];
    this.loadDashboardData();
  }
  /**
   * Navigate to admin pages
   */
  navigateToAdmin(page: string) {
    if (!this.isAdmin) return;
    this.router.navigate(['/admin'], { queryParams: { tab: page } });
  }
}

