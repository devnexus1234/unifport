import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { AdminComponent } from './components/admin/admin.component';
import { CatalogueWelcomeComponent } from './components/catalogue-welcome/catalogue-welcome.component';
import { AuthGuard } from './guards/auth.guard';
import { MorningChecklistComponent } from './modules/linux/morning-checklist/morning-checklist.component';

import { ValidatedHostnamesComponent } from './modules/linux/morning-checklist/components/validated-hostnames/validated-hostnames.component';
import { AdminGuard } from './guards/admin.guard';
import { CapacityFirewallReportComponent } from './components/capacity-firewall-report/capacity-firewall-report.component';
import { CapacityNetworkReportComponent } from './components/capacity-network-report/capacity-network-report.component';
import { FirewallBackupReportComponent } from './features/firewall/components/firewall-backup-report/firewall-backup-report.component';
import { FirewallTaskReportComponent } from './features/firewall/components/firewall-task-report/firewall-task-report.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'admin', component: AdminComponent, canActivate: [AuthGuard, AdminGuard] },
  {
    path: 'catalogues/linux/morning-checklist',
    component: MorningChecklistComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/morning-checklist',
    component: MorningChecklistComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/linux/validated-hostnames',
    component: ValidatedHostnamesComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/network/ipam',
    loadChildren: () => import('./modules/network/ipam/ipam.module').then(m => m.IpamModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/:route',
    component: CatalogueWelcomeComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/firewall/capacity-firewall-report',
    component: CapacityFirewallReportComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/firewall/backup-report',
    component: FirewallBackupReportComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/network/capacity-report',
    component: CapacityNetworkReportComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'catalogues/firewall/task-report',
    component: FirewallTaskReportComponent,
    canActivate: [AuthGuard]
  },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

