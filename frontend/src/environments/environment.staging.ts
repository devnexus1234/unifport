export const environment = {
  production: false,
  apiUrl: 'https://staging-api.example.com/api/v1',
  appName: 'Unified Management Portal (Staging)',
  appVersion: '1.0.0',
  enableDebug: true,
  enableRegistration: false,
  enablePasswordReset: true,
  sessionTimeout: 30, // minutes
  pageSize: 20,
  theme: {
    defaultTheme: 'light',
    enableThemeToggle: true
  },
  features: {
    enableAuditLogging: true,
    enableRateLimiting: true
  }
};

