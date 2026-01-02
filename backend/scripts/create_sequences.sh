#!/bin/bash
# Script to create Oracle sequences for auto-increment IDs
# Usage: ./create_sequences.sh

ORACLE_CONTAINER="${ORACLE_CONTAINER:-unified-portal-oracle}"
ORACLE_PDB="${ORACLE_PDB:-XEPDB1}"
ORACLE_USER="${ORACLE_USER:-umduser}"
ORACLE_PASSWORD="${ORACLE_PASSWORD:-umd123}"

echo "Creating sequences for Oracle auto-increment IDs..."
echo "Container: $ORACLE_CONTAINER"
echo "PDB: $ORACLE_PDB"
echo "User: $ORACLE_USER"
echo ""

# Create sequences with error handling
docker exec $ORACLE_CONTAINER sqlplus -s $ORACLE_USER/$ORACLE_PASSWORD@$ORACLE_PDB <<EOF
-- Create sequences if they don't exist
BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created users_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('users_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE catalogue_categories_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created catalogue_categories_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('catalogue_categories_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE catalogues_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created catalogues_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('catalogues_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE roles_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created roles_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('roles_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE permissions_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created permissions_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('permissions_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE user_role_mapping_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created user_role_mapping_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('user_role_mapping_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'CREATE SEQUENCE catalogue_permissions_seq START WITH 1 INCREMENT BY 1 NOCACHE';
  DBMS_OUTPUT.PUT_LINE('Created catalogue_permissions_seq');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE = -955 THEN 
      DBMS_OUTPUT.PUT_LINE('catalogue_permissions_seq already exists');
    ELSE 
      RAISE;
    END IF;
END;
/

COMMIT;

-- Verify sequences exist
SET SERVEROUTPUT ON
SELECT 'Verifying sequences...' FROM DUAL;
SELECT sequence_name FROM user_sequences ORDER BY sequence_name;

EXIT;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Sequences created/verified successfully!"
    echo ""
    echo "You can now run: make create-test-user"
else
    echo "✗ Failed to create sequences"
    exit 1
fi
