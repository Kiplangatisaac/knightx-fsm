# KnightX_fsm - Database Schema & Implementation Details

## Overview

KnightX_fsm uses **SQLite** as its primary database with **WAL (Write-Ahead Logging)** journal mode for consistency and concurrent access. All sensitive data (passwords, encryption keys) is protected using industry-standard cryptography.

**Database Location:** `data/knightx_fsm.db`

---

## Database Tables

### 1. `users` - User Accounts

Stores user authentication and profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user ID |
| `username` | TEXT | UNIQUE NOT NULL | Login username |
| `password_hash` | TEXT | NOT NULL | bcrypt-hashed password |
| `email` | TEXT | NULLABLE | User email address |
| `role` | TEXT | DEFAULT 'user' | User role (admin/user) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| `last_login` | TIMESTAMP | NULLABLE | Last successful login |
| `is_active` | INTEGER | DEFAULT 1 | Account active status (0=disabled) |

**Security:** Passwords hashed with bcrypt (12 rounds). Never stored in plaintext.

**Default Admin User:**
- Username: `admin`
- Password: `KnightX@2026!` (change immediately)
- Role: `admin`

---

### 2. `file_metadata` - Scanned File Information

Stores metadata about files discovered during directory scans.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `path` | TEXT | NOT NULL | Parent directory path |
| `name` | TEXT | NOT NULL | File/directory name |
| `size` | INTEGER | NOT NULL | File size in bytes |
| `file_type` | TEXT | NULLABLE | File extension (e.g., .pdf) |
| `mime_type` | TEXT | NULLABLE | MIME type (e.g., application/pdf) |
| `sha256` | TEXT | NULLABLE | SHA-256 hash (for duplicate detection) |
| `is_duplicate` | INTEGER | DEFAULT 0 | 1 if file is a duplicate |
| `is_junk` | INTEGER | DEFAULT 0 | 1 if file is identified as junk |
| `risk_score` | REAL | DEFAULT 0.0 | AI risk score (0.0-1.0) |
| `last_scanned` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last scan timestamp |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:** Queries optimized by path, sha256, is_duplicate, is_junk.

---

### 3. `scan_history` - Scan Operation History

Records all scan operations performed by the application.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `scan_type` | TEXT | NOT NULL | Type: directory, virus, junk, duplicate, usb |
| `target_path` | TEXT | NULLABLE | Path that was scanned |
| `files_scanned` | INTEGER | DEFAULT 0 | Number of files scanned |
| `threats_found` | INTEGER | DEFAULT 0 | Threats detected (virus scans) |
| `duplicates_found` | INTEGER | DEFAULT 0 | Duplicate files found |
| `junk_found` | INTEGER | DEFAULT 0 | Junk files found |
| `space_recovered` | INTEGER | DEFAULT 0 | Bytes freed by cleaning |
| `status` | TEXT | DEFAULT 'completed' | Scan status (completed/failed/cancelled) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Scan start time |

---

### 4. `usb_devices` - USB Device Registry

Tracks connected USB storage devices.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `device_name` | TEXT | NULLABLE | Device identifier (e.g., /dev/sdb1) |
| `device_path` | TEXT | NULLABLE | Mount point (e.g., /media/usb) |
| `serial_number` | TEXT | NULLABLE | Device serial number |
| `vendor_id` | TEXT | NULLABLE | USB vendor ID |
| `product_id` | TEXT | NULLABLE | USB product ID |
| `size` | INTEGER | DEFAULT 0 | Device total size in bytes |
| `first_seen` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | First detection time |
| `last_seen` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Most recent detection |
| `scan_status` | TEXT | DEFAULT 'pending' | Scan status (pending/completed/infected) |
| `threats_found` | INTEGER | DEFAULT 0 | Threats found on device |

---

### 5. `activity_log` - Audit Trail

Records all user actions for security auditing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `user_id` | INTEGER | FK → users.id | User who performed the action |
| `action` | TEXT | NOT NULL | Action description (e.g., "login", "delete_file") |
| `details` | TEXT | NULLABLE | Additional action details |
| `ip_address` | TEXT | NULLABLE | Client IP address |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Action time |

**Foreign Key:** `user_id` references `users(id)` with ON DELETE SET NULL.

---

### 6. `system_metrics` - System Performance Snapshots

Stores system resource usage over time.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `cpu_percent` | REAL | NULLABLE | CPU usage percentage |
| `memory_percent` | REAL | NULLABLE | Memory usage percentage |
| `disk_percent` | REAL | NULLABLE | Disk usage percentage |
| `network_sent` | INTEGER | DEFAULT 0 | Bytes sent (network) |
| `network_recv` | INTEGER | DEFAULT 0 | Bytes received (network) |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Snapshot time |

---

## Security Implementation

### Password Hashing

```python
# bcrypt with 12 rounds
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
verified = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
```

### Data Encryption

All sensitive fields use **Fernet (AES-128 in CBC mode with HMAC-SHA256)**:

- Encryption key stored at `data/.encryption_key` with `600` permissions
- Key auto-generated on first run if missing
- Used for encrypting any sensitive configuration data

### Database Integrity

- **WAL journal mode** for concurrent read/write access
- **Foreign key constraints** enforced via `PRAGMA foreign_keys = ON`
- **Parameterized queries** throughout - no SQL injection vulnerability
- **Connection context managers** with automatic rollback on error

---

## Data Operations

### User Management

```python
# Create user
db.create_user(username, password, email, role)

# Authenticate
user = db.authenticate_user(username, password)

# Get user
user = db.get_user_by_id(user_id)
```

### File Metadata

```python
# Insert file record
file_id = db.insert_file_metadata({
    'path': '/home/user/documents',
    'name': 'report.pdf',
    'size': 102400,
    'file_type': '.pdf',
    'mime_type': 'application/pdf',
    'sha256': 'abc123...',
    'is_duplicate': 0,
    'is_junk': 0,
    'risk_score': 0.1,
})

# Get duplicates
duplicates = db.get_duplicates()

# Get junk files
junk = db.get_junk_files()
```

### Scan History

```python
# Record scan
db.insert_scan_history({
    'scan_type': 'virus',
    'target_path': '/home/user',
    'files_scanned': 500,
    'threats_found': 2,
    'status': 'completed',
})

# Get history
history = db.get_scan_history(limit=50)
```

### Activity Logging

```python
# Log user action
db.log_activity(user_id, 'login', 'User logged in from 192.168.1.100')

# Get activity log
logs = db.get_activity_log(limit=100)
```

---

## Implementation Details

### Connection Management

All database operations use `DatabaseManager.get_connection()` context manager:

```python
with db.get_connection() as conn:
    conn.execute("INSERT INTO ...")
    conn.commit()  # Auto-committed on success
# Auto-rollback on exception
```

### Initialization

On first run, the database is automatically created with all tables and a default admin user. The encryption key is also generated.

### Migrations

Schema changes are handled by updating `config.py` TABLES definitions. For production migrations, use Alembic or manual SQL scripts.

---

## Sample Queries

```sql
-- Find all duplicate files
SELECT * FROM file_metadata WHERE is_duplicate = 1;

-- Find total junk size
SELECT SUM(size) FROM file_metadata WHERE is_junk = 1;

-- Recent activity
SELECT al.timestamp, u.username, al.action 
FROM activity_log al 
JOIN users u ON al.user_id = u.id 
ORDER BY al.timestamp DESC LIMIT 20;

-- Scan history summary
SELECT scan_type, COUNT(*) as count, SUM(threats_found) as total_threats
FROM scan_history 
GROUP BY scan_type;
```
