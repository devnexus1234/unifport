import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../../../environments/environment';

interface BackupSummary {
  total_devices: number;
  success_count: number;
  failed_count: number;
}

interface FirewallBackup {
  id: number;
  task_date: string;
  task_name: string;
  host_count: number;
  failed_count: number;
  failed_hosts: string;
  successful_hosts: string;
}

import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-firewall-backup-report',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './firewall-backup-report.component.html',
  styleUrls: ['./firewall-backup-report.component.scss']
})
export class FirewallBackupReportComponent implements OnInit {
  summary: BackupSummary = { total_devices: 0, success_count: 0, failed_count: 0 };
  reports: FirewallBackup[] = [];
  isLoading = false;
  error = '';

  selectedDate: string = new Date().toISOString().split('T')[0];
  
  // Task Report Form
  taskBackupType: string = '';
  taskDeviceType: string = '';
  
  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.loadData();
  }

  onDateChange(): void {
    this.loadData();
  }

  clearDateFilter(): void {
    this.selectedDate = '';
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Fetch Summary
    this.http.get<BackupSummary>(`${environment.apiUrl}/firewall/backup-report/summary`).subscribe({
      next: (data) => {
        this.summary = data;
      },
      error: (err) => console.error('Error fetching summary:', err)
    });

    // Fetch Reports
    let params = {};
    if (this.selectedDate) {
      params = { task_date: this.selectedDate };
    }

    this.http.get<FirewallBackup[]>(`${environment.apiUrl}/firewall/backup-report/reports`, { params }).subscribe({
      next: (data) => {
        this.reports = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load backup reports';
        this.isLoading = false;
        console.error(err);
      }
    });
  }
  submitTaskReport(): void {
    if (this.taskBackupType && this.taskDeviceType) {
      this.router.navigate(['/catalogues/firewall/task-report'], {
        queryParams: {
          backupType: this.taskBackupType,
          deviceType: this.taskDeviceType
        }
      });
    }
  }
}
