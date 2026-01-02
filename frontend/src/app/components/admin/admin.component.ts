import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {
  activeTab = 0;
  enableDebug = environment.enableDebug;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    // Ensure we're at the top of the page
    window.scrollTo(0, 0);

    // Check for tab query parameter
    this.route.queryParams.subscribe(params => {
      if (params['tab']) {
        switch (params['tab']) {
          case 'catalogues':
            this.activeTab = 0;
            break;
          case 'roles':
            this.activeTab = 1;
            break;
          case 'categories':
            this.activeTab = 2;
            break;
          case 'users':
            // Only switch if debug is enabled or if we decide users tab is always visible
            if (this.enableDebug) {
              this.activeTab = 3;
            }
            break;
        }
      }
    });
  }

  setActiveTab(index: number) {
    this.activeTab = index;
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }
}

