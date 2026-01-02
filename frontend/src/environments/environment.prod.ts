export const environment = {
  production: true,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Unified Management Portal',
  appVersion: '1.0.0',
  enableDebug: false,
  enableRegistration: false,
  enablePasswordReset: true,
  sessionTimeout: 30, // minutes
  pageSize: 50,
  theme: {
    defaultTheme: 'light',
    enableThemeToggle: true
  },
  features: {
    enableAuditLogging: true,
    enableRateLimiting: true
  }
};

