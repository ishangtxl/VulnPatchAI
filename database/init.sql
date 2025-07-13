-- Initialize VulnPatch AI Database

-- Create database and user
CREATE DATABASE vulnpatch_db;
CREATE USER vulnpatch WITH PASSWORD 'vulnpatch';
GRANT ALL PRIVILEGES ON DATABASE vulnpatch_db TO vulnpatch;

-- Connect to the database
\c vulnpatch_db;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO vulnpatch;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vulnpatch;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vulnpatch;