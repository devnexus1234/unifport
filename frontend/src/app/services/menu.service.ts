import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, Subject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface MenuItem {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  catalogues: CatalogueItem[];
}

export interface CatalogueItem {
  id: number;
  name: string;
  description?: string;
  route?: string;
  icon?: string;
  api_endpoint?: string;
}

export interface MenuResponse {
  menu: MenuItem[];
}

@Injectable({
  providedIn: 'root'
})
export class MenuService {
  private apiUrl = environment.apiUrl;
  private selectedCategorySubject = new BehaviorSubject<MenuItem | null>(null);
  public selectedCategory$ = this.selectedCategorySubject.asObservable();
  private menuRefreshSubject = new Subject<void>();
  public menuRefresh$ = this.menuRefreshSubject.asObservable();

  constructor(private http: HttpClient) {}

  getMenu(): Observable<MenuResponse> {
    return this.http.get<MenuResponse>(`${this.apiUrl}/menu`);
  }

  selectCategory(category: MenuItem | null) {
    this.selectedCategorySubject.next(category);
  }

  getSelectedCategory(): MenuItem | null {
    return this.selectedCategorySubject.value;
  }

  refreshMenu() {
    this.menuRefreshSubject.next();
  }
}

