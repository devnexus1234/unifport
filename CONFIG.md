# Configuration Guide

## Multi-Environment Configuration

The Unified Portal supports multiple environments with separate configuration files for both backend and frontend.

## Backend Configuration

### Environment Files

- **Development**: `backend/.env.dev`
- **Staging**: `backend/.env.staging`
- **Production**: `backend/.env.prod`

### Setting Environment

Set the `ENVIRONMENT` variable before running:

```bash
export ENVIRONMENT=development
make run-backend

# Or specify directly
make run-backend ENV=development
make run-backend ENV=staging
make run-backend ENV=production
```

### Configuration Variables

#### Database
- `ORACLE_USER` - Database username
- `ORACLE_PASSWORD` - Database password
- `ORACLE_HOST` - Database host
- `ORACLE_PORT` - Database port
- `ORACLE_SERVICE` - Database service name

#### Security
- `SECRET_KEY` - JWT secret key (MUST change in production)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiry
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiry

#### LDAP
- `LDAP_ENABLED` - Enable/disable LDAP
- `LDAP_SERVER` - LDAP server URL
- `LDAP_BASE_DN` - LDAP base DN
- `LDAP_USER_DN` - LDAP user DN
- `LDAP_GROUP_DN` - LDAP group DN

#### Application
- `APP_TITLE` - Application title
- `PAGE_SIZE` - Default page size
- `ENABLE_AUDIT_LOGGING` - Enable audit logging
- `ENABLE_RATE_LIMITING` - Enable rate limiting

## Frontend Configuration

### Environment Files

- **Development**: `frontend/src/environments/environment.ts`
- **Staging**: `frontend/src/environments/environment.staging.ts`
- **Production**: `frontend/src/environments/environment.prod.ts`

### Building for Different Environments

```bash
# Development (default)
npm start

# Staging
ng build --configuration=staging

# Production
ng build --configuration=production
```

### Configuration Variables

- `production` - Production mode flag
- `apiUrl` - Backend API URL
- `appName` - Application name
- `appVersion` - Application version
- `enableDebug` - Enable debug mode
- `theme.defaultTheme` - Default theme (light/dark/auto)
- `theme.enableThemeToggle` - Enable theme toggle

## App-Level Configuration

Application-level settings that are the same across environments but configurable:

### Backend (`app/core/app_config.py`)

- UI settings (title, description, version)
- Pagination defaults
- File upload limits
- Theme defaults
- Security policies
- Branding (colors, logos)

### Accessing App Config

**API Endpoints:**
- `GET /api/v1/config/app` - Public app configuration
- `GET /api/v1/config/environment` - Environment-specific config (requires auth)

**Frontend Service:**
```typescript
import { ConfigService } from './services/config.service';

constructor(private configService: ConfigService) {
  this.configService.appConfig$.subscribe(config => {
    // Use config
  });
}
```

## Dark Theme

### Configuration

Theme can be configured via:
1. Environment file: `theme.defaultTheme`
2. App config API: `default_theme`
3. User preference (stored in localStorage)

### Theme Modes

- **light**: Light color scheme
- **dark**: Dark color scheme
- **auto**: Follows system preference

### Toggle Theme

Users can toggle theme via the theme icon in the toolbar. Preference is saved in localStorage.

## JWT Authentication

### Configuration

- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token lifetime (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token lifetime (default: 7)
- `SECRET_KEY` - JWT signing key (MUST be strong in production)
- `JWT_ISSUER` - Token issuer
- `JWT_AUDIENCE` - Token audience

### Token Structure

Access tokens include:
- `sub` - Username
- `user_id` - User ID
- `email` - User email
- `exp` - Expiration time
- `iat` - Issued at
- `iss` - Issuer
- `aud` - Audience
- `type` - Token type (access/refresh)

### Automatic Refresh

The frontend automatically refreshes expired access tokens using refresh tokens. This is handled by the `AuthInterceptor`.

## Best Practices

1. **Never commit secrets**: Use `.env` files (gitignored) for sensitive data
2. **Use strong keys**: Generate strong SECRET_KEY for production
3. **Environment-specific configs**: Keep dev/staging/prod configs separate
4. **Validate configs**: Check configuration on startup
5. **Document changes**: Update this file when adding new config options

