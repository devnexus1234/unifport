import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Catalogue {
  id: number;
  name: string;
  description?: string;
  menu_id: number;  // Required: link to menu
  category_id?: number;  // Optional: for backward compatibility
  api_endpoint?: string;
  frontend_route?: string;
  icon?: string;
  is_enabled: boolean;
  is_active: boolean;
  display_order: number;
  config?: any;
  category?: {
    id: number;
    name: string;
    description?: string;
    icon?: string;
  };
  menu?: {
    id: number;
    name: string;
    description?: string;
    icon?: string;
  };
}

export interface CatalogueCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  is_enabled: boolean;
  is_active: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class CatalogueService {
  private apiUrl = environment.apiUrl;
  private categoriesRefreshSubject = new Subject<void>();
  public categoriesRefresh$ = this.categoriesRefreshSubject.asObservable();

  constructor(private http: HttpClient) { }

  refreshCategories() {
    this.categoriesRefreshSubject.next();
  }

  getCatalogues(categoryId?: number): Observable<Catalogue[]> {
    let params = new HttpParams();
    if (categoryId) {
      params = params.set('category_id', categoryId.toString());
    }
    return this.http.get<Catalogue[]>(`${this.apiUrl}/catalogues`, { params });
  }

  getCatalogue(id: number): Observable<Catalogue> {
    return this.http.get<Catalogue>(`${this.apiUrl}/catalogues/${id}`);
  }

  // Public method to get active categories for header dropdown
  getActiveCategories(): Observable<CatalogueCategory[]> {
    return this.http.get<CatalogueCategory[]>(`${this.apiUrl}/catalogues/categories`);
  }

  // Admin methods
  getAllCatalogues(): Observable<Catalogue[]> {
    return this.http.get<Catalogue[]>(`${this.apiUrl}/admin/catalogues`);
  }

  createCatalogue(catalogue: Partial<Catalogue>): Observable<Catalogue> {
    return this.http.post<Catalogue>(`${this.apiUrl}/admin/catalogues`, catalogue);
  }

  updateCatalogue(id: number, catalogue: Partial<Catalogue>): Observable<Catalogue> {
    return this.http.put<Catalogue>(`${this.apiUrl}/admin/catalogues/${id}`, catalogue);
  }

  deleteCatalogue(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/catalogues/${id}`);
  }

  getCategories(): Observable<CatalogueCategory[]> {
    return this.http.get<CatalogueCategory[]>(`${this.apiUrl}/admin/categories`);
  }

  createCategory(category: Partial<CatalogueCategory>): Observable<CatalogueCategory> {
    return this.http.post<CatalogueCategory>(`${this.apiUrl}/admin/categories`, category);
  }

  updateCategory(id: number, category: Partial<CatalogueCategory>): Observable<CatalogueCategory> {
    return this.http.put<CatalogueCategory>(`${this.apiUrl}/admin/categories/${id}`, category);
  }

  deleteCategory(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/categories/${id}`);
  }

  reorderCategory(id: number, displayOrder: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/categories/${id}/reorder`, { display_order: displayOrder });
  }

  reorderCatalogue(id: number, displayOrder: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/catalogues/${id}/reorder`, { display_order: displayOrder });
  }
}

