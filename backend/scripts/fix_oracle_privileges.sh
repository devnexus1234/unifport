#!/bin/bash
# Script to fix Oracle user privileges (tablespace quota issue)
# Usage: ./fix_oracle_privileges.sh

ORACLE_CONTAINER="${ORACLE_CONTAINER:-unified-portal-oracle}"
ORACLE_PDB="${ORACLE_PDB:-XEPDB1}"
ORACLE_USER="${ORACLE_USER:-umduser}"

echo "Fixing Oracle privileges for user: $ORACLE_USER"
echo "Container: $ORACLE_CONTAINER"
echo "PDB: $ORACLE_PDB"
echo ""

# Grant unlimited quota on USERS tablespace
docker exec $ORACLE_CONTAINER /bin/bash -c "sqlplus -s / as sysdba <<EOF
ALTER SESSION SET CONTAINER=$ORACLE_PDB;
ALTER USER $ORACLE_USER QUOTA UNLIMITED ON USERS;
GRANT UNLIMITED TABLESPACE TO $ORACLE_USER;
GRANT RESOURCE TO $ORACLE_USER;
GRANT CONNECT TO $ORACLE_USER;
COMMIT;
EXIT;
EOF"

if [ $? -eq 0 ]; then
    echo "✓ Privileges granted successfully!"
else
    echo "✗ Failed to grant privileges"
    exit 1
fi
