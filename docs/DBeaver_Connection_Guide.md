# DBeaver Connection Guide for Oracle XE

This guide explains how to connect to the Oracle XE database using DBeaver.

## Connection Details

### Basic Connection Information

- **Host**: `localhost`
- **Port**: `1521`
- **Service Name**: `XEPDB1` (Pluggable Database)
- **SID**: `XE` (Container Database - use only if Service Name doesn't work)
- **Username**: `umd`
- **Password**: `portal_pass`

### Alternative Users

- **Username**: `portal_user`
- **Password**: `portal_pass`

## DBeaver Connection Setup

### Step 1: Create New Connection

1. Open DBeaver
2. Click **Database** → **New Database Connection**
3. Select **Oracle** from the list
4. Click **Next**

### Step 2: Configure Connection

#### Option A: Using Service Name (Recommended)

- **Host**: `localhost`
- **Port**: `1521`
- **Database/Schema**: Leave empty or use `XEPDB1`
- **Service name**: `XEPDB1`
- **Username**: `umd`
- **Password**: `portal_pass`

#### Option B: Using SID (If Service Name doesn't work)

- **Host**: `localhost`
- **Port**: `1521`
- **Database/Schema**: `XE`
- **SID**: `XE`
- **Username**: `umd`
- **Password**: `portal_pass`

### Step 3: Advanced Settings (if needed)

1. Go to **Driver properties** tab
2. Set **oracle.net.CONNECT_TIMEOUT**: `10000` (10 seconds)
3. Set **oracle.jdbc.timezoneAsRegion**: `false`

### Step 4: Test Connection

1. Click **Test Connection**
2. If prompted, download the Oracle JDBC driver
3. Click **Finish** once connection is successful

## Common Issues and Solutions

### Issue 1: "ORA-12514: TNS:listener does not currently know of service requested"

**Solution**: 
- Make sure you're using **Service Name**: `XEPDB1` (not SID)
- Verify the Oracle container is running: `docker ps | grep oracle`
- Check if the PDB is open: The container should automatically open XEPDB1

### Issue 2: "ORA-01017: invalid username/password"

**Solution**:
- Verify the username is `umd` (lowercase)
- Verify the password is `portal_pass`
- Try connecting with `portal_user` instead
- Check if the user exists: Run `make oracle-logs` to see user creation logs

### Issue 3: "Connection timeout"

**Solution**:
- Verify the Oracle container is running: `docker ps | grep oracle`
- Check if port 1521 is accessible: `netstat -an | grep 1521` or `lsof -i :1521`
- Increase connection timeout in DBeaver driver properties

### Issue 4: Cannot connect from Windows to WSL

**Solution**:
- If running Oracle in WSL, you may need to:
  - Use `localhost` or `127.0.0.1` as host
  - Ensure port forwarding is set up correctly
  - Try using the WSL IP address instead of localhost

## Connection String Formats

### JDBC URL Format

```
jdbc:oracle:thin:@localhost:1521/XEPDB1
```

### TNS Format

```
(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))
```

## Verifying Connection from Command Line

Test the connection using sqlplus:

```bash
# From inside the container
docker exec -it unified-portal-oracle sqlplus umd/portal_pass@XEPDB1

# Or if you have sqlplus installed locally
sqlplus umd/portal_pass@localhost:1521/XEPDB1
```

## Default Schema

When connected, you'll be in the `umd` schema. To see all tables:

```sql
SELECT table_name FROM user_tables;
```

## Additional Resources

- Oracle XE Documentation: https://docs.oracle.com/en/database/oracle/oracle-database/
- DBeaver Oracle Connection: https://dbeaver.com/docs/wiki/Oracle/
