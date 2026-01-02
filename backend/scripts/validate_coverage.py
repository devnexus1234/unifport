#!/usr/bin/env python3
"""
Coverage validation script for Docker builds.
Fails the build if coverage thresholds are not met.
"""
import sys
import json
import subprocess
from pathlib import Path

def run_coverage():
    """Run pytest with coverage and generate JSON report"""
    print("Running tests with coverage...")
    
    # Run pytest directly with streaming output (no capture_output)
    # Removing -q to show full logs as requested
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--cov=app", "--cov-report=json", "--cov-report=term"],
        text=True
    )
    
    if result.returncode != 0:
        print(f"\n❌ Tests failed with exit code: {result.returncode}", file=sys.stderr)
        return False
        
    return True

def check_overall_coverage(min_coverage=70):
    """Check overall coverage threshold"""
    coverage_file = Path("coverage.json")
    
    if not coverage_file.exists():
        print("ERROR: coverage.json not found")
        return False
    
    with open(coverage_file) as f:
        data = json.load(f)
    
    total_coverage = data["totals"]["percent_covered"]
    
    print(f"\n{'='*60}")
    print(f"Overall Coverage: {total_coverage:.2f}%")
    print(f"Required: {min_coverage}%")
    print(f"{'='*60}\n")
    
    if total_coverage < min_coverage:
        print(f"❌ FAILED: Overall coverage {total_coverage:.2f}% is below {min_coverage}%")
        return False
    
    print(f"✅ PASSED: Overall coverage {total_coverage:.2f}% meets {min_coverage}% threshold")
    return True

def check_service_coverage(min_coverage=95):
    """Check service tests coverage threshold"""
    coverage_file = Path("coverage.json")
    
    if not coverage_file.exists():
        print("ERROR: coverage.json not found")
        return False
    
    with open(coverage_file) as f:
        data = json.load(f)
    
    # Get all service files
    service_files = {
        path: info for path, info in data["files"].items()
        if "app/services/" in path and not path.endswith("__init__.py")
    }
    
    if not service_files:
        print("WARNING: No service files found in coverage report")
        return True
    
    print(f"\n{'='*60}")
    print(f"Service Coverage Check (Minimum: {min_coverage}%)")
    print(f"{'='*60}\n")
    
    failed_services = []
    
    for path, info in service_files.items():
        coverage = info["summary"]["percent_covered"]
        status = "✅" if coverage >= min_coverage else "❌"
        print(f"{status} {path}: {coverage:.2f}%")
        
        if coverage < min_coverage:
            failed_services.append((path, coverage))
    
    print(f"\n{'='*60}\n")
    
    if failed_services:
        print(f"❌ FAILED: {len(failed_services)} service(s) below {min_coverage}% coverage:")
        for path, coverage in failed_services:
            print(f"  - {path}: {coverage:.2f}%")
        return False
    
    print(f"✅ PASSED: All services meet {min_coverage}% coverage threshold")
    return True

def check_business_logic_coverage(min_coverage=95):
    """Check business logic coverage threshold (modules, models, api, utils)"""
    coverage_file = Path("coverage.json")
    
    if not coverage_file.exists():
        print("ERROR: coverage.json not found")
        return False
    
    with open(coverage_file) as f:
        data = json.load(f)
    
    # Get all business logic files
    business_logic_patterns = [
        "app/modules/",
        "app/models/",
        "app/api/",
        "app/utils/"
    ]
    
    business_logic_files = {}
    for path, info in data["files"].items():
        # Check if path matches any business logic pattern
        if any(pattern in path for pattern in business_logic_patterns):
            # Exclude __init__.py files
            if not path.endswith("__init__.py"):
                business_logic_files[path] = info
    
    if not business_logic_files:
        print("WARNING: No business logic files found in coverage report")
        return True
    
    print(f"\n{'='*60}")
    print(f"Business Logic Coverage Check (Minimum: {min_coverage}%)")
    print(f"Checking: modules/, models/, api/, utils/")
    print(f"{'='*60}\n")
    
    failed_files = []
    
    for path, info in business_logic_files.items():
        coverage = info["summary"]["percent_covered"]
        status = "✅" if coverage >= min_coverage else "❌"
        print(f"{status} {path}: {coverage:.2f}%")
        
        if coverage < min_coverage:
            failed_files.append((path, coverage))
    
    print(f"\n{'='*60}\n")
    
    if failed_files:
        print(f"❌ FAILED: {len(failed_files)} business logic file(s) below {min_coverage}% coverage:")
        for path, coverage in failed_files:
            print(f"  - {path}: {coverage:.2f}%")
        return False
    
    print(f"✅ PASSED: All business logic files meet {min_coverage}% coverage threshold")
    return True

def main():
    """Main validation function"""
    print("="*60)
    print("Coverage Validation for Docker Build")
    print("="*60)
    
    # Run tests with coverage
    if not run_coverage():
        print("\n❌ Tests failed")
        sys.exit(1)
    
    # Check overall coverage (70%)
    overall_passed = check_overall_coverage(min_coverage=70)
    
    # Check service coverage (95%)
    service_passed = check_service_coverage(min_coverage=95)
    
    # Check business logic coverage (75%)
    business_logic_passed = check_business_logic_coverage(min_coverage=75)
    
    # Final result
    print("\n" + "="*60)
    if overall_passed and service_passed and business_logic_passed:
        print("✅ ALL COVERAGE CHECKS PASSED")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ COVERAGE CHECKS FAILED")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
