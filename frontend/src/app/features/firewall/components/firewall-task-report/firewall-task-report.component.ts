import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';

import { FormsModule } from '@angular/forms';

export interface TaskReportItem {
  deviceType: string;
  backupType: string;
  backupDate: string;
  hostname: string;
  ip: string;
  status: 'Success' | 'Failed';
}

@Component({
  selector: 'app-firewall-task-report',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './firewall-task-report.component.html',
  styleUrls: ['./firewall-task-report.component.scss']
})
export class FirewallTaskReportComponent implements OnInit {
  backupType: string = '';
  deviceType: string = '';
  
  startTime: string = new Date().toISOString().split('T')[0];
  endTime: string = new Date().toISOString().split('T')[0];

  allReportItems: TaskReportItem[] = [
    // Checkpoint FW
    { deviceType: 'Checkpoint FW', backupType: 'config', backupDate: '2026-01-09 10:00:00', hostname: 'FW-BLR-01', ip: '192.168.1.1', status: 'Success' },
    { deviceType: 'Checkpoint FW', backupType: 'config', backupDate: '2026-01-08 23:00:00', hostname: 'FW-BLR-02', ip: '192.168.1.2', status: 'Failed' },
    { deviceType: 'Checkpoint FW', backupType: 'system/device', backupDate: '2026-01-09 12:00:00', hostname: 'FW-DEL-01', ip: '10.10.10.1', status: 'Success' },
    { deviceType: 'Checkpoint FW', backupType: 'traffic log', backupDate: '2026-01-09 01:30:00', hostname: 'FW-MUM-03', ip: '10.10.20.5', status: 'Success' },
    
    // Checkpoint MGMT
    { deviceType: 'Checkpoint MGMT', backupType: 'migrate export', backupDate: '2026-01-07 02:00:00', hostname: 'MGMT-MUM-01', ip: '172.16.0.5', status: 'Success' },
    { deviceType: 'Checkpoint MGMT', backupType: 'config', backupDate: '2026-01-09 03:00:00', hostname: 'MGMT-DR-01', ip: '172.16.0.6', status: 'Success' },

    // Paloalto FW
    { deviceType: 'Paloalto FW', backupType: 'system/device', backupDate: '2026-01-09 10:15:00', hostname: 'PA-MUM-02', ip: '192.168.1.20', status: 'Failed' },
    { deviceType: 'Paloalto FW', backupType: 'config', backupDate: '2026-01-08 09:30:00', hostname: 'PA-CHN-01', ip: '192.168.2.50', status: 'Success' },
    { deviceType: 'Paloalto FW', backupType: 'traffic log', backupDate: '2026-01-09 00:00:00', hostname: 'PA-BLR-Edge', ip: '192.168.2.51', status: 'Success' },

    // Cisco ASA
    { deviceType: 'Cisco ASA', backupType: 'config', backupDate: '2026-01-08 14:30:00', hostname: 'ASA-DEL-01', ip: '10.0.0.1', status: 'Success' },
    { deviceType: 'Cisco ASA', backupType: 'traffic log', backupDate: '2026-01-09 08:00:00', hostname: 'ASA-BLR-05', ip: '10.0.0.5', status: 'Success' },
    { deviceType: 'Cisco ASA', backupType: 'system/device', backupDate: '2026-01-07 18:00:00', hostname: 'ASA-HYD-02', ip: '10.0.0.6', status: 'Failed' },

    // Cisco FTD
    { deviceType: 'Cisco FTD', backupType: 'config', backupDate: '2026-01-09 11:00:00', hostname: 'FTD-HYD-01', ip: '10.20.20.1', status: 'Success' },
    { deviceType: 'Cisco FTD', backupType: 'tape', backupDate: '2026-01-01 00:00:00', hostname: 'FTD-ARC-01', ip: '10.20.20.99', status: 'Success' },

    // F5
    { deviceType: 'F5', backupType: 'config', backupDate: '2026-01-09 01:00:00', hostname: 'F5-LB-01', ip: '192.168.100.1', status: 'Success' },
    { deviceType: 'F5', backupType: 'system/device', backupDate: '2026-01-06 15:00:00', hostname: 'F5-LB-02', ip: '192.168.100.2', status: 'Failed' },
    { deviceType: 'F5', backupType: 'migrate export', backupDate: '2026-01-05 12:00:00', hostname: 'F5-GSLB-01', ip: '192.168.100.5', status: 'Success' },
    
    // Panorama
    { deviceType: 'Panorama', backupType: 'config', backupDate: '2026-01-09 03:00:00', hostname: 'PANO-HQ', ip: '10.50.50.50', status: 'Success' },
    { deviceType: 'Panorama', backupType: 'system/device', backupDate: '2026-01-08 04:00:00', hostname: 'PANO-DR', ip: '10.50.50.51', status: 'Success' }
  ];

  displayedReportItems: TaskReportItem[] = [];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.backupType = params['backupType'] || '';
      this.deviceType = params['deviceType'] || '';
      this.applyFilters();
    });
  }

  applyFilters(): void {
    this.displayedReportItems = this.allReportItems.filter(item => {
      const matchDevice = !this.deviceType || item.deviceType === this.deviceType;
      const matchBackup = !this.backupType || item.backupType === this.backupType;
      
      let matchDate = true;
      if (this.startTime && this.endTime) {
         // Simple string comparison for YYYY-MM-DD
         const itemDate = item.backupDate.split(' ')[0]; 
         matchDate = itemDate >= this.startTime && itemDate <= this.endTime;
      }

      return matchDevice && matchBackup && matchDate;
    });
  }
  
  onDateChange(): void {
     this.applyFilters();
  }
}
