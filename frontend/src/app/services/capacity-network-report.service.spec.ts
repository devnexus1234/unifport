
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CapacityNetworkReportService } from './capacity-network-report.service';
import { environment } from '../../environments/environment';

describe('CapacityNetworkReportService', () => {
  let service: CapacityNetworkReportService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CapacityNetworkReportService]
    });
    service = TestBed.inject(CapacityNetworkReportService);
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

    const req = httpMock.expectOne(`${environment.apiUrl}/capacity-network-report/dashboard?region=XYZ&production_hours=true`);
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should add device to zone', () => {
    service.addDeviceToZone('Zone A', 'Device 1').subscribe(response => {
      expect(response).toBeTruthy();
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/capacity-network-report/device-zone-mapping/add`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ zone_name: 'Zone A', device_name: 'Device 1' });
    req.flush({ message: 'Success' });
  });

  it('should get zones', () => {
      const mockZones = { zones: [{ zone_name: 'Z1', region_name: 'R1' }] };
      service.getZones().subscribe(res => {
          expect(res).toEqual(mockZones);
      });
      const req = httpMock.expectOne(`${environment.apiUrl}/capacity-network-report/zones`);
      expect(req.request.method).toBe('GET');
      req.flush(mockZones);
  });
});
