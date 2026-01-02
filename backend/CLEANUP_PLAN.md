# Backend Cleanup Plan

## Files to Remove

### 1. Duplicate/Old Test Files (Keep the comprehensive versions)
- `tests/test_api_integration/test_remaining_apis.py` (keep test_remaining_apis_complete.py)
- `tests/test_api_integration/test_all_apis_comprehensive.py` (duplicate of other comprehensive tests)
- `tests/test_modules/test_morning_checklist.py` (keep test_morning_checklist_complete.py)
- `tests/test_modules/test_morning_checklist_and_report.py` (keep test_morning_checklist_api_full.py and test_report_generator_comprehensive.py)

### 2. Debug/Utility Scripts (No longer needed)
- `check_validated.py` - Debug script
- `debug_db.py` - Debug script
- `verify_ist.py` - Debug script

### 3. Unused Directories
- `MagicMock/` - Leftover directory

### 4. Old Test Files (Superseded by comprehensive versions)
- `tests/test_api_integration/test_auth_api.py` (keep test_auth_api_full.py)
- `tests/test_api_integration/test_catalogue_api.py` (keep test_catalogue_api_full.py)
- `tests/test_api_integration/test_dashboard_api.py` (keep test_dashboard_api_full.py and test_dashboard_comprehensive.py)

## Files to Keep

### Essential Test Files
- `tests/test_api_integration/test_admin_comprehensive.py` ✅
- `tests/test_api_integration/test_auth_api_full.py` ✅
- `tests/test_api_integration/test_catalogue_api_full.py` ✅
- `tests/test_api_integration/test_catalogues_comprehensive.py` ✅
- `tests/test_api_integration/test_dashboard_api_full.py` ✅
- `tests/test_api_integration/test_dashboard_comprehensive.py` ✅
- `tests/test_api_integration/test_menu_comprehensive.py` ✅
- `tests/test_api_integration/test_remaining_apis_complete.py` ✅
- `tests/test_modules/test_morning_checklist_api_full.py` ✅
- `tests/test_modules/test_morning_checklist_complete.py` ✅
- `tests/test_modules/test_report_generator_comprehensive.py` ✅

### Essential Scripts
- `scripts/validate_coverage.py` ✅
- `scripts/seed_menus.py` ✅
- `scripts/create_admin.py` ✅
- `scripts/init_db.py` ✅
- All other production scripts ✅

## Summary
- **Total files to remove**: ~10 files
- **Reason**: Duplicates, debug scripts, superseded test files
- **Impact**: None - all functionality preserved in comprehensive test files
