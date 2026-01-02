import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CatalogueService, Catalogue } from '../../services/catalogue.service';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-catalogue-welcome',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './catalogue-welcome.component.html',
  styleUrl: './catalogue-welcome.component.scss'
})
export class CatalogueWelcomeComponent implements OnInit {
  catalogue: Catalogue | null = null;
  isLoading = false;
  error: string | null = null;
  routeParam: string = '';
  isRedirecting = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private catalogueService: CatalogueService
  ) {}

  ngOnInit() {
    // Check route parameter synchronously first to redirect immediately
    const routeParam = this.route.snapshot.paramMap.get('route') || '';
    this.routeParam = routeParam;
    
    // Normalize route parameter (lowercase, trim)
    const normalizedRoute = routeParam.toLowerCase().trim();
    
    // Check if this is a special catalogue that has its own component
    // Redirect immediately to avoid showing welcome page
    // Handle various route formats: "morning-checklist", "morning_checklist", "linux-morning-checklist", etc.
    if (normalizedRoute === 'morning-checklist' || 
        normalizedRoute === 'morning_checklist' ||
        normalizedRoute.includes('morning-checklist') ||
        normalizedRoute.includes('morning_checklist')) {
      this.isRedirecting = true;
      this.router.navigateByUrl('/catalogues/morning-checklist', { replaceUrl: true });
      return;
    }
    if (normalizedRoute === 'validated-hostnames' || 
        normalizedRoute === 'validated_hostnames' ||
        normalizedRoute.includes('validated-hostnames')) {
      this.isRedirecting = true;
      this.router.navigateByUrl('/catalogues/validated-hostnames', { replaceUrl: true });
      return;
    }
    
    // For other catalogues, load normally
    if (routeParam) {
      this.loadCatalogueByRoute(routeParam);
    }
    
    // Also subscribe to route changes
    this.route.paramMap.subscribe(params => {
      const param = params.get('route') || '';
      if (param && param !== this.routeParam) {
        this.routeParam = param;
        const normalized = param.toLowerCase().trim();
        // Check again in case route changed
        if (normalized === 'morning-checklist' || 
            normalized === 'morning_checklist' ||
            normalized.includes('morning-checklist') ||
            normalized.includes('morning_checklist')) {
          this.isRedirecting = true;
          this.router.navigateByUrl('/catalogues/morning-checklist', { replaceUrl: true });
          return;
        }
        if (normalized === 'validated-hostnames' || 
            normalized === 'validated_hostnames' ||
            normalized.includes('validated-hostnames')) {
          this.isRedirecting = true;
          this.router.navigateByUrl('/catalogues/validated-hostnames', { replaceUrl: true });
          return;
        }
        this.loadCatalogueByRoute(param);
      }
    });
  }

  loadCatalogueByRoute(route: string) {
    this.isLoading = true;
    this.error = null;
    
    // Get accessible catalogues (public method, respects user permissions)
    // Route can be in format: "example" or "/catalogues/example"
    this.catalogueService.getCatalogues().subscribe({
      next: (catalogues) => {
        // Normalize the route parameter
        const normalizedRoute = route.startsWith('/') ? route : `/catalogues/${route}`;
        
        // Try to find catalogue by matching frontend_route
        let catalogue = catalogues.find(c => {
          if (!c.frontend_route) return false;
          // Normalize the stored route for comparison
          const storedRoute = c.frontend_route.startsWith('/catalogues/') 
            ? c.frontend_route 
            : `/catalogues/${c.frontend_route}`;
          return storedRoute === normalizedRoute || 
                 storedRoute === `/catalogues/${route}` ||
                 c.frontend_route === route ||
                 c.frontend_route === normalizedRoute;
        });
        
        if (catalogue) {
          this.catalogue = catalogue;
        } else {
          this.error = 'Catalogue not found or you do not have permission to access it';
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading catalogue:', error);
        this.error = 'Error loading catalogue';
        this.isLoading = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }
}
