import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RoleService, Role, RoleWithPermissions, Menu, Catalogue } from '../../../services/role.service';

@Component({
  selector: 'app-role-management',
  templateUrl: './role-management.component.html',
  styleUrls: ['./role-management.component.scss']
})
export class RoleManagementComponent implements OnInit {
  roles: Role[] = [];
  selectedRole: RoleWithPermissions | null = null;
  menus: Menu[] = [];
  catalogues: Catalogue[] = [];
  loading = false;
  
  // Form state
  showCreateForm = false;
  newRoleName = '';
  newRoleDescription = '';
  editingRole: Role | null = null;
  editRoleName = '';
  editRoleDescription = '';

  constructor(
    private roleService: RoleService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadRoles();
    this.loadMenus();
    this.loadCatalogues();
  }

  loadRoles() {
    this.loading = true;
    this.roleService.getRoles().subscribe({
      next: (roles) => {
        this.roles = roles;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading roles:', error);
        this.snackBar.open('Error loading roles', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  loadMenus() {
    this.roleService.getMenus().subscribe({
      next: (menus) => {
        this.menus = menus;
      },
      error: (error) => {
        console.error('Error loading menus:', error);
      }
    });
  }

  loadCatalogues() {
    this.roleService.getCatalogues().subscribe({
      next: (catalogues) => {
        this.catalogues = catalogues;
      },
      error: (error) => {
        console.error('Error loading catalogues:', error);
      }
    });
  }

  selectRole(role: Role) {
    this.loading = true;
    this.roleService.getRole(role.id).subscribe({
      next: (roleWithPerms) => {
        this.selectedRole = roleWithPerms;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading role details:', error);
        this.snackBar.open('Error loading role details', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  createRole() {
    if (!this.newRoleName.trim()) {
      this.snackBar.open('Role name is required', 'Close', { duration: 3000 });
      return;
    }

    this.roleService.createRole({
      name: this.newRoleName,
      description: this.newRoleDescription
    }).subscribe({
      next: () => {
        this.snackBar.open('Role created successfully', 'Close', { duration: 3000 });
        this.showCreateForm = false;
        this.newRoleName = '';
        this.newRoleDescription = '';
        this.loadRoles();
      },
      error: (error) => {
        console.error('Error creating role:', error);
        this.snackBar.open(error.error?.detail || 'Error creating role', 'Close', { duration: 3000 });
      }
    });
  }

  startEditRole(role: Role) {
    this.editingRole = role;
    this.editRoleName = role.name;
    this.editRoleDescription = role.description || '';
  }

  cancelEdit() {
    this.editingRole = null;
    this.editRoleName = '';
    this.editRoleDescription = '';
  }

  updateRole() {
    if (!this.editingRole) return;

    this.roleService.updateRole(this.editingRole.id, {
      name: this.editRoleName,
      description: this.editRoleDescription
    }).subscribe({
      next: () => {
        this.snackBar.open('Role updated successfully', 'Close', { duration: 3000 });
        this.cancelEdit();
        this.loadRoles();
        if (this.selectedRole && this.selectedRole.id === this.editingRole!.id) {
          this.selectRole(this.editingRole!);
        }
      },
      error: (error) => {
        console.error('Error updating role:', error);
        this.snackBar.open(error.error?.detail || 'Error updating role', 'Close', { duration: 3000 });
      }
    });
  }

  deleteRole(role: Role) {
    if (!confirm(`Are you sure you want to delete role "${role.name}"?`)) {
      return;
    }

    this.roleService.deleteRole(role.id).subscribe({
      next: () => {
        this.snackBar.open('Role deleted successfully', 'Close', { duration: 3000 });
        this.loadRoles();
        if (this.selectedRole && this.selectedRole.id === role.id) {
          this.selectedRole = null;
        }
      },
      error: (error) => {
        console.error('Error deleting role:', error);
        this.snackBar.open(error.error?.detail || 'Error deleting role', 'Close', { duration: 3000 });
      }
    });
  }

  hasMenuPermission(menuId: number): boolean {
    if (!this.selectedRole) return false;
    return this.selectedRole.menu_permissions.some(p => p.menu_id === menuId);
  }

  getMenuPermissionType(menuId: number): string {
    if (!this.selectedRole) return '';
    const perm = this.selectedRole.menu_permissions.find(p => p.menu_id === menuId);
    return perm ? perm.permission_type : '';
  }

  toggleMenuPermission(menuId: number) {
    if (!this.selectedRole) return;

    const hasPerm = this.hasMenuPermission(menuId);
    if (hasPerm) {
      this.roleService.removeMenuPermission(this.selectedRole.id, menuId).subscribe({
        next: () => {
          this.snackBar.open('Menu permission removed', 'Close', { duration: 2000 });
          this.selectRole(this.selectedRole!);
        },
        error: (error) => {
          console.error('Error removing menu permission:', error);
          this.snackBar.open('Error removing permission', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.roleService.assignMenuPermission(this.selectedRole.id, menuId, 'read').subscribe({
        next: () => {
          this.snackBar.open('Menu permission assigned', 'Close', { duration: 2000 });
          this.selectRole(this.selectedRole!);
        },
        error: (error) => {
          console.error('Error assigning menu permission:', error);
          this.snackBar.open('Error assigning permission', 'Close', { duration: 3000 });
        }
      });
    }
  }

  updateMenuPermissionType(menuId: number, permissionType: string) {
    if (!this.selectedRole) return;

    this.roleService.removeMenuPermission(this.selectedRole.id, menuId).subscribe({
      next: () => {
        this.roleService.assignMenuPermission(this.selectedRole!.id, menuId, permissionType).subscribe({
          next: () => {
            this.snackBar.open('Menu permission updated', 'Close', { duration: 2000 });
            this.selectRole(this.selectedRole!);
          },
          error: (error) => {
            console.error('Error updating menu permission:', error);
            this.snackBar.open('Error updating permission', 'Close', { duration: 3000 });
          }
        });
      },
      error: (error) => {
        console.error('Error updating menu permission:', error);
        this.snackBar.open('Error updating permission', 'Close', { duration: 3000 });
      }
    });
  }

  hasCataloguePermission(catalogueId: number): boolean {
    if (!this.selectedRole) return false;
    return this.selectedRole.catalogue_permissions.some(p => p.catalogue_id === catalogueId);
  }

  getCataloguePermissionType(catalogueId: number): string {
    if (!this.selectedRole) return '';
    const perm = this.selectedRole.catalogue_permissions.find(p => p.catalogue_id === catalogueId);
    return perm ? perm.permission_type : '';
  }

  toggleCataloguePermission(catalogueId: number) {
    if (!this.selectedRole) return;

    const hasPerm = this.hasCataloguePermission(catalogueId);
    if (hasPerm) {
      this.roleService.removeCataloguePermission(this.selectedRole.id, catalogueId).subscribe({
        next: () => {
          this.snackBar.open('Catalogue permission removed', 'Close', { duration: 2000 });
          this.selectRole(this.selectedRole!);
        },
        error: (error) => {
          console.error('Error removing catalogue permission:', error);
          this.snackBar.open('Error removing permission', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.roleService.assignCataloguePermission(this.selectedRole.id, catalogueId, 'read').subscribe({
        next: () => {
          this.snackBar.open('Catalogue permission assigned', 'Close', { duration: 2000 });
          this.selectRole(this.selectedRole!);
        },
        error: (error) => {
          console.error('Error assigning catalogue permission:', error);
          this.snackBar.open('Error assigning permission', 'Close', { duration: 3000 });
        }
      });
    }
  }

  updateCataloguePermissionType(catalogueId: number, permissionType: string) {
    if (!this.selectedRole) return;

    this.roleService.removeCataloguePermission(this.selectedRole.id, catalogueId).subscribe({
      next: () => {
        this.roleService.assignCataloguePermission(this.selectedRole!.id, catalogueId, permissionType).subscribe({
          next: () => {
            this.snackBar.open('Catalogue permission updated', 'Close', { duration: 2000 });
            this.selectRole(this.selectedRole!);
          },
          error: (error) => {
            console.error('Error updating catalogue permission:', error);
            this.snackBar.open('Error updating permission', 'Close', { duration: 3000 });
          }
        });
      },
      error: (error) => {
        console.error('Error updating catalogue permission:', error);
        this.snackBar.open('Error updating permission', 'Close', { duration: 3000 });
      }
    });
  }

  getCataloguesForMenu(menuId: number): Catalogue[] {
    return this.catalogues.filter(c => c.menu_id === menuId);
  }
}
