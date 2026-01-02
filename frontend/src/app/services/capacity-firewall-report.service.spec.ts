
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CapacityReportService } from './capacity-report.service';
import { environment } from '../../environments/environment';

describe('CapacityReportService', () => {
  let service: CapacityReportService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CapacityReportService]
    });
    service = TestBed.inject(CapacityReportService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get dashboard data', () => {
    const mockData = {
      region: 'XYZ',
      production_hours: true,
      zone_summary: []
    };

    service.getDashboard('XYZ', true).subscribe(data => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/capacity-report/dashboard?region=XYZ&production_hours=true`);
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should add device to zone', () => {
    service.addDeviceToZone('Zone A', 'Device 1').subscribe(response => {
      expect(response).toBeTruthy();
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/capacity-report/device-zone-mapping/add`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ zone_name: 'Zone A', device_name: 'Device 1' });
    req.flush({ message: 'Success' });
  });
});
