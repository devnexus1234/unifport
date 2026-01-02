// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Unified Management Portal',
  appVersion: '1.0.0',
  enableDebug: true,
  enableRegistration: true,
  enablePasswordReset: true,
  sessionTimeout: 30, // minutes
  pageSize: 20,
  theme: {
    defaultTheme: 'light', // 'light' | 'dark' | 'auto'
    enableThemeToggle: true
  },
  features: {
    enableAuditLogging: false,
    enableRateLimiting: false
  }
};

