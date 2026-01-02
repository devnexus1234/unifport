-- Grant tablespace quota to Oracle user
-- This fixes ORA-01950: no privileges on tablespace 'USERS'

-- Connect as sysdba and run these commands
-- For Docker Oracle XE container, connect as: sys/Oracle18@XEPDB1 as sysdba

-- Grant unlimited quota on USERS tablespace
ALTER USER umduser QUOTA UNLIMITED ON USERS;

-- Also grant RESOURCE role if not already granted (includes tablespace privileges)
GRANT RESOURCE TO umduser;

-- Grant CONNECT role if not already granted
GRANT CONNECT TO umduser;

-- Grant CREATE TABLE, CREATE SEQUENCE, etc. (usually included in RESOURCE, but explicit is better)
GRANT CREATE TABLE TO umduser;
GRANT CREATE SEQUENCE TO umduser;
GRANT CREATE VIEW TO umduser;
GRANT CREATE PROCEDURE TO umduser;

-- Commit the changes
COMMIT;
