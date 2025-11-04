# Data Storage Guide - Codebase Judge System

## Your Account Information

### User: `avpthegreat`
- **Email**: anantwebsites@gmail.com
- **Created**: October 30, 2025 at 05:43:19 UTC
- **User ID**: 2
- **Avatar**: `/public/avatar/203d0185d4.png`

---

## Where Your Data is Stored

### 1. **Database (PostgreSQL)** ✅ PERSISTENT
All your account credentials and metadata are stored in PostgreSQL database.

**Location**: 
- Container: `/var/lib/postgresql/data`
- Host (Your Mac): `./OnlineJudge/data/postgres/`

**What's stored**:
- ✅ Username: `avpthegreat`
- ✅ Email: `anantwebsites@gmail.com`
- ✅ Password: Hashed (bcrypt/PBKDF2 - secure, not reversible)
- ✅ Profile data (mood, bio, etc.)
- ✅ Avatar file path: `/public/avatar/203d0185d4.png`
- ✅ All submissions you make
- ✅ Problem attempts, scores, rankings
- ✅ Contest participations

**Database Tables**:
```
user              - Your account credentials
user_profile      - Your profile info & avatar path
submission        - All your code submissions
```

---

### 2. **File Storage (Avatar & Uploads)** ✅ PERSISTENT

Your uploaded avatar image is stored as a **real file** on disk.

**Avatar Location**:
- Container: `/data/public/avatar/203d0185d4.png`
- Host (Your Mac): `./OnlineJudge/data/public/avatar/203d0185d4.png`

**File Details**:
- Filename: `203d0185d4.png` (random hash generated on upload)
- Size: ~149 KB
- Format: PNG image
- Accessible at: `http://localhost:8000/public/avatar/203d0185d4.png`

**Other file storage directories**:
```
OnlineJudge/data/
├── public/
│   ├── avatar/          ← Your avatar & all user avatars
│   ├── upload/          ← Any file uploads (images in problem descriptions, etc.)
│   └── website/         ← Website assets (logos, banners)
├── test_case/           ← Problem test cases
├── log/                 ← System logs
└── backend/             ← Misc backend data
```

---

### 3. **Session Storage (Redis Cache)** ⚠️ TEMPORARY

Your login session is stored in Redis for performance.

**Location**: 
- Container: Redis in-memory
- Host: `./OnlineJudge/data/redis/`

**What's stored**:
- ✅ Session token (so you stay logged in)
- ✅ Temporary cache data
- ⚠️ **NOT permanent** - if Redis restarts, you'll need to log in again

---

### 4. **Browser Storage** ⚠️ LOCAL ONLY

Some UI preferences are stored in your browser.

**LocalStorage**:
- Theme preference (if you enable dark mode in future)
- UI state (sidebar collapsed, etc.)
- ⚠️ **Only on your computer** - not synced to server

**Cookies**:
- `csrftoken` - Security token
- `sessionid` - Login session
- ⚠️ **Temporary** - deleted when you clear cookies

---

## What Happens When You Deploy to Digital Ocean or Other Cloud?

### ✅ Data That WILL Transfer:

1. **Database (PostgreSQL)** ✅
   - All user accounts
   - All submissions
   - All problems, contests, rankings
   - **How**: Copy `./OnlineJudge/data/postgres/` folder OR export/import SQL dump

2. **Uploaded Files** ✅
   - All avatars (including yours: `203d0185d4.png`)
   - All uploaded images/files
   - **How**: Copy `./OnlineJudge/data/public/` folder

3. **Test Cases** ✅
   - All problem test cases
   - **How**: Copy `./OnlineJudge/data/test_case/` folder

### ⚠️ Data That WON'T Transfer Automatically:

1. **Redis Cache** ⚠️
   - Sessions will be reset
   - Users need to log in again
   - **Not a problem**: Redis is meant to be temporary

2. **Browser LocalStorage/Cookies** ⚠️
   - UI preferences won't carry over
   - **Not a problem**: Users set preferences per device

---

## How to Backup Your Data

### Quick Backup Commands:

```bash
# Backup database
docker compose exec postgres pg_dump -U onlinejudge onlinejudge > backup.sql

# Backup all data folders
tar -czf onlinejudge_data_backup.tar.gz OnlineJudge/data/

# Restore database
cat backup.sql | docker compose exec -T postgres psql -U onlinejudge onlinejudge
```

---

## Deployment Checklist for Digital Ocean/Cloud

When you deploy to production:

### ✅ Must Transfer:
1. Copy `OnlineJudge/data/postgres/` → Your cloud server
2. Copy `OnlineJudge/data/public/` → Your cloud server (or use S3/object storage)
3. Copy `OnlineJudge/data/test_case/` → Your cloud server
4. Update `docker-compose.yml` with production settings
5. Set environment variables (database password, secret keys)

### ✅ Your Account Will Work:
- ✅ Username: `avpthegreat`
- ✅ Email: `anantwebsites@gmail.com`
- ✅ Password: Same (stored securely hashed)
- ✅ Avatar: `203d0185d4.png` (if you copy the files)
- ✅ All submissions and progress

### ⚠️ You'll Need to Redo:
- Log in again (new session)
- Set UI preferences again (local storage is per-browser)

---

## Storage Architecture Diagram

```
┌─────────────────────────────────────────┐
│  PostgreSQL Database (PERSISTENT)       │
│  Location: ./OnlineJudge/data/postgres/ │
│                                          │
│  ✓ Credentials (username, email, pass)  │
│  ✓ User profiles                         │
│  ✓ Submissions, rankings                 │
│  ✓ Problems, contests                    │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│  File System (PERSISTENT)                │
│  Location: ./OnlineJudge/data/public/    │
│                                          │
│  ✓ Avatar: 203d0185d4.png               │
│  ✓ Other uploads                         │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│  Redis Cache (TEMPORARY)                 │
│  Location: In-memory + ./data/redis/     │
│                                          │
│  ✓ Session tokens                        │
│  ✓ Temporary cache                       │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│  Browser (LOCAL ONLY)                    │
│  Location: Your computer only            │
│                                          │
│  ✓ UI preferences                        │
│  ✓ Dark mode toggle (future)             │
└─────────────────────────────────────────┘
```

---

## Summary

### Your Data is Stored in:

1. **PostgreSQL Database** (`./OnlineJudge/data/postgres/`)
   - Username, email, hashed password
   - All your activity and submissions

2. **File System** (`./OnlineJudge/data/public/avatar/203d0185d4.png`)
   - Your uploaded avatar image

3. **Redis** (temporary session storage)
   - Login session (temporary)

### When You Deploy:

✅ **YES** - All your data transfers if you:
   - Copy the database folder
   - Copy the public/avatar folder
   - OR export/import the database

✅ **YES** - Your account, avatar, and all activity will be preserved

⚠️ **NO** - You won't lose data, but you'll need to:
   - Log in again on the new server
   - Set UI preferences again

---

## Verify Your Data Now

Run these commands to see your data:

```bash
# See your account in database
docker compose exec postgres psql -U onlinejudge -d onlinejudge -c "SELECT * FROM \"user\" WHERE username='avpthegreat';"

# See your avatar file
ls -lah OnlineJudge/data/public/avatar/203d0185d4.png

# View your avatar in browser
open http://localhost:8000/public/avatar/203d0185d4.png
```

Your data is safe and persistent! 🎯
