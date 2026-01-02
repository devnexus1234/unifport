import { Component, OnInit } from "@angular/core";
import {
  animate,
  state,
  style,
  transition,
  trigger,
} from "@angular/animations";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { MatSnackBar } from "@angular/material/snack-bar";
import { finalize } from "rxjs/operators";
import {
  CapacityFirewallReportService,
  ZoneSummary,
  DeviceDetail,
} from "../../services/capacity-firewall-report.service";
import { DateAdapter } from "@angular/material/core";
import { HttpErrorResponse } from "@angular/common/http";

@Component({
  selector: "app-capacity-firewall-report",
  templateUrl: "./capacity-firewall-report.component.html",
  styleUrls: ["./capacity-firewall-report.component.scss"],
  animations: [
    trigger("detailExpand", [
      state("collapsed", style({ height: "0px", minHeight: "0" })),
      state("expanded", style({ height: "*" })),
      transition(
        "expanded <=> collapsed",
        animate("225ms cubic-bezier(0.4, 0.0, 0.2, 1)")
      ),
    ]),
  ],
})
export class CapacityFirewallReportComponent implements OnInit {
  form: FormGroup;
  loading = false;
  downloading = false;

  // Dashboard properties
  selectedRegion: string = "XYZ";
  productionHours: boolean = true;
  zones: ZoneSummary[] = [];
  deviceDetails: { [zoneName: string]: DeviceDetail[] } = {};
  expandedZones: Set<string> = new Set();
  loadingDashboard = false;
  regions = ["XYZ", "ORM-XYZ", "DRM", "ORM-DRM"];

  // Device/Zone Management properties
  activeMode: "device" | "zone" | null = null;
  availableZones: { zone_name: string; region_name: string }[] = [];
  availableDevices: string[] = [];
  availableRegions: string[] = [];
  zoneDeviceMappings: { zone_name: string; device_name: string }[] = [];
  loadingOptions = false;

  // Device form
  deviceForm: FormGroup;

  // Zone form
  zoneForm: FormGroup;

  // Table column definitions
  zoneSummaryColumns: string[] = [
    "zone_name",
    "total_device_count",
    "cpu_normal",
    "memory_normal",
    "cpu_warning",
    "memory_warning",
    "cpu_critical",
    "memory_critical",
  ];

  deviceDetailsColumns: string[] = [
    "device_name",
    "cpu_peak_percent",
    "cpu_peak_count",
    "cpu_peak_duration_min",
    "memory_peak_percent",
    "memory_peak_count",
    "memory_peak_duration_min",
  ];

  constructor(
    private fb: FormBuilder,
    private capacityReportService: CapacityFirewallReportService,
    private snackBar: MatSnackBar,
    private dateAdapter: DateAdapter<Date>
  ) {
    // Ensure datepicker uses local format (dd-MM-yyyy can be displayed via input)
    this.dateAdapter.setLocale("en-GB");

    this.form = this.fb.group({
      start_date: ["", Validators.required],
      end_date: ["", Validators.required],
      raw_data_file: [null, Validators.required],
      connection_count_file: [null, Validators.required],
    });

    // Device form
    this.deviceForm = this.fb.group({
      action: ["ADD DEVICE", Validators.required], // ADD DEVICE, EDIT DEVICE, DELETE DEVICE
      zone_name: ["", Validators.required],
      device_name: ["", Validators.required],
      new_device_name: [""], // For editing device name (required when action is EDIT DEVICE)
    });

    // Zone form
    this.zoneForm = this.fb.group({
      action: ["ADD ZONE", Validators.required], // ADD ZONE, EDIT ZONE, DELETE ZONE
      region_name: ["", Validators.required],
      zone_name: ["", Validators.required],
      new_zone_name: [""], // For editing zone name (required when action is EDIT ZONE)
    });
  }

  ngOnInit() {
    this.loadDashboard();
    this.loadManagementOptions();
  }

  onFileChange(
    event: Event,
    controlName: "raw_data_file" | "connection_count_file"
  ) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.form.patchValue({ [controlName]: input.files[0] });
    }
  }

  submit() {
    if (this.form.invalid) {
      this.snackBar.open(
        "Please fill all fields and attach both files.",
        "Close",
        { duration: 3000 }
      );
      return;
    }

    const { start_date, end_date, raw_data_file, connection_count_file } =
      this.form.value;
    const formData = new FormData();
    formData.append("start_date", start_date);
    formData.append("end_date", end_date);
    formData.append("raw_data_file", raw_data_file);
    formData.append("connection_count_file", connection_count_file);

    this.loading = true;
    this.capacityReportService
      .upload(formData)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: (res) => {
          this.snackBar.open(
            "Capacity report submitted successfully.",
            "Close",
            { duration: 3000 }
          );
          this.downloadReport();
        },
        error: (err) => {
          const msg = err?.error?.detail || "Failed to submit capacity report.";
          this.snackBar.open(msg, "Close", { duration: 4000 });
        },
      });
  }

  private downloadReport() {
    this.downloading = true;
    // First download detailed per-device report
    this.capacityReportService.downloadDevices().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "capacity_devices.xlsx";
        a.click();
        window.URL.revokeObjectURL(url);

        // Then download summary production/non-production report
        this.capacityReportService
          .downloadSummary()
          .pipe(finalize(() => (this.downloading = false)))
          .subscribe({
            next: (summaryBlob) => {
              const url2 = window.URL.createObjectURL(summaryBlob);
              const a2 = document.createElement("a");
              a2.href = url2;
              a2.download = "capacity_summary.xlsx";
              a2.click();
              window.URL.revokeObjectURL(url2);
              this.snackBar.open("Reports downloaded.", "Close", {
                duration: 3000,
              });
            },
            error: (err: HttpErrorResponse) => {
              const msg =
                err?.error?.detail || "Failed to download summary report.";
              this.snackBar.open(msg, "Close", { duration: 4000 });
            },
          });
      },
      error: (err: HttpErrorResponse) => {
        this.downloading = false;
        const msg =
          err?.error?.detail || "Failed to download detailed device report.";
        this.snackBar.open(msg, "Close", { duration: 4000 });
      },
    });
  }

  onRegionChange() {
    this.expandedZones.clear();
    this.deviceDetails = {};
    this.loadDashboard();
  }

  onProductionHoursChange() {
    this.expandedZones.clear();
    this.deviceDetails = {};
    this.loadDashboard();
  }

  loadDashboard() {
    this.loadingDashboard = true;
    this.capacityReportService
      .getDashboard(this.selectedRegion, this.productionHours)
      .pipe(finalize(() => (this.loadingDashboard = false)))
      .subscribe({
        next: (response) => {
          this.zones = response.zone_summary;
        },
        error: (err: HttpErrorResponse) => {
          const msg = err?.error?.detail || "Failed to load dashboard data.";
          this.snackBar.open(msg, "Close", { duration: 4000 });
        },
      });
  }

  toggleZone(zoneName: string) {
    if (this.expandedZones.has(zoneName)) {
      this.expandedZones.delete(zoneName);
    } else {
      this.expandedZones.add(zoneName);
      // Load device details if not already loaded
      if (!this.deviceDetails[zoneName]) {
        this.loadDeviceDetails(zoneName);
      }
    }
  }

  loadDeviceDetails(zoneName: string) {
    this.capacityReportService
      .getDashboard(this.selectedRegion, this.productionHours, zoneName)
      .subscribe({
        next: (response) => {
          if (response.device_details) {
            this.deviceDetails[zoneName] = response.device_details;
          }
        },
        error: (err: HttpErrorResponse) => {
          const msg = err?.error?.detail || "Failed to load device details.";
          this.snackBar.open(msg, "Close", { duration: 4000 });
        },
      });
  }

  isZoneExpanded(zoneName: string): boolean {
    return this.expandedZones.has(zoneName);
  }

  getDeviceDetails(zoneName: string): DeviceDetail[] {
    return this.deviceDetails[zoneName] || [];
  }

  // Device/Zone Management methods
  setActiveMode(mode: "device" | "zone") {
    this.activeMode = this.activeMode === mode ? null : mode;
    if (this.activeMode) {
      this.loadManagementOptions();
    }
  }

  loadManagementOptions() {
    this.loadingOptions = true;

    // Load zones
    this.capacityReportService.getZones().subscribe({
      next: (response) => {
        this.availableZones = response.zones;
      },
      error: (err) => {
        console.error("Failed to load zones:", err);
      },
    });

    // Load devices
    this.capacityReportService.getDevices().subscribe({
      next: (response) => {
        this.availableDevices = response.devices;
      },
      error: (err) => {
        console.error("Failed to load devices:", err);
      },
    });

    // Load regions
    this.capacityReportService.getRegions().subscribe({
      next: (response) => {
        this.availableRegions = response.regions;
      },
      error: (err) => {
        console.error("Failed to load regions:", err);
      },
    });

    // Load zone-device mappings
    this.capacityReportService.getZoneDeviceMappings().subscribe({
      next: (response) => {
        this.zoneDeviceMappings = response.mappings;
        this.loadingOptions = false;
      },
      error: (err) => {
        console.error("Failed to load zone-device mappings:", err);
        this.loadingOptions = false;
      },
    });
  }

  getDevicesForZone(zoneName: string): string[] {
    if (!zoneName) return [];
    return this.zoneDeviceMappings
      .filter((m) => m.zone_name === zoneName)
      .map((m) => m.device_name);
  }

  getZonesForRegion(
    regionName: string
  ): { zone_name: string; region_name: string }[] {
    if (!regionName) return [];
    return this.availableZones.filter((z) => z.region_name === regionName);
  }

  submitDeviceForm() {
    const { action, zone_name, device_name, new_device_name } =
      this.deviceForm.value;

    // Validate based on action
    if (action === "EDIT DEVICE") {
      if (!zone_name || !device_name || !new_device_name) {
        this.snackBar.open(
          "Please fill all required fields including New Device Name.",
          "Close",
          {
            duration: 3000,
          }
        );
        return;
      }
    } else {
      if (this.deviceForm.invalid) {
        this.snackBar.open("Please fill all required fields.", "Close", {
          duration: 3000,
        });
        return;
      }
    }

    this.loading = true;

    if (action === "ADD DEVICE") {
      if (!device_name) {
        this.snackBar.open("Please enter a device name.", "Close", {
          duration: 3000,
        });
        this.loading = false;
        return;
      }

      this.capacityReportService
        .addDeviceToZone(zone_name, device_name)
        .pipe(finalize(() => (this.loading = false)))
        .subscribe({
          next: (response) => {
            this.snackBar.open(
              response.message || "Device added successfully.",
              "Close",
              {
                duration: 3000,
              }
            );
            this.deviceForm.reset({ action: "ADD DEVICE" });
            this.loadManagementOptions();
            this.loadDashboard();
          },
          error: (err: HttpErrorResponse) => {
            const msg = err?.error?.detail || "Failed to add device to zone.";
            this.snackBar.open(msg, "Close", { duration: 4000 });
          },
        });
    } else if (action === "EDIT DEVICE") {
      this.capacityReportService
        .updateDeviceZoneMapping(
          zone_name,
          device_name,
          undefined, // No zone change
          new_device_name
        )
        .pipe(finalize(() => (this.loading = false)))
        .subscribe({
          next: (response) => {
            this.snackBar.open(
              response.message || "Device mapping updated successfully.",
              "Close",
              {
                duration: 3000,
              }
            );
            this.deviceForm.reset({ action: "EDIT DEVICE" });
            this.loadManagementOptions();
            this.loadDashboard();
          },
          error: (err: HttpErrorResponse) => {
            const msg =
              err?.error?.detail || "Failed to update device mapping.";
            this.snackBar.open(msg, "Close", { duration: 4000 });
          },
        });
    } else if (action === "DELETE DEVICE") {
      if (!zone_name || !device_name) {
        this.snackBar.open(
          "Please select zone and device to delete.",
          "Close",
          {
            duration: 3000,
          }
        );
        this.loading = false;
        return;
      }

      this.capacityReportService
        .deleteDeviceZoneMapping(zone_name, device_name)
        .pipe(finalize(() => (this.loading = false)))
        .subscribe({
          next: (response) => {
            this.snackBar.open(
              response.message || "Device removed from zone successfully.",
              "Close",
              {
                duration: 3000,
              }
            );
            this.deviceForm.reset({ action: "DELETE DEVICE" });
            this.loadManagementOptions();
            this.loadDashboard();
          },
          error: (err: HttpErrorResponse) => {
            const msg =
              err?.error?.detail || "Failed to delete device mapping.";
            this.snackBar.open(msg, "Close", { duration: 4000 });
          },
        });
    }
  }

  submitZoneForm() {
    const { action, region_name, zone_name, new_zone_name } =
      this.zoneForm.value;

    // Validate based on action
    if (action === "EDIT ZONE") {
      if (!region_name || !zone_name || !new_zone_name) {
        this.snackBar.open(
          "Please fill all required fields including New Zone Name.",
          "Close",
          {
            duration: 3000,
          }
        );
        return;
      }
    } else {
      if (this.zoneForm.invalid) {
        this.snackBar.open("Please fill all required fields.", "Close", {
          duration: 3000,
        });
        return;
      }
    }

    this.loading = true;

    this.capacityReportService
      .manageZone(region_name, zone_name, action, new_zone_name)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: (response) => {
          this.snackBar.open(
            response.message || "Zone operation completed.",
            "Close",
            {
              duration: 3000,
            }
          );
          this.zoneForm.reset({ action: "ADD ZONE" });
          this.loadManagementOptions();
          this.loadDashboard();
        },
        error: (err: HttpErrorResponse) => {
          const msg = err?.error?.detail || "Failed to perform zone operation.";
          this.snackBar.open(msg, "Close", { duration: 4000 });
        },
      });
  }

  getRiskClass(value: number): string {
    if (value >= 71) {
      return 'cell-critical';
    } else if (value >= 61) {
      return 'cell-warning';
    } else {
      return 'cell-normal';
    }
  }
}
