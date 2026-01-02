import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthService } from './services/auth.service';
import { MenuService, MenuItem, CatalogueItem } from './services/menu.service';
import { CatalogueService, CatalogueCategory } from './services/catalogue.service';
import { ThemeService } from './services/theme.service';
import { ConfigService } from './services/config.service';
import { environment } from '../environments/environment';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = environment.appName;
  menuItems: MenuItem[] = [];
  categories: CatalogueCategory[] = [];
  selectedCategory: MenuItem | null = null;
  isAuthenticated = false;
  currentUser: any = null;
  currentTheme: string = 'light';
  enableThemeToggle = environment.theme.enableThemeToggle;
  isDebugMode = false;

  constructor(
    private authService: AuthService,
    private menuService: MenuService,
    private catalogueService: CatalogueService,
    private themeService: ThemeService,
    private configService: ConfigService,
    public router: Router
  ) { }

  ngOnInit() {
    // Initialize theme
    this.themeService.theme$.subscribe(theme => {
      this.currentTheme = theme === 'auto'
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : theme;
    });

    // Check debug mode from environment first
    this.isDebugMode = environment.enableDebug;

    // Try to get debug mode from backend if authenticated
    this.authService.isAuthenticated$.subscribe(isAuth => {
      this.isAuthenticated = isAuth;
      if (isAuth) {
        this.currentUser = this.authService.getCurrentUser();
        this.loadMenu();
        this.checkDebugMode();

        // Set dashboard as active on initial load only if no category is selected
        setTimeout(() => {
          const currentCategory = this.menuService.getSelectedCategory();
          if ((this.router.url === '/dashboard' || this.router.url === '/') && !currentCategory) {
            this.selectDashboard();
          }
        }, 100);
      }
    });

    // Check current route to set dashboard as active
    // Only auto-select dashboard if no category is currently selected
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      // Only auto-select dashboard if no category is selected
      // This prevents clearing category selection when navigating to dashboard
      const currentCategory = this.menuService.getSelectedCategory();
      if ((this.router.url === '/dashboard' || this.router.url === '/') && !currentCategory) {
        this.selectDashboard();
      }
    });

    // Subscribe to selected category changes
    this.menuService.selectedCategory$.subscribe(category => {
      this.selectedCategory = category;
    });

    // Subscribe to category updates to refresh header dropdown and menu
    this.catalogueService.categoriesRefresh$.subscribe(() => {
      this.loadCategories();
      // Also refresh menu to get updated catalogues
      this.menuService.refreshMenu();
    });

    // Subscribe to menu refresh to reload menu items
    this.menuService.menuRefresh$.subscribe(() => {
      this.loadMenu();
      // If a category is currently selected, refresh its catalogues
      const currentCategory = this.menuService.getSelectedCategory();
      if (currentCategory) {
        this.refreshSelectedCategoryCatalogues(currentCategory);
      }
    });
  }

  refreshSelectedCategoryCatalogues(menuItem: MenuItem) {
    // Find the category ID from the menu item and refresh its catalogues
    const category = this.categories.find(cat => cat.id === menuItem.id || cat.name === menuItem.name);
    if (category) {
      this.catalogueService.getCatalogues(category.id).subscribe({
        next: (catalogues) => {
          const catalogueItems: CatalogueItem[] = catalogues.map(cat => ({
            id: cat.id,
            name: cat.name,
            description: cat.description,
            route: cat.frontend_route,
            icon: cat.icon,
            api_endpoint: cat.api_endpoint
          }));

          const updatedMenuItem: MenuItem = {
            ...menuItem,
            catalogues: catalogueItems
          };
          this.menuService.selectCategory(updatedMenuItem);
        },
        error: (error) => {
          console.error('Error refreshing catalogues:', error);
        }
      });
    }
  }

  loadCategories() {
    // Load active categories for header dropdown
    this.catalogueService.getActiveCategories().subscribe({
      next: (categories) => {
        this.categories = categories || [];
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadMenu() {
    this.menuService.getMenu().subscribe({
      next: (response) => {
        this.menuItems = response.menu || [];
        // Only auto-select dashboard if no category is currently selected
        // This prevents clearing category selection when menu reloads
        const currentCategory = this.menuService.getSelectedCategory();
        if ((this.router.url === '/dashboard' || this.router.url === '/') && !currentCategory) {
          this.selectDashboard();
        }
      },
      error: (error) => {
        console.error('Error loading menu:', error);
      }
    });

    // Load active categories for header dropdown
    this.loadCategories();
  }

  selectCategory(category: MenuItem) {
    this.menuService.selectCategory(category);
    // Navigate to dashboard if not already there
    if (this.router.url !== '/dashboard') {
      this.router.navigate(['/dashboard']);
    }
  }

  selectCategoryFromDropdown(category: CatalogueCategory) {
    // Fetch catalogues for this category
    this.catalogueService.getCatalogues(category.id).subscribe({
      next: (catalogues) => {
        // Convert catalogues to CatalogueItem format
        const catalogueItems: CatalogueItem[] = catalogues.map(cat => ({
          id: cat.id,
          name: cat.name,
          description: cat.description,
          route: cat.frontend_route,
          icon: cat.icon,
          api_endpoint: cat.api_endpoint
        }));

        // Create a menu item from the category with its catalogues
        const menuItem: MenuItem = {
          id: category.id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          catalogues: catalogueItems
        };

        this.selectCategory(menuItem);
      },
      error: (error) => {
        console.error('Error loading catalogues for category:', error);
        // Still select the category even if catalogues fail to load
        const menuItem: MenuItem = {
          id: category.id,
          name: category.name,
          description: category.description,
          icon: category.icon,
          catalogues: []
        };
        this.selectCategory(menuItem);
      }
    });
  }

  selectDashboard() {
    // Clear category selection to show dashboard summary
    this.menuService.selectCategory(null);
  }

  toggleTheme() {
    this.themeService.toggleTheme();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  checkDebugMode() {
    // Try to get debug mode from backend
    this.configService.loadEnvironmentConfig().subscribe({
      next: (config) => {
        if (config && config.debug !== undefined) {
          this.isDebugMode = config.debug;
        }
      },
      error: () => {
        // If backend call fails, keep the value from environment
        // This is already set in ngOnInit
      }
    });
  }

  isUserAdmin(): boolean {
    return this.authService.isAdmin();
  }
}

