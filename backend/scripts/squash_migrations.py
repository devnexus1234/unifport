import os
import sys
import glob
import subprocess
import oracledb

# ...

    # Connection string for Admin (current user must have DBA privs)
    dsn = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SERVICE)
    
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
        cursor = conn.cursor()
    except oracledb.Error as e:
        print(f"Error connecting to Oracle: {e}")
        sys.exit(1)
        
    # 2. Create Temporary User/Schema
    print(f"Creating temporary schema '{TEMP_USER}'...")
    try:
        # Drop if exists (cleanup from failed run)
        try:
            cursor.execute(f"DROP USER {TEMP_USER} CASCADE")
        except oracledb.DatabaseError:
            pass
            
        cursor.execute(f"CREATE USER {TEMP_USER} IDENTIFIED BY {TEMP_PASSWORD}")
        cursor.execute(f"GRANT CONNECT, RESOURCE, DBA TO {TEMP_USER}")
        cursor.execute(f"GRANT UNLIMITED TABLESPACE TO {TEMP_USER}")
        print("Temporary schema created.")
    except oracledb.Error as e:
        print(f"Error creating temp user: {e}")
        conn.close()
        sys.exit(1)
        
    conn.close() # Close admin connection
    
    # 3. Generate New Migration against Temporary Schema
    print("Generating new initial migration...")
    
    # Construct Temp DB URL
    TEMP_DB_URL = f"oracle+oracledb://{TEMP_USER}:{TEMP_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SERVICE}"
    
    # Prepare Environment for Alembic
    env = os.environ.copy()
    env["DATABASE_URL"] = TEMP_DB_URL
    
    # ...

    # 4. Cleanup Temporary Schema
    print(f"Dropping temporary schema '{TEMP_USER}'...")
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
        cursor = conn.cursor()
        cursor.execute(f"DROP USER {TEMP_USER} CASCADE")
        print("Temporary schema dropped.")
        conn.close()
    except oracledb.Error as e:
        print(f"Error dropping temp user: {e}")
        # Don't exit, proceed to stamp
        
    # 5. Stamp Current Database
    print("Stamping current database to HEAD...")
    # Generate DB URL for current DB
    CURRENT_DB_URL = f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SERVICE}"
    env["DATABASE_URL"] = CURRENT_DB_URL
    
    # Manually clear alembic_version table to avoid "Can't locate revision" error
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
        cursor = conn.cursor()
        print("Clearing alembic_version table...")
        try:
            cursor.execute("DELETE FROM alembic_version")
            conn.commit()
        except oracledb.DatabaseError as e:
            print(f"Warning: Could not clear alembic_version (maybe table doesn't exist yet?): {e}")
        conn.close()
    except oracledb.Error as e:
        print(f"Error connecting to clear version table: {e}")

    # Alembic stamp head
    run_command('alembic stamp head', env=env)
    
    print("Squash complete! Data preserved, migrations reset.")

if __name__ == "__main__":
    main()
