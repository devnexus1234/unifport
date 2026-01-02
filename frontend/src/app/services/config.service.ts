import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface AppConfig {
  app_title: string;
  app_description: string;
  app_version: string;
  default_page_size: number;
  max_upload_size_mb: number;
  enable_theme_toggle: boolean;
  default_theme: string;
  primary_color: string;
  secondary_color: string;
  logo_url?: string;
  favicon_url?: string;
}

export interface EnvironmentConfig {
  environment: string;
  debug: boolean;
  app_name: string;
  app_version: string;
  enable_registration: boolean;
  enable_password_reset: boolean;
  enable_email_notifications: boolean;
  session_timeout_minutes: number;
  page_size: number;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private apiUrl = environment.apiUrl;
  private appConfigSubject = new BehaviorSubject<AppConfig | null>(null);
  private envConfigSubject = new BehaviorSubject<EnvironmentConfig | null>(null);

  public appConfig$ = this.appConfigSubject.asObservable();
  public envConfig$ = this.envConfigSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadAppConfig();
  }

  loadAppConfig(): void {
    this.http.get<AppConfig>(`${this.apiUrl}/config/app`).subscribe({
      next: (config) => {
        this.appConfigSubject.next(config);
        this.applyBranding(config);
      },
      error: (error) => {
        console.error('Error loading app config:', error);
        // Use defaults from environment
        this.appConfigSubject.next({
          app_title: environment.appName,
          app_description: 'Unified automation portal',
          app_version: environment.appVersion,
          default_page_size: environment.pageSize,
          max_upload_size_mb: 10,
          enable_theme_toggle: environment.theme.enableThemeToggle,
          default_theme: environment.theme.defaultTheme,
          primary_color: '#362D7E',
          secondary_color: '#ECAE0E'
        });
      }
    });
  }

  loadEnvironmentConfig(): Observable<EnvironmentConfig> {
    return this.http.get<EnvironmentConfig>(`${this.apiUrl}/config/environment`).pipe(
      tap(config => this.envConfigSubject.next(config))
    );
  }

  getAppConfig(): AppConfig | null {
    return this.appConfigSubject.value;
  }

  getEnvironmentConfig(): EnvironmentConfig | null {
    return this.envConfigSubject.value;
  }

  private applyBranding(config: AppConfig): void {
    // Apply CSS variables for colors
    if (config.primary_color) {
      document.documentElement.style.setProperty('--primary-color', config.primary_color);
      document.documentElement.style.setProperty('--accent-color', config.primary_color);
    }
    if (config.secondary_color) {
      document.documentElement.style.setProperty('--secondary-color', config.secondary_color);
      document.documentElement.style.setProperty('--accent-color', config.secondary_color);
    }
    
    // Update page title
    if (config.app_title) {
      document.title = config.app_title;
    }
    
    // Update favicon if provided
    if (config.favicon_url) {
      const link = document.querySelector("link[rel*='icon']") as HTMLLinkElement;
      if (link) {
        link.href = config.favicon_url;
      }
    }
  }
}

