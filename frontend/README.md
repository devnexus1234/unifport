# Unified Portal Frontend

Angular frontend for the Unified Portal application.

## Quick Start

### Prerequisites
- Node.js (v18 or higher recommended)
- Angular CLI (~18.2.0): `npm install -g @angular/cli@18.2.0`

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm start
```

3. Open browser:
```
http://localhost:4200
```

## Build

Build for production:
```bash
ng build --configuration production
```

## Development

The app will automatically reload if you change any of the source files.

## Code Structure

- `src/app/components/` - Angular components
- `src/app/services/` - API services
- `src/app/guards/` - Route guards
- `src/app/interceptors/` - HTTP interceptors

## Testing

The frontend uses **Karma** and **Jasmine** for unit testing.

### Running Tests
```bash
# Run unit tests
npm test

# Run with code coverage
ng test --code-coverage
```

### Writing Tests

#### Unit Tests (`.spec.ts`)

Tests are co-located with the component/service they test.

**Example Component Test:**
```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginComponent]
    }).compileComponents();
    
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have invalid form initially', () => {
    expect(component.loginForm.valid).toBeFalsy();
  });
});
```

