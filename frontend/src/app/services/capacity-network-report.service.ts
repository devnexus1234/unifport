import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export interface ZoneSummary {
  zone_name: string;
  total_device_count: number;
  cpu_normal: number;
  cpu_warning: number;
  cpu_critical: number;
  memory_normal: number;
  memory_warning: number;
  memory_critical: number;
}

export interface DeviceDetail {
  device_name: string;
  cpu_peak_percent: number;
  cpu_peak_count: number;
  cpu_peak_duration_min: number;
  memory_peak_percent: number;
  memory_peak_count: number;
  memory_peak_duration_min: number;
}

export interface DashboardResponse {
  region: string;
  production_hours: boolean;
  zone_summary: ZoneSummary[];
  device_details?: DeviceDetail[];
}

@Injectable({
  providedIn: 'root'
})
export class CapacityNetworkReportService {
  private baseUrl = `${environment.apiUrl}/capacity-network-report`;

  constructor(private http: HttpClient) {}

  upload(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }

  downloadDevices(): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/export`, { responseType: 'blob' });
  }

  downloadSummary(): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/export-summary`, { responseType: 'blob' });
  }

  getDashboard(region: string, productionHours: boolean, zoneName?: string): Observable<DashboardResponse> {
    let params = new HttpParams()
      .set('region', region)
      .set('production_hours', productionHours.toString());
    
    if (zoneName) {
      params = params.set('zone_name', zoneName);
    }
    
    return this.http.get<DashboardResponse>(`${this.baseUrl}/dashboard`, { params });
  }

  getZones(): Observable<{ zones: { zone_name: string; region_name: string }[] }> {
    return this.http.get<{ zones: { zone_name: string; region_name: string }[] }>(`${this.baseUrl}/zones`);
  }

  getDevices(): Observable<{ devices: string[] }> {
    return this.http.get<{ devices: string[] }>(`${this.baseUrl}/devices`);
  }

  getRegions(): Observable<{ regions: string[] }> {
    return this.http.get<{ regions: string[] }>(`${this.baseUrl}/regions`);
  }

  getZoneDeviceMappings(): Observable<{ mappings: { zone_name: string; device_name: string }[] }> {
    return this.http.get<{ mappings: { zone_name: string; device_name: string }[] }>(`${this.baseUrl}/zone-device-mappings`);
  }

  addDeviceToZone(zoneName: string, deviceName: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/device-zone-mapping/add`, {
      zone_name: zoneName,
      device_name: deviceName
    });
  }

  updateDeviceZoneMapping(oldZoneName: string, oldDeviceName: string, newZoneName?: string, newDeviceName?: string): Observable<any> {
    let params = new HttpParams()
      .set('old_zone_name', oldZoneName)
      .set('old_device_name', oldDeviceName);
    
    if (newZoneName) {
      params = params.set('new_zone_name', newZoneName);
    }
    if (newDeviceName) {
      params = params.set('new_device_name', newDeviceName);
    }
    
    return this.http.put(`${this.baseUrl}/device-zone-mapping/update`, null, { params });
  }

  deleteDeviceZoneMapping(zoneName: string, deviceName: string): Observable<any> {
    const params = new HttpParams()
      .set('zone_name', zoneName)
      .set('device_name', deviceName);
    
    return this.http.delete(`${this.baseUrl}/device-zone-mapping/delete`, { params });
  }

  manageZone(regionName: string, zoneName: string, action: string, newZoneName?: string): Observable<any> {
    const body: any = {
      region_name: regionName,
      zone_name: zoneName
    };
    
    if (newZoneName) {
      body.new_zone_name = newZoneName;
    }
    
    // Route to appropriate endpoint based on action
    if (action === 'ADD ZONE' || action === 'ADD') {
      return this.http.post(`${this.baseUrl}/zone-region-mapping/add`, body);
    } else if (action === 'EDIT ZONE' || action === 'EDIT') {
      return this.http.put(`${this.baseUrl}/zone-region-mapping/update`, body);
    } else if (action === 'DELETE ZONE' || action === 'DELETE') {
      const params = new HttpParams().set('zone_name', zoneName);
      return this.http.delete(`${this.baseUrl}/zone-region-mapping/delete`, { params });
    } else {
      throw new Error(`Invalid action: ${action}`);
    }
  }
}
