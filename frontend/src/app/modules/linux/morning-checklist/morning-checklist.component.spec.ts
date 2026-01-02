import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MorningChecklistComponent } from './morning-checklist.component';
import { MorningChecklistService } from './services/morning-checklist.service';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of } from 'rxjs';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

describe('MorningChecklistComponent', () => {
    let component: MorningChecklistComponent;
    let fixture: ComponentFixture<MorningChecklistComponent>;
    let mockService: jasmine.SpyObj<MorningChecklistService>;
    let mockDialog: jasmine.SpyObj<MatDialog>;
    let mockSnackBar: jasmine.SpyObj<MatSnackBar>;

    beforeEach(async () => {
        mockService = jasmine.createSpyObj('MorningChecklistService', [
            'getDates',
            'getSummary',
            'getDetails',
            'validateSelected',
            'validateGroups',
            'getApplicationOwnerMapping',
            'getChecklistValidationStatus',
            'getValidatedList'
        ]);
        mockDialog = jasmine.createSpyObj('MatDialog', ['open']);
        mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);

        // Setup default returns
        mockService.getDates.and.returnValue(of([]));
        mockService.getApplicationOwnerMapping.and.returnValue(of({}));
        mockService.getSummary.and.returnValue(of({ reachability: { total: 0, reachable: 0, failed: 0, unreachable: 0 }, date: '2025-01-01', groups: [] }));

        await TestBed.configureTestingModule({
            declarations: [MorningChecklistComponent],
            providers: [
                { provide: MorningChecklistService, useValue: mockService },
                { provide: MatDialog, useValue: mockDialog },
                { provide: MatSnackBar, useValue: mockSnackBar },
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        })
            .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(MorningChecklistComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should toggle selection', () => {
        const hostname = 'host1';
        component.toggleSelection(hostname);
        expect(component.selectedHostnames.has(hostname)).toBeTrue();
        component.toggleSelection(hostname);
        expect(component.selectedHostnames.has(hostname)).toBeFalse();
    });

    it('should handle master toggle', () => {
        component.detailRows = [
            { hostname: 'host1', application_name: 'app1', mc_check_date: '2025-01-01', success: false },
            { hostname: 'host2', application_name: 'app1', mc_check_date: '2025-01-01', success: false }
        ] as any[];

        // Select All
        component.masterToggle();
        expect(component.selectedHostnames.size).toBe(2);
        expect(component.isAllSelected()).toBeTrue();

        // Deselect All
        component.masterToggle();
        expect(component.selectedHostnames.size).toBe(0);
        expect(component.isAllSelected()).toBeFalse();
    });

    it('should call validateSelected when validating hostnames', () => {
        component.selectedDate = new Date();
        component.selectedHostnames.add('host1');

        // Mock dialog close with a comment
        mockDialog.open.and.returnValue({
            afterClosed: () => of('Test Comment')
        } as any);

        mockService.validateSelected.and.returnValue(of({ status: 'validated_selected' }));

        component.validateSelectedHostnames();

        expect(mockDialog.open).toHaveBeenCalled();
        expect(mockService.validateSelected).toHaveBeenCalled();
        expect(component.selectedHostnames.size).toBe(0); // Should clear after success
    });

    it('should toggle group selection only for groups with errors', () => {
        const groupWithErrors: any = { application_name: 'app1', asset_owner: 'owner1', error_count: 5 };
        const groupNoErrors: any = { application_name: 'app2', asset_owner: 'owner2', error_count: 0 };

        component.toggleGroupSelection(groupWithErrors);
        expect(component.selectedGroups.has(groupWithErrors)).toBeTrue();

        component.toggleGroupSelection(groupNoErrors);
        expect(component.selectedGroups.has(groupNoErrors)).toBeFalse();
    });

    it('should handle master group toggle considering only errors', () => {
        const group1: any = { application_name: 'app1', error_count: 5 };
        const group2: any = { application_name: 'app2', error_count: 0 };
        component.groups = [group1, group2];

        component.masterGroupToggle();
        expect(component.selectedGroups.size).toBe(1);
        expect(component.selectedGroups.has(group1)).toBeTrue();
        expect(component.isAllGroupsSelected()).toBeTrue();

        component.masterGroupToggle();
        expect(component.selectedGroups.size).toBe(0);
        expect(component.isAllGroupsSelected()).toBeFalse();
    });

    it('should call validateGroups when validating groups', () => {
        component.selectedDate = new Date();
        component.selectedGroups.add({ application_name: 'app1' } as any);

        mockDialog.open.and.returnValue({
            afterClosed: () => of('Group Comment')
        } as any);

        mockService.validateGroups.and.returnValue(of({ status: 'validated_groups' }));

        component.validateSelectedGroups();

        expect(mockDialog.open).toHaveBeenCalled();
        expect(mockService.validateGroups).toHaveBeenCalled();
        expect(component.selectedGroups.size).toBe(0);
    });
});
