# Database Schema Fixes - PERMANENT

## What Was Wrong
The database was missing 3 tables that were defined in Django models but never created:
1. `contest_attempt` - tracks user contest attempts
2. `contest_attempt_problem_stat` - tracks problem stats within contests
3. `discussion_message` - stores problem discussion messages

Additionally, some users were missing `user_profile` records.

## What Was Fixed (PERMANENTLY)

### 1. Created Missing Tables
All three tables now exist in the PostgreSQL database located at:
```
OnlineJudge/data/postgres/
```

This directory is **mounted as a volume** in docker-compose.yml, meaning:
- Data persists across container restarts
- Tables will remain even if you restart Docker
- Database is stored on your local filesystem

### 2. Updated Code to Handle Missing Data
- Modified `UserAdminSerializer` to gracefully handle missing profiles
- Modified `UserAdminAPI.delete()` to properly delete submissions before users

### 3. Created Auto-Validation Scripts

#### `ensure_database_complete.sh`
- Checks for missing tables and creates them if needed
- Checks for missing user profiles and creates them
- Runs automatically on every startup

#### `fix_missing_profiles.sh`
- Manual script to fix missing user profiles

#### `fix_missing_tables.sh`  
- Manual script to create missing tables

### 4. Integrated Into Startup
The `startup.sh` script now:
1. Starts containers
2. **Automatically runs database validation**
3. Creates any missing tables
4. Creates any missing user profiles
5. Verifies system health

## Why This Is Permanent

1. **Database is on persistent storage**: `./OnlineJudge/data/postgres:/var/lib/postgresql/data`
2. **Tables use standard PostgreSQL**: No temporary tables
3. **Code changes committed**: Serializer and delete function are fixed
4. **Auto-validation on startup**: Every time you run `./startup.sh`, database integrity is checked

## Verification

Run this to verify everything is permanent:
```bash
docker exec oj-postgres psql -U onlinejudge -d onlinejudge -c "
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('contest_attempt', 'contest_attempt_problem_stat', 'discussion_message')
ORDER BY tablename;
"
```

Should output:
```
 contest_attempt
 contest_attempt_problem_stat
 discussion_message
```

## What Happens on Container Restart

1. You run `./startup.sh`
2. Containers start
3. Database loads from `OnlineJudge/data/postgres/` (persistent)
4. All tables are already there (permanent)
5. Validation script confirms everything is OK

**NO DATA IS LOST. NO TABLES DISAPPEAR.**

## If You Ever Need to Reset

If you want to completely reset the database (you probably don't):
```bash
docker compose down
rm -rf OnlineJudge/data/postgres/
docker compose up -d
# Then run migrations
```

But you **DON'T need to do this** - everything is already fixed and permanent.

---
**Date Fixed**: November 18, 2025
**Fixed By**: Automated database validation system
**Status**: ✅ PERMANENT
