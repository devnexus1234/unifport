import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../../environments/environment';

export interface IpamSegment {
    id: number;
    segment: string;
    name: string;
    description: string;
    location: string;
    entity: string;
    environment: string;
    network_zone: string;
    segment_description: string;
    total_ips: number;
    assigned_ips: number;
    unassigned_ips: number;
}

export interface IpamIp {
    ip_address: string;
    status: 'Assigned' | 'Unassigned' | 'Reserved';
    segment_id: number;
    segment_name: string;
    segment?: string;
    location: string;
    entity: string;
    environment: string;
    ritm?: string;
    comment?: string;
    source?: string;
    updated_at?: string;
}

export interface IpamAllocationUpdate {
    status: string;
    ritm?: string;
    comment?: string;
    source?: string;
}

@Injectable({
    providedIn: 'root'
})
export class IpamService {
    private apiUrl = `${environment.apiUrl}/network/ipam`;

    constructor(private http: HttpClient) { }

    getSegments(): Observable<IpamSegment[]> {
        return this.http.get<IpamSegment[]>(`${this.apiUrl}/segments`);
    }

    getSegmentIps(segmentId: number): Observable<IpamIp[]> {
        return this.http.get<IpamIp[]>(`${this.apiUrl}/segments/${segmentId}/ips`);
    }

    updateAllocation(segmentId: number, ipAddress: string, data: IpamAllocationUpdate): Observable<IpamIp> {
        return this.http.put<IpamIp>(`${this.apiUrl}/segments/${segmentId}/ips/${ipAddress}`, data);
    }

    syncSegments(): Observable<any> {
        return this.http.post(`${this.apiUrl}/segments/sync`, {});
    }

    getSyncStatus(): Observable<any> {
        return this.http.get(`${this.apiUrl}/segments/sync/status`);
    }

    getAuditLogs(segmentId?: number, ipAddress?: string): Observable<IpamAuditLog[]> {
        let params: any = {};
        if (segmentId) params['segment_id'] = segmentId;
        if (ipAddress) params['ip_address'] = ipAddress;
        return this.http.get<IpamAuditLog[]>(`${this.apiUrl}/audit-logs`, { params });
    }
}

export interface IpamAuditLog {
    id: number;
    user_id: number;
    username: string;
    segment_id?: number;
    ip_address?: string;
    action: string;
    changes?: string;
    created_at: string;
}
