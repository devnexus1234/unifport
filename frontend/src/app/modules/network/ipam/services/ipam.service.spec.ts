/// <reference types="jasmine" />
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { IpamService, IpamSegment, IpamAllocationUpdate } from './ipam.service';
import { environment } from '../../../../../environments/environment';

describe('IpamService', () => {
    let service: IpamService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [IpamService]
        });
        service = TestBed.inject(IpamService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('should retrieve segments', () => {
        const dummySegments: IpamSegment[] = [
            {
                id: 1,
                segment: '10.0.0.0/24',
                name: 'Test',
                description: 'Desc',
                location: 'Loc',
                entity: 'Ent',
                environment: 'Env',
                network_zone: 'Zone',
                segment_description: 'SegDesc',
                assigned_ips: 0,
                unassigned_ips: 254,
                total_ips: 254
            }
        ];

        service.getSegments().subscribe(segments => {
            expect(segments.length).toBe(1);
            expect(segments).toEqual(dummySegments);
        });

        const req = httpMock.expectOne(`${environment.apiUrl}/network/ipam/segments`);
        expect(req.request.method).toBe('GET');
        req.flush(dummySegments);
    });

    it('should update allocation', () => {
        const updateData: IpamAllocationUpdate = { status: 'Assigned', ritm: 'RITM1', comment: 'Test', source: 'Manual' };

        service.updateAllocation(1, '10.0.0.5', updateData).subscribe(res => {
            expect(res).toBeDefined();
        });

        const req = httpMock.expectOne(`${environment.apiUrl}/network/ipam/segments/1/ips/10.0.0.5`);
        expect(req.request.method).toBe('PUT');
        req.flush({});
    });
});
