#!/bin/bash
# Script to manually grant tablespace quota permissions to Oracle user
# Usage: ./grant_tablespace_quota.sh

ORACLE_CONTAINER="${ORACLE_CONTAINER:-unified-portal-oracle}"
ORACLE_PDB="${ORACLE_PDB:-XEPDB1}"
ORACLE_USER="${ORACLE_USER:-umduser}"

echo "Granting tablespace quota permissions to user: $ORACLE_USER"
echo "Container: $ORACLE_CONTAINER"
echo "PDB: $ORACLE_PDB"
echo ""

# Grant unlimited quota on USERS tablespace
docker exec $ORACLE_CONTAINER sqlplus -s / as sysdba <<EOF
ALTER SESSION SET CONTAINER=$ORACLE_PDB;
ALTER USER $ORACLE_USER QUOTA UNLIMITED ON USERS;
GRANT UNLIMITED TABLESPACE TO $ORACLE_USER;
GRANT RESOURCE TO $ORACLE_USER;
GRANT CONNECT TO $ORACLE_USER;
COMMIT;
EXIT;
EOF

if [ $? -eq 0 ]; then
    echo "✓ Privileges granted successfully!"
    echo ""
    echo "You can now run: make create-test-user"
else
    echo "✗ Failed to grant privileges"
    exit 1
fi
