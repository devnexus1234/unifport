import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../../environments/environment';

export interface ReachabilityWidget {
    total: number;
    reachable: number;
    failed: number;
    unreachable: number;
}

export interface SummaryGroup {
    application_name: string;
    asset_owner?: string | null;
    success_count: number;
    error_count: number;
}

export interface SummaryResponse {
    date: string;
    reachability: ReachabilityWidget;
    groups: SummaryGroup[];
}

export interface HostnameDetail {
    hostname: string;
    ip?: string;
    location?: string;
    application_name: string;
    asset_owner?: string;
    mc_check_date: string;
    mc_status?: string;
    mc_criticality?: string;
    updated_by?: string;
    updated_at?: string;
    is_validated?: boolean;
    success: boolean;
}

export interface CommandDiff {
    command?: string;
    current_output?: string;
    previous_output?: string;
    diff: string[];
    is_validated: boolean;
}

export interface AggregatedValidatedItem {
    hostname: string;
    ip?: string;
    application_name: string;
    asset_owner?: string;
    mc_criticality?: string;
    mc_check_date: string;
    validated_at: string;
    validate_by: string;
    validate_comment?: string;
    is_bulk: boolean;
}

export interface ValidationHistoryItem {
    hostname: string;
    application_name: string;
    asset_owner?: string;
    mc_criticality?: string;
    mc_check_date: string;
    validated_at: string;
    validate_by: string;
    validate_comment?: string;
    is_bulk: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class MorningChecklistService {
    private apiUrl = `${environment.apiUrl}/linux/morning-checklist`;

    constructor(private http: HttpClient) { }

    getDates(): Observable<string[]> {
        return this.http.get<string[]>(`${this.apiUrl}/dates`);
    }

    getSummary(date: string, filters: { application_name?: string; asset_owner?: string; show_errors_only?: boolean } = {}): Observable<SummaryResponse> {
        let params = new HttpParams().set('date', date);
        if (filters.application_name) params = params.set('application_name', filters.application_name);
        if (filters.asset_owner) params = params.set('asset_owner', filters.asset_owner);
        if (filters.show_errors_only !== undefined) params = params.set('show_errors_only', String(filters.show_errors_only));
        // Add cache buster
        params = params.set('_t', new Date().getTime().toString());
        return this.http.get<SummaryResponse>(`${this.apiUrl}/summary`, { params });
    }

    getDetails(date: string, status?: 'success' | 'error', filters: { application_name?: string; asset_owner?: string } = {}, mc_status?: string): Observable<HostnameDetail[]> {
        let params = new HttpParams().set('date', date);
        if (status) params = params.set('status', status);
        if (mc_status) params = params.set('mc_status', mc_status);
        if (filters.application_name) params = params.set('application_name', filters.application_name);
        if (filters.asset_owner) params = params.set('asset_owner', filters.asset_owner);
        return this.http.get<HostnameDetail[]>(`${this.apiUrl}/details`, { params });
    }

    getDiff(hostname: string, date: string): Observable<CommandDiff[]> {
        const params = new HttpParams().set('date', date);
        return this.http.get<CommandDiff[]>(`${this.apiUrl}/hostnames/${hostname}/diff`, { params });
    }

    getCommands(hostname: string, date: string): Observable<CommandDiff[]> {
        const params = new HttpParams().set('date', date);
        return this.http.get<CommandDiff[]>(`${this.apiUrl}/hostnames/${hostname}/commands`, { params });
    }

    validateHost(hostname: string, date: string, validated_by: string, comment?: string): Observable<any> {
        const params = new HttpParams().set('date', date);
        return this.http.post(`${this.apiUrl}/hostnames/${hostname}/validate`, { validated_by, comment }, { params });
    }

    undoValidation(hostname: string, date: string): Observable<any> {
        const params = new HttpParams().set('date', date);
        return this.http.delete(`${this.apiUrl}/hostnames/${hostname}/validate`, { params });
    }

    validateAll(date: string, application_name: string, validated_by: string, asset_owner?: string, comment?: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/validate-all`, {
            date,
            application_name,
            validated_by,
            asset_owner,
            comment
        });
    }

    validateSelected(date: string, hostnames: string[], validated_by: string, comment?: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/validate-selected`, {
            date,
            hostnames,
            validated_by,
            comment
        });
    }

    validateGroups(date: string, groups: SummaryGroup[], validated_by: string, comment?: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/validate-groups`, {
            date,
            groups,
            validated_by,
            comment
        });
    }

    getValidatedList(filters: { start_date?: string; end_date?: string; application_name?: string; asset_owner?: string; validated_by?: string; sort_by?: string } = {}): Observable<{ items: AggregatedValidatedItem[] }> {
        let params = new HttpParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value) params = params.set(key, value);
        });
        return this.http.get<{ items: AggregatedValidatedItem[] }>(`${this.apiUrl}/validated`, { params });
    }

    getValidationHistory(hostname: string): Observable<{ hostname: string; history: ValidationHistoryItem[] }> {
        return this.http.get<{ hostname: string; history: ValidationHistoryItem[] }>(`${this.apiUrl}/hostnames/${hostname}/history`);
    }

    exportSummary(date: string, filters: { application_name?: string; asset_owner?: string } = {}): Observable<Blob> {
        let params = new HttpParams().set('date', date);
        if (filters.application_name) params = params.set('application_name', filters.application_name);
        if (filters.asset_owner) params = params.set('asset_owner', filters.asset_owner);
        return this.http.get(`${this.apiUrl}/export`, { params, responseType: 'blob' });
    }

    validateChecklist(date: string, validated_by: string, validate_comment?: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/validate-checklist`, {
            date,
            // validated_by is handled by backend token now
            validate_comment
        });
    }

    undoChecklistValidation(date: string): Observable<any> {
        const params = new HttpParams().set('date', date);
        return this.http.delete(`${this.apiUrl}/validate-checklist`, { params });
    }

    getChecklistValidationStatus(date: string): Observable<{ validate_by: string; validated_at: string; validate_comment?: string } | null> {
        const params = new HttpParams().set('date', date);
        return this.http.get<{ validate_by: string; validated_at: string; validate_comment?: string } | null>(
            `${this.apiUrl}/checklist-validation-status`, { params }
        );
    }

    getApplicationOwnerMapping(): Observable<Record<string, string[]>> {
        return this.http.get<Record<string, string[]>>(`${this.apiUrl}/filters/application-owners`);
    }
}
