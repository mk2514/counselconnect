# CounselConnect Database Backup and Restore Process

This document outlines the standard operating procedure (SOP) for protecting, exporting, and recovering the production PostgreSQL database.

## 1. Architecture Overview
The production database is a containerized PostgreSQL 15 instance. Data is persisted to the Docker volume `counselconnect_postgres_data`.

## 2. Automated Backups (Cron)
A cron job should be scheduled on the host machine to execute `pg_dump` daily.

**Example Backup Script (`backup.sh`):**
```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/opt/backups/counselconnect"
DB_USER="counselconnect_prod"
DB_NAME="counselconnect_prod"

mkdir -p ${BACKUP_DIR}

# Execute pg_dump against the running postgres container
docker exec counselconnect-postgres-1 pg_dump -U ${DB_USER} -F c ${DB_NAME} > ${BACKUP_DIR}/db_backup_${TIMESTAMP}.dump

# Retain only the last 30 days of backups
find ${BACKUP_DIR} -name "db_backup_*.dump" -type f -mtime +30 -exec rm {} \;
```

**Cron Installation:**
`0 2 * * * /opt/scripts/backup.sh >> /var/log/db_backup.log 2>&1`
*(Runs daily at 2:00 AM)*

## 3. Manual Backup (Ad-hoc)
To take an immediate backup before a major deployment or migration:
```bash
docker exec -t counselconnect-postgres-1 pg_dump -U counselconnect_prod -F c counselconnect_prod > ./db_backup_manual_$(date +"%Y%m%d").dump
```

## 4. Restore Procedure
> **WARNING:** Restoring a database overwrites existing data. Ensure you are restoring to the correct environment.

**Step 1: Stop Application Services**
To prevent data corruption, stop the API and Celery workers.
```bash
docker-compose -f docker-compose.prod.yml stop api worker
```

**Step 2: Drop and Recreate the Database**
```bash
docker exec -it counselconnect-postgres-1 psql -U counselconnect_prod -d postgres -c "DROP DATABASE counselconnect_prod;"
docker exec -it counselconnect-postgres-1 psql -U counselconnect_prod -d postgres -c "CREATE DATABASE counselconnect_prod;"
```

**Step 3: Run `pg_restore`**
```bash
docker exec -i counselconnect-postgres-1 pg_restore -U counselconnect_prod -d counselconnect_prod < ./db_backup_manual_20261002.dump
```

**Step 4: Restart Application Services**
```bash
docker-compose -f docker-compose.prod.yml start api worker
```

## 5. MinIO (File Storage) Backups
While PostgreSQL stores metadata, actual FIRs and Audio files are in MinIO. 
Use the `mc` (MinIO Client) tool to mirror the bucket to a cold storage solution (like AWS S3).
```bash
mc mirror counsel_prod/counselconnect-prod-data/ s3_cold_storage/counselconnect-prod-data-backup/
```
