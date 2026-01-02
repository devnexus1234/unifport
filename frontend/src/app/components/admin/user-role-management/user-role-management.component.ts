import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RoleService, User, Role, UserRolesResponse } from '../../../services/role.service';
import { AuthService } from '../../../services/auth.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-user-role-management',
  templateUrl: './user-role-management.component.html',
  styleUrls: ['./user-role-management.component.scss']
})
export class UserRoleManagementComponent implements OnInit {
  users: User[] = [];
  roles: Role[] = [];
  selectedUser: User | null = null;
  userRoles: Role[] = [];
  loading = false;
  enableDebug = environment.enableDebug;
  currentUserId: number | null = null;

  constructor(
    private roleService: RoleService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
    const currentUser = this.authService.getCurrentUser();
    this.currentUserId = currentUser ? currentUser.id : null;
    this.loadUsers();
    this.loadRoles();
  }

  loadUsers() {
    this.loading = true;
    this.roleService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.loading = false;
        // If a user was selected, update their object from the new list
        if (this.selectedUser) {
          const updatedUser = this.users.find(u => u.id === this.selectedUser!.id);
          if (updatedUser) {
            this.selectedUser = updatedUser;
          }
        }
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.snackBar.open('Error loading users', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  loadRoles() {
    this.roleService.getRoles().subscribe({
      next: (roles) => {
        this.roles = roles;
      },
      error: (error) => {
        console.error('Error loading roles:', error);
        this.snackBar.open('Error loading roles', 'Close', { duration: 3000 });
      }
    });
  }

  selectUser(user: User) {
    this.selectedUser = user;
    this.loadUserRoles(user.id);
  }

  loadUserRoles(userId: number) {
    this.loading = true;
    this.roleService.getUserRoles(userId).subscribe({
      next: (response) => {
        this.userRoles = response.roles;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading user roles:', error);
        this.snackBar.open('Error loading user roles', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  hasRole(roleId: number): boolean {
    return this.userRoles.some(r => r.id === roleId);
  }

  isSelfModification(): boolean {
    return this.selectedUser !== null && this.selectedUser.id === this.currentUserId;
  }

  toggleRole(role: Role) {
    if (!this.selectedUser) return;
    if (this.isSelfModification()) {
      this.snackBar.open('You cannot modify your own roles', 'Close', { duration: 3000 });
      return;
    }

    const hasRole = this.hasRole(role.id);
    if (hasRole) {
      this.removeRole(role);
    } else {
      this.assignRole(role);
    }
  }

  assignRole(role: Role) {
    if (!this.selectedUser) return;
    if (this.isSelfModification()) {
      this.snackBar.open('You cannot assign roles to yourself', 'Close', { duration: 3000 });
      return;
    }

    this.roleService.assignRoleToUser(this.selectedUser.id, role.id).subscribe({
      next: () => {
        this.snackBar.open(`Role "${role.name}" assigned successfully`, 'Close', { duration: 3000 });
        this.loadUserRoles(this.selectedUser!.id);
        this.loadUsers(); // Refresh user list to update roles
      },
      error: (error) => {
        console.error('Error assigning role:', error);
        this.snackBar.open(error.error?.detail || 'Error assigning role', 'Close', { duration: 3000 });
      }
    });
  }

  removeRole(role: Role) {
    if (!this.selectedUser) return;
    if (this.isSelfModification()) {
      this.snackBar.open('You cannot remove roles from yourself', 'Close', { duration: 3000 });
      return;
    }

    const confirmed = confirm(
      `Are you sure you want to remove role "${role.name}" from user "${this.selectedUser.username}"?\n\n` +
      `This will revoke all permissions associated with this role.`
    );

    if (!confirmed) {
      return;
    }

    this.loading = true;
    this.roleService.removeRoleFromUser(this.selectedUser.id, role.id).subscribe({
      next: () => {
        this.snackBar.open(`Role "${role.name}" removed successfully from ${this.selectedUser!.username}`, 'Close', { duration: 3000 });
        this.loadUserRoles(this.selectedUser!.id);
        this.loadUsers(); // Refresh user list to update roles
        this.loading = false;
      },
      error: (error) => {
        console.error('Error removing role:', error);
        this.snackBar.open(error.error?.detail || 'Error removing role', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  toggleAdminStatus(checked: boolean) {
    if (!this.selectedUser) return;

    if (this.isSelfModification()) {
      // Revert the toggle visually (though disabled attribute should prevent this)
      this.selectedUser.is_admin = !checked;
      this.snackBar.open('You cannot modify your own admin status', 'Close', { duration: 3000 });
      return;
    }

    const action = checked ? 'promote to Admin' : 'revoke Admin status';
    const confirmed = confirm(
      `Are you sure you want to ${action} for user "${this.selectedUser.username}"?`
    );

    if (!confirmed) {
      // Revert the toggle if cancelled
      this.selectedUser.is_admin = !checked;
      return;
    }

    this.loading = true;
    this.roleService.updateUserStatus(this.selectedUser.id, { is_admin: checked }).subscribe({
      next: (updatedUser) => {
        this.snackBar.open(`User ${this.selectedUser!.username} status updated`, 'Close', { duration: 3000 });
        this.loadUsers();
        this.loading = false;
        if (this.selectedUser && this.selectedUser.id === updatedUser.id) {
          this.selectedUser.is_admin = updatedUser.is_admin;
        }
      },
      error: (error) => {
        console.error('Error updating user status:', error);
        this.snackBar.open('Error updating user status', 'Close', { duration: 3000 });
        this.loading = false;
        // Revert on error
        if (this.selectedUser) {
          this.selectedUser.is_admin = !checked;
        }
      }
    });
  }

  getAvailableRoles(): Role[] {
    return this.roles.filter(role => !this.hasRole(role.id));
  }
}
