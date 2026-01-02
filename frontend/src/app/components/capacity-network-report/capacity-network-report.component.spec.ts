
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CapacityNetworkReportComponent } from './capacity-network-report.component';
import { CapacityNetworkReportService } from '../../services/capacity-network-report.service';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';

describe('CapacityNetworkReportComponent', () => {
  let component: CapacityNetworkReportComponent;
  let fixture: ComponentFixture<CapacityNetworkReportComponent>;
  let mockService: any;
  let mockSnackBar: any;

  beforeEach(async () => {
    mockService = {
      getDashboard: jasmine.createSpy('getDashboard').and.returnValue(of({
        region: 'XYZ',
        production_hours: true,
        zone_summary: []
      })),
      getZones: jasmine.createSpy('getZones').and.returnValue(of({ zones: [] })),
      getDevices: jasmine.createSpy('getDevices').and.returnValue(of({ devices: [] })),
      getRegions: jasmine.createSpy('getRegions').and.returnValue(of({ regions: ['XYZ'] })),
      getZoneDeviceMappings: jasmine.createSpy('getZoneDeviceMappings').and.returnValue(of({ mappings: [] }))
    };

    mockSnackBar = {
      open: jasmine.createSpy('open')
    };

    await TestBed.configureTestingModule({
      declarations: [ CapacityNetworkReportComponent ],
      imports: [ ReactiveFormsModule ],
      providers: [
        FormBuilder,
        { provide: CapacityNetworkReportService, useValue: mockService },
        { provide: MatSnackBar, useValue: mockSnackBar }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CapacityNetworkReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load dashboard on init', () => {
    expect(mockService.getDashboard).toHaveBeenCalledWith('XYZ', true);
  });
});
