#!/bin/bash
set -e

export $(grep -v '^#' .env | xargs)

sudo systemctl start mysql || sudo systemctl start mariadb

sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < db/migrations/001_surface_tables.sql

echo "Done"