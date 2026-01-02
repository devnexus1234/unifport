import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatMenuModule } from '@angular/material/menu';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './components/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { AdminComponent } from './components/admin/admin.component';
import { CatalogueListComponent } from './components/admin/catalogue-list/catalogue-list.component';
import { CatalogueFormComponent } from './components/admin/catalogue-form/catalogue-form.component';
import { RoleManagementComponent } from './components/admin/role-management/role-management.component';
import { CategoryManagementComponent } from './components/admin/category-management/category-management.component';
import { CategoryFormComponent } from './components/admin/category-form/category-form.component';
import { UserRoleManagementComponent } from './components/admin/user-role-management/user-role-management.component';
import { MorningChecklistComponent } from './modules/linux/morning-checklist/morning-checklist.component';
import { ValidatedHostnamesComponent } from './modules/linux/morning-checklist/components/validated-hostnames/validated-hostnames.component';
import { CommentDialogComponent } from './modules/linux/morning-checklist/components/comment-dialog/comment-dialog.component';
import { CapacityFirewallReportComponent } from './components/capacity-firewall-report/capacity-firewall-report.component';
import { CapacityNetworkReportComponent } from './components/capacity-network-report/capacity-network-report.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';
import { ThemeService } from './services/theme.service';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    DashboardComponent,
    AdminComponent,
    CatalogueListComponent,
    CatalogueFormComponent,
    RoleManagementComponent,
    CategoryManagementComponent,
    CategoryFormComponent,
    UserRoleManagementComponent,
    MorningChecklistComponent,
    ValidatedHostnamesComponent,
    CommentDialogComponent,
    CapacityFirewallReportComponent,
    CapacityNetworkReportComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatTableModule,
    MatDialogModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatChipsModule,
    MatTooltipModule,
    MatCheckboxModule,
    MatDividerModule,
    MatExpansionModule,
    MatMenuModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  providers: [
    AuthGuard,
    AdminGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

