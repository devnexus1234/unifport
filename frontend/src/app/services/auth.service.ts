import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
  is_active: boolean;
  roles?: string[];
  ldap_groups?: string[];
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  private refreshTokenSubject = new BehaviorSubject<string | null>(null);

  public currentUser$ = this.currentUserSubject.asObservable();
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
          this.refreshTokenSubject.next(response.refresh_token);
        }
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('token_expires_in', String(response.expires_in || 1800));
        this.currentUserSubject.next(response.user);
        this.isAuthenticatedSubject.next(true);
      })
    );
  }

  refreshAccessToken(): Observable<LoginResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
          this.refreshTokenSubject.next(response.refresh_token);
        }
        localStorage.setItem('token_expires_in', String(response.expires_in || 1800));
        if (response.user) {
          localStorage.setItem('user', JSON.stringify(response.user));
          this.currentUserSubject.next(response.user);
        }
      })
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_expires_in');
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    this.refreshTokenSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.isAuthenticatedSubject.value;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    
    // Check is_admin flag or Admin role
    if (user.is_admin) return true;
    if (user.roles && user.roles.includes("Admin")) return true;
    
    return false;
  }

  private loadUserFromStorage() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
        this.isAuthenticatedSubject.next(true);
        if (refreshToken) {
          this.refreshTokenSubject.next(refreshToken);
        }
      } catch (e) {
        this.logout();
      }
    }
  }

  getRefreshToken(): string | null {
    return this.refreshTokenSubject.value || localStorage.getItem('refresh_token');
  }

  getCurrentUserInfo(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/auth/me`);
  }
}

