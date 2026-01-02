# Fix for libaio.so.1 Error - ONE TIME FIX

This error has been fixed permanently in the Dockerfile and entrypoint.sh. You just need to rebuild the Docker image.

## Quick Fix (Run This Now)

```bash
cd /home/rohit/github/unified-portal
docker-compose build --no-cache backend
```

Or use the rebuild script:
```bash
./backend/scripts/rebuild-docker.sh
```

## What Was Fixed

1. **Dockerfile ENV**: Added standard library paths (`/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu`) to `LD_LIBRARY_PATH`
2. **ld.so.conf**: Added standard library paths to the system library configuration
3. **entrypoint.sh**: Enhanced to always include standard library paths in `LD_LIBRARY_PATH`

## Verification

After rebuilding, test it:
```bash
docker-compose run --rm --no-deps backend python -c "import cx_Oracle; print('OK')"
```

Or run your original command:
```bash
make dev-with-db ENV=development
```

## Why This Happened

The Oracle Instant Client needs `libaio.so.1` which is a system library. Even though it was installed, the library loader couldn't find it because the standard library paths weren't in `LD_LIBRARY_PATH` or `ld.so.conf`.

## This Won't Happen Again

The fix is permanent in:
- `backend/Dockerfile` (lines 37-38, 55)
- `backend/entrypoint.sh` (lines 6-20)

Every new build will have these paths configured correctly.
