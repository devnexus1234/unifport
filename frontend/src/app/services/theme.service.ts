import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';

export type Theme = 'light' | 'dark' | 'auto';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private themeSubject = new BehaviorSubject<Theme>(this.getInitialTheme());
  public theme$ = this.themeSubject.asObservable();
  private systemThemeHandler: ((e: MediaQueryListEvent) => void) | null = null;

  constructor() {
    this.applyTheme(this.themeSubject.value);
    this.watchSystemTheme();
  }

  private getInitialTheme(): Theme {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
      return savedTheme;
    }
    
    // Use environment default
    return environment.theme.defaultTheme as Theme;
  }

  getTheme(): Theme {
    return this.themeSubject.value;
  }

  setTheme(theme: Theme): void {
    this.themeSubject.next(theme);
    localStorage.setItem('theme', theme);
    this.applyTheme(theme);
    // Update system theme watcher if needed
    this.watchSystemTheme();
  }

  toggleTheme(): void {
    const current = this.themeSubject.value;
    if (current === 'light') {
      this.setTheme('dark');
    } else if (current === 'dark') {
      this.setTheme('light');
    } else {
      // If auto, toggle to opposite of system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'light' : 'dark');
    }
  }

  private applyTheme(theme: Theme): void {
    const root = document.documentElement;
    const body = document.body;
    
    // Remove both theme classes first
    root.classList.remove('dark-theme', 'light-theme');
    body.classList.remove('dark-theme', 'light-theme');
    
    if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        root.classList.add('dark-theme');
        body.classList.add('dark-theme');
      } else {
        root.classList.add('light-theme');
        body.classList.add('light-theme');
      }
    } else {
      if (theme === 'dark') {
        root.classList.add('dark-theme');
        body.classList.add('dark-theme');
      } else {
        root.classList.add('light-theme');
        body.classList.add('light-theme');
      }
    }
  }

  private watchSystemTheme(): void {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Remove existing listener if any
    if (this.systemThemeHandler) {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', this.systemThemeHandler);
      } else {
        mediaQuery.removeListener(this.systemThemeHandler);
      }
      this.systemThemeHandler = null;
    }
    
    // Add listener only if theme is 'auto'
    if (this.themeSubject.value === 'auto') {
      this.systemThemeHandler = (e: MediaQueryListEvent) => {
        if (this.themeSubject.value === 'auto') {
          this.applyTheme('auto');
        }
      };
      
      // Modern browsers support addEventListener
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', this.systemThemeHandler);
      } else {
        // Fallback for older browsers
        mediaQuery.addListener(this.systemThemeHandler);
      }
    }
  }

  isDarkMode(): boolean {
    const theme = this.themeSubject.value;
    if (theme === 'dark') return true;
    if (theme === 'light') return false;
    // Auto mode
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
}

