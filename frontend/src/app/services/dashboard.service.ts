import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface DashboardSummary {
  users: {
    total: number;
    active: number;
    inactive: number;
  };
  catalogues: {
    total: number;
    enabled: number;
    disabled: number;
  };
  categories: {
    total: number;
    active: number;
    inactive: number;
  };
  roles: {
    total: number;
    active: number;
    inactive: number;
    assignments: number;
  };
  timestamp: string;
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  response_time_ms?: number;
  error?: string;
  host?: string;
  port?: number;
  service?: string;
  cpu?: {
    usage_percent: number;
    cores: number;
  };
  memory?: {
    usage_percent: number;
    total_gb: number;
    available_gb: number;
  };
  platform?: string;
  platform_version?: string;
}

export interface DashboardHealth {
  overall: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    database?: ComponentHealth;
    api?: ComponentHealth;
    system?: ComponentHealth;
  };
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.apiUrl}/dashboard/summary`);
  }

  getHealth(): Observable<DashboardHealth> {
    return this.http.get<DashboardHealth>(`${this.apiUrl}/dashboard/health`);
  }
}
