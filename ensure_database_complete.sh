#!/bin/bash
# Database validation and auto-fix script
# Run this to ensure all required tables exist

set -e

echo "=== Database Completeness Check ==="
echo ""

# Function to create missing tables
create_missing_tables() {
    echo "Creating missing tables..."
    docker exec oj-postgres psql -U onlinejudge -d onlinejudge -c "
-- Contest attempt tables
CREATE TABLE IF NOT EXISTS contest_attempt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES \"user\"(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    contest_id INTEGER NOT NULL REFERENCES contest(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    attempt_no INTEGER NOT NULL DEFAULT 1,
    started BOOLEAN NOT NULL DEFAULT FALSE,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    fullscreen_exit_count INTEGER NOT NULL DEFAULT 0,
    violations JSONB NOT NULL DEFAULT '[]',
    UNIQUE (user_id, contest_id, attempt_no)
);

CREATE TABLE IF NOT EXISTS contest_attempt_problem_stat (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER NOT NULL REFERENCES contest_attempt(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    problem_id INTEGER NOT NULL REFERENCES problem(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    attempts INTEGER NOT NULL DEFAULT 0,
    best_result INTEGER NOT NULL DEFAULT 0,
    passed_cases INTEGER NOT NULL DEFAULT 0,
    total_cases INTEGER NOT NULL DEFAULT 0,
    score INTEGER NOT NULL DEFAULT 0,
    UNIQUE (attempt_id, problem_id)
);

-- Discussion table
CREATE TABLE IF NOT EXISTS discussion_message (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problem(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    user_id INTEGER NOT NULL REFERENCES \"user\"(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    username VARCHAR(32) NOT NULL,
    message TEXT NOT NULL,
    create_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS contest_attempt_user_id_idx ON contest_attempt(user_id);
CREATE INDEX IF NOT EXISTS contest_attempt_contest_id_idx ON contest_attempt(contest_id);
CREATE INDEX IF NOT EXISTS contest_attempt_started_at_idx ON contest_attempt(started_at DESC);
CREATE INDEX IF NOT EXISTS contest_attempt_problem_stat_attempt_id_idx ON contest_attempt_problem_stat(attempt_id);
CREATE INDEX IF NOT EXISTS contest_attempt_problem_stat_problem_id_idx ON contest_attempt_problem_stat(problem_id);
CREATE INDEX IF NOT EXISTS discussion_message_problem_id_idx ON discussion_message(problem_id);
CREATE INDEX IF NOT EXISTS discussion_message_user_id_idx ON discussion_message(user_id);
CREATE INDEX IF NOT EXISTS discussion_message_create_time_idx ON discussion_message(create_time DESC);
" > /dev/null 2>&1
}

# Check if required tables exist
echo "Checking required tables..."
MISSING_TABLES=$(docker exec oj-postgres psql -U onlinejudge -d onlinejudge -t -c "
SELECT COUNT(*) FROM (
    SELECT 'contest_attempt' AS tbl
    UNION ALL SELECT 'contest_attempt_problem_stat'
    UNION ALL SELECT 'discussion_message'
) required
WHERE NOT EXISTS (
    SELECT 1 FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename = required.tbl
);
" | tr -d ' ')

if [ "$MISSING_TABLES" -gt 0 ]; then
    echo "⚠️  Found $MISSING_TABLES missing table(s)"
    create_missing_tables
    echo "✅ Missing tables created"
else
    echo "✅ All required tables exist"
fi

# Verify UserProfiles exist for all users
echo ""
echo "Checking user profiles..."
docker exec oj-postgres psql -U onlinejudge -d onlinejudge -c "
INSERT INTO user_profile (
    user_id, acm_problems_status, oi_problems_status, 
    avatar, accepted_number, submission_number, total_score, real_name
)
SELECT 
    u.id, '{}', '{}', '/public/avatar/default.png', 0, 0, 0, ''
FROM \"user\" u
LEFT JOIN user_profile up ON u.id = up.user_id
WHERE up.id IS NULL;
" > /dev/null 2>&1

PROFILES_CREATED=$(docker exec oj-postgres psql -U onlinejudge -d onlinejudge -t -c "
SELECT COUNT(*) FROM \"user\" u
LEFT JOIN user_profile up ON u.id = up.user_id
WHERE up.id IS NULL;
" | tr -d ' ')

if [ "$PROFILES_CREATED" -eq 0 ]; then
    echo "✅ All users have profiles"
else
    echo "⚠️  Created $PROFILES_CREATED missing profile(s)"
fi

# Final verification
echo ""
echo "Running Django system check..."
docker exec oj-app python manage.py check 2>&1 | grep -q "identified no issues" && echo "✅ Django system check passed" || echo "⚠️  Django system check found some issues (may be warnings)"

echo ""
echo "=== Database is complete and ready ==="
