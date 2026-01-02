# Code Walkthrough Guide

This document provides a comprehensive walkthrough of the Unified Portal codebase for newcomers. It explains the architecture, key components, and how different parts of the application work together.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Backend Walkthrough](#backend-walkthrough)
4. [Frontend Walkthrough](#frontend-walkthrough)
5. [Key Concepts](#key-concepts)
6. [Request Flow](#request-flow)
7. [Database Layer](#database-layer)
8. [Authentication Flow](#authentication-flow)
9. [Background Jobs](#background-jobs)
10. [Common Tasks](#common-tasks)

## Architecture Overview

The Unified Portal is a full-stack application with the following architecture:

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼─────────────────────────────────────┐
│         Nginx (Reverse Proxy)               │
│  - SSL Termination                         │
│  - Static File Serving (Frontend)          │
│  - API Proxying (Backend)                 │
└──────┬─────────────────────────────────────┘
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
│   Frontend  │   │   Backend   │   │   Oracle    │
│  (Angular)  │   │  (FastAPI)   │   │     XE      │
│             │   │              │   │             │
│ Port: 4200  │   │ Port: 8000   │   │ Port: 1521  │
└─────────────┘   └──────┬───────┘   └─────────────┘
                         │
                         │ SQLAlchemy ORM
                         │
                  ┌──────▼───────┐
                  │   Database   │
                  │   (Oracle)   │
                  └──────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Oracle XE**: Enterprise database
- **APScheduler**: Background job scheduling
- **Pydantic**: Data validation and settings management
- **JWT**: Authentication tokens

**Frontend:**
- **Angular 17**: Frontend framework
- **Angular Material**: UI component library
- **RxJS**: Reactive programming
- **TypeScript**: Type-safe JavaScript

**Infrastructure:**
- **Docker**: Containerization
- **Nginx**: Reverse proxy and static file server
- **Makefile**: Build automation

## Project Structure

```
unified-portal/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── v1/           # API version 1
│   │   │       ├── auth.py   # Authentication endpoints
│   │   │       ├── catalogues.py  # Catalogue management
│   │   │       ├── jobs.py   # Background job management
│   │   │       └── ...
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py     # Configuration management
│   │   │   ├── database.py   # Database connection
│   │   │   ├── security.py   # JWT and password hashing
│   │   │   ├── middleware.py # Request middleware
│   │   │   └── logging_config.py  # Logging setup
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py       # User model
│   │   │   ├── catalogue.py  # Catalogue model
│   │   │   └── rbac.py       # RBAC model
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── auth.py       # Auth request/response schemas
│   │   │   └── ...
│   │   ├── services/          # Business logic services
│   │   │   ├── email_service.py  # Email sending
│   │   │   ├── scheduler.py  # Job scheduler
│   │   │   ├── job_registry.py  # Job registration
│   │   │   └── workers/      # Background workers
│   │   └── main.py           # FastAPI application entry point
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   ├── requirements.txt       # Python dependencies
│   └── .env.*                 # Environment configurations
│
├── frontend/                   # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # Angular components
│   │   │   │   ├── login/    # Login component
│   │   │   │   ├── dashboard/ # Dashboard component
│   │   │   │   └── admin/    # Admin components
│   │   │   ├── services/     # Angular services
│   │   │   │   ├── auth.service.ts  # Authentication
│   │   │   │   ├── catalogue.service.ts  # Catalogue API
│   │   │   │   └── ...
│   │   │   ├── guards/       # Route guards
│   │   │   │   ├── auth.guard.ts  # Auth protection
│   │   │   │   └── admin.guard.ts  # Admin protection
│   │   │   ├── interceptors/ # HTTP interceptors
│   │   │   │   └── auth.interceptor.ts  # Token injection
│   │   │   └── app.module.ts # Root module
│   │   └── environments/     # Environment configs
│   └── package.json          # Node dependencies
│
├── nginx/                      # Nginx configuration
│   ├── nginx.conf             # Main config
│   └── conf.d/                # Site configs
│
├── docs/                       # Documentation
│   ├── CODE_WALKTHROUGH.md    # This file
│   └── DBeaver_Connection_Guide.md
│
├── docker-compose.yml          # Docker orchestration
├── Makefile                    # Build automation
└── README.md                   # Main documentation
```

## Backend Walkthrough

### Entry Point: `main.py`

The application starts here. Let's break down what happens:

```python
# 1. Import dependencies
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api_router

# 2. Create FastAPI app instance
app = FastAPI(
    title="Unified Portal",
    description="...",
    version="1.0.0"
)

# 3. Add middleware (order matters!)
app.add_middleware(RequestIDMiddleware)  # First: Generate request IDs
app.add_middleware(LoggingMiddleware)    # Second: Log requests
app.add_middleware(CORSMiddleware)       # Third: Handle CORS

# 4. Startup event: Initialize services
@app.on_event("startup")
async def startup_event():
    # - Test database connection
    # - Start background job scheduler
    # - Register all scheduled jobs

# 5. Include API routes
app.include_router(api_router, prefix="/api/v1")
```

**Key Points:**
- Middleware order matters: RequestID → Logging → CORS
- Startup event initializes database and background jobs
- All API routes are prefixed with `/api/v1`

### Configuration: `core/config.py`

Central configuration management using Pydantic:

```python
class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = ""
    ORACLE_USER: str = "umd"
    # ... more settings
    
    class Config:
        env_file = ".env"  # Loads from .env.dev, .env.staging, or .env.prod
```

**How it works:**
1. `load_settings()` checks `ENVIRONMENT` variable
2. Maps to `.env.dev`, `.env.staging`, or `.env.prod`
3. Creates `Settings` instance with environment-specific values
4. Settings are accessible via `settings` singleton

### Database Layer: `core/database.py`

```python
# Create database engine
engine = create_engine(
    settings.get_database_url(),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True  # Verify connections before use
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage in routes:**
```python
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### API Routes: `api/v1/`

#### Authentication: `auth.py`

```python
@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user in database
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # 2. Verify password (or bypass in debug mode)
    if settings.DEBUG_MODE:
        # Skip password check
    else:
        # Verify password hash
    
    # 3. Generate JWT tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    # 4. Return tokens and user info
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }
```

#### Catalogue Management: `catalogues.py`

```python
@router.get("/catalogues")
async def list_catalogues(db: Session = Depends(get_db)):
    # Query catalogues with relationships
    catalogues = db.query(Catalogue).all()
    return catalogues

@router.post("/catalogues")
async def create_catalogue(
    catalogue: CatalogueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create new catalogue
    db_catalogue = Catalogue(**catalogue.dict())
    db.add(db_catalogue)
    db.commit()
    return db_catalogue
```

### Models: `models/`

SQLAlchemy ORM models define database tables:

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    roles = relationship("Role", back_populates="user")
```

**Key Points:**
- `Base` is the declarative base from SQLAlchemy
- Relationships use `relationship()` for joins
- `__tablename__` maps to database table name

### Schemas: `schemas/`

Pydantic models for request/response validation:

```python
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
```

**Purpose:**
- Request validation (input)
- Response serialization (output)
- Type safety and documentation

### Services: `services/`

Business logic layer:

#### Email Service: `email_service.py`

```python
class EmailService:
    def send_email(self, subject, body, recipients, ...):
        # 1. Create email message
        msg = MIMEMultipart()
        msg['From'] = self.smtp_from_email
        msg['To'] = recipients
        
        # 2. Connect to SMTP server
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        
        # 3. Send email
        server.send_message(msg)
```

#### Scheduler Service: `scheduler.py`

```python
# Global scheduler instance
scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.start()

def add_job(func, trigger, id, name):
    scheduler.add_job(func, trigger=trigger, id=id, name=name)
```

### Background Workers: `services/workers/`

#### Base Worker: `base.py`

```python
class BaseWorker(ABC):
    name: str
    description: str
    
    def __init__(self):
        self.logger = get_logger(f"worker.{self.name}")
        self.db = None
    
    def get_db(self):
        """Get database session"""
        if not self.db:
            self.db = SessionLocal()
        return self.db
    
    async def run(self):
        """Main execution method"""
        try:
            await self.execute()
        finally:
            self.close_db()
    
    @abstractmethod
    async def execute(self):
        """Override in subclasses"""
        pass
```

#### Example Worker: `token_cleaner.py`

```python
class TokenCleanerWorker(BaseWorker):
    name = "token_cleaner"
    description = "Cleans expired refresh tokens"
    
    async def execute(self):
        db = self.get_db()
        # Query expired tokens
        # Delete them
        # Commit changes
```

## Frontend Walkthrough

### Entry Point: `app.module.ts`

```typescript
@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    DashboardComponent,
    // ... more components
  ],
  imports: [
    BrowserModule,
    HttpClientModule,  // For API calls
    AppRoutingModule,  // Routing
    // ... Angular Material modules
  ],
  providers: [
    AuthService,       // Authentication service
    CatalogueService,  // API service
    // ... more services
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### Services: `services/`

#### Auth Service: `auth.service.ts`

```typescript
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  
  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, {
      username,
      password
    }).pipe(
      tap(response => {
        // Store tokens in localStorage
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
      })
    );
  }
  
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/auth/me`);
  }
}
```

#### Catalogue Service: `catalogue.service.ts`

```typescript
@Injectable({
  providedIn: 'root'
})
export class CatalogueService {
  getCatalogues(): Observable<Catalogue[]> {
    return this.http.get<Catalogue[]>(`${this.apiUrl}/catalogues`);
  }
  
  createCatalogue(catalogue: Catalogue): Observable<Catalogue> {
    return this.http.post<Catalogue>(`${this.apiUrl}/catalogues`, catalogue);
  }
}
```

### Components: `components/`

#### Login Component: `login/login.component.ts`

```typescript
export class LoginComponent {
  loginForm: FormGroup;
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }
  
  onSubmit() {
    if (this.loginForm.valid) {
      const { username, password } = this.loginForm.value;
      this.authService.login(username, password).subscribe({
        next: () => this.router.navigate(['/dashboard']),
        error: (err) => console.error('Login failed', err)
      });
    }
  }
}
```

### Guards: `guards/`

#### Auth Guard: `auth.guard.ts`

```typescript
@Injectable()
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}
  
  canActivate(): boolean {
    if (this.authService.isAuthenticated()) {
      return true;
    }
    this.router.navigate(['/login']);
    return false;
  }
}
```

**Usage in routing:**
```typescript
{
  path: 'dashboard',
  component: DashboardComponent,
  canActivate: [AuthGuard]  // Protected route
}
```

### Interceptors: `interceptors/`

#### Auth Interceptor: `auth.interceptor.ts`

```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(req);
  }
}
```

**Purpose:** Automatically adds JWT token to all API requests

## Key Concepts

### 1. Dependency Injection

**Backend (FastAPI):**
```python
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    # FastAPI automatically injects database session
    return db.query(User).all()
```

**Frontend (Angular):**
```typescript
constructor(
  private authService: AuthService,  // Angular injects service
  private router: Router
) {}
```

### 2. Async/Await Pattern

**Backend:**
```python
async def get_users(db: Session = Depends(get_db)):
    users = await db.query(User).all()  # Async database query
    return users
```

**Frontend:**
```typescript
async login() {
  const response = await this.authService.login(username, password).toPromise();
  // Handle response
}
```

### 3. Observables (RxJS)

**Frontend:**
```typescript
this.catalogueService.getCatalogues().subscribe({
  next: (catalogues) => {
    this.catalogues = catalogues;
  },
  error: (err) => {
    console.error(err);
  }
});
```

### 4. Middleware Pattern

**Backend:**
```python
# Request flow:
# 1. RequestIDMiddleware → Generate unique request ID
# 2. LoggingMiddleware → Log request details
# 3. CORSMiddleware → Handle CORS headers
# 4. Route handler → Process request
```

## Request Flow

### Complete Request Flow Example

**1. User clicks "Login" button**

```
Frontend (LoginComponent)
  ↓
AuthService.login()
  ↓
HTTP POST /api/v1/auth/login
  ↓
Auth Interceptor adds token (if exists)
  ↓
Nginx receives request
  ↓
Nginx proxies to Backend:8000
  ↓
FastAPI receives request
  ↓
RequestIDMiddleware generates request ID
  ↓
LoggingMiddleware logs request
  ↓
CORSMiddleware adds CORS headers
  ↓
Route handler: /api/v1/auth/login
  ↓
AuthService.login() (backend)
  ↓
Database query: Find user
  ↓
Verify password / Debug mode check
  ↓
Generate JWT tokens
  ↓
Return response
  ↓
LoggingMiddleware logs response
  ↓
Nginx proxies response
  ↓
Frontend receives response
  ↓
AuthService stores tokens
  ↓
Router navigates to /dashboard
```

## Database Layer

### SQLAlchemy ORM

**Model Definition:**
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
```

**Querying:**
```python
# Get all users
users = db.query(User).all()

# Filter
user = db.query(User).filter(User.username == "admin").first()

# Create
new_user = User(username="test", email="test@example.com")
db.add(new_user)
db.commit()
```

**Relationships:**
```python
class Catalogue(Base):
    __tablename__ = "catalogues"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    category = relationship("Category", back_populates="catalogues")
```

### Migrations (Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Authentication Flow

### JWT Token Flow

```
1. User logs in
   ↓
2. Backend validates credentials
   ↓
3. Backend generates:
   - Access Token (short-lived, 30 min)
   - Refresh Token (long-lived, 7 days)
   ↓
4. Frontend stores tokens in localStorage
   ↓
5. Frontend includes access token in API requests
   ↓
6. Backend validates token on each request
   ↓
7. If access token expires:
   - Frontend uses refresh token to get new access token
   - Backend validates refresh token
   - Backend issues new access token
```

### Token Structure

```json
{
  "sub": "user_id",
  "username": "admin",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

## Background Jobs

### Job Lifecycle

```
1. Application Startup
   ↓
2. start_scheduler() called
   ↓
3. register_all_jobs() called
   ↓
4. Jobs registered with APScheduler
   ↓
5. Scheduler runs jobs at scheduled times
   ↓
6. Worker.execute() called
   ↓
7. Worker performs task
   ↓
8. Worker logs results
   ↓
9. Next scheduled run
```

### Creating a New Worker

**Step 1:** Create worker class
```python
class MyWorker(BaseWorker):
    name = "my_worker"
    description = "My worker description"
    
    async def execute(self):
        db = self.get_db()
        # Your logic here
```

**Step 2:** Register in `job_registry.py`
```python
add_job(
    func=MyWorker().run,
    trigger=CronTrigger(hour=2, minute=0),
    id="my_worker_daily",
    name="My Daily Worker"
)
```

## Common Tasks

### Adding a New API Endpoint

**1. Create route in `api/v1/`:**
```python
@router.get("/my-endpoint")
async def my_endpoint(db: Session = Depends(get_db)):
    return {"message": "Hello"}
```

**2. Add to router in `api/v1/__init__.py`:**
```python
from .my_module import router as my_router
api_router.include_router(my_router)
```

### Adding a New Frontend Component

**1. Generate component:**
```bash
ng generate component my-component
```

**2. Add route in `app-routing.module.ts`:**
```typescript
{
  path: 'my-component',
  component: MyComponentComponent
}
```

### Adding a New Database Model

**1. Create model in `models/`:**
```python
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
```

**2. Create migration:**
```bash
alembic revision --autogenerate -m "Add my_table"
alembic upgrade head
```

### Debugging Tips

**Backend:**
- Check logs: `tail -f logs/app.log`
- Use FastAPI docs: `http://localhost:8000/docs`
- Add breakpoints in IDE
- Check database: `docker exec -it unified-portal-oracle sqlplus umd/portal_pass@XEPDB1`

**Frontend:**
- Browser DevTools → Network tab
- Browser DevTools → Console
- Angular DevTools extension
- Check localStorage for tokens

**Common Issues:**
- CORS errors → Check `CORS_ORIGINS` in config
- Database connection → Check `DATABASE_URL`
- Token expired → Check token expiration settings
- 404 errors → Check route definitions

## Next Steps

1. **Read the README**: Start with the main README.md for setup instructions
2. **Explore the API**: Use `/docs` endpoint to see all available endpoints
3. **Check Examples**: Look at existing workers and components as examples
4. **Run Tests**: Run `make test-backend` to see how tests are structured
5. **Read Code Comments**: Most code has inline documentation

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.io/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
