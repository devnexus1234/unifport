import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Role {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface RoleWithPermissions extends Role {
  menu_permissions: MenuPermission[];
  catalogue_permissions: CatalogueRolePermission[];
}

export interface MenuPermission {
  id: number;
  menu_id: number;
  role_id: number;
  permission_type: string;
}

export interface CatalogueRolePermission {
  id: number;
  catalogue_id: number;
  role_id: number;
  permission_type: string;
}

export interface Menu {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
}

export interface Catalogue {
  id: number;
  name: string;
  description?: string;
  menu_id: number;
  icon?: string;
}

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getRoles(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.apiUrl}/admin/roles`);
  }

  getRole(roleId: number): Observable<RoleWithPermissions> {
    return this.http.get<RoleWithPermissions>(`${this.apiUrl}/admin/roles/${roleId}`);
  }

  createRole(role: { name: string; description?: string }): Observable<Role> {
    return this.http.post<Role>(`${this.apiUrl}/admin/roles`, role);
  }

  updateRole(roleId: number, role: Partial<Role>): Observable<Role> {
    return this.http.put<Role>(`${this.apiUrl}/admin/roles/${roleId}`, role);
  }

  deleteRole(roleId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/admin/roles/${roleId}`);
  }

  assignMenuPermission(roleId: number, menuId: number, permissionType: string): Observable<MenuPermission> {
    return this.http.post<MenuPermission>(`${this.apiUrl}/admin/roles/${roleId}/menu-permissions`, {
      role_id: roleId,
      menu_id: menuId,
      permission_type: permissionType
    });
  }

  removeMenuPermission(roleId: number, menuId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/admin/roles/${roleId}/menu-permissions/${menuId}`);
  }

  assignCataloguePermission(roleId: number, catalogueId: number, permissionType: string): Observable<CatalogueRolePermission> {
    return this.http.post<CatalogueRolePermission>(`${this.apiUrl}/admin/roles/${roleId}/catalogue-permissions`, {
      role_id: roleId,
      catalogue_id: catalogueId,
      permission_type: permissionType
    });
  }

  removeCataloguePermission(roleId: number, catalogueId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/admin/roles/${roleId}/catalogue-permissions/${catalogueId}`);
  }

  getMenus(): Observable<Menu[]> {
    return this.http.get<Menu[]>(`${this.apiUrl}/admin/menus`);
  }

  deleteMenu(menuId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/admin/menus/${menuId}`);
  }

  reorderMenu(menuId: number, displayOrder: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/menus/${menuId}/reorder`, { display_order: displayOrder });
  }

  getCatalogues(menuId?: number): Observable<Catalogue[]> {
    const params = menuId ? `?menu_id=${menuId}` : '';
    return this.http.get<Catalogue[]>(`${this.apiUrl}/admin/catalogues${params}`);
  }

  // User-Role Management (Debug Mode Only)
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/admin/users`);
  }

  getUserRoles(userId: number): Observable<UserRolesResponse> {
    return this.http.get<UserRolesResponse>(`${this.apiUrl}/admin/users/${userId}/roles`);
  }

  assignRoleToUser(userId: number, roleId: number, isDl: boolean = false, dlName?: string): Observable<UserRole> {
    return this.http.post<UserRole>(`${this.apiUrl}/admin/users/${userId}/roles`, {
      role_id: roleId,
      is_dl: isDl,
      dl_name: dlName || null
    });
  }

  removeRoleFromUser(userId: number, roleId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/admin/users/${userId}/roles/${roleId}`);
  }

  updateUserStatus(userId: number, status: { is_admin?: boolean, is_active?: boolean }): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/users/${userId}/status`, status);
  }
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_admin: boolean;
  is_active: boolean;
  roles?: Role[];
}

export interface UserRole {
  id: number;
  user_id: number;
  role_id: number;
  is_dl: boolean;
  dl_name?: string;
}

export interface UserRolesResponse {
  user_id: number;
  username: string;
  roles: Role[];
}
