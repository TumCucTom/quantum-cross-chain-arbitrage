-- Ensure the database exists
CREATE DATABASE IF NOT EXISTS ETHDB;

-- Ensure the user exists
CREATE USER IF NOT EXISTS 'general-user'@'%' IDENTIFIED BY 'mypassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON ETHDB.* TO 'general-user'@'%';
FLUSH PRIVILEGES;
