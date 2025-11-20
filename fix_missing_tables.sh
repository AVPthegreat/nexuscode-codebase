#!/bin/bash
# Fix missing database tables
# These tables were defined in models but never created via migrations

echo "Creating missing database tables..."

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
"

echo ""
echo "Verifying tables exist..."
docker exec oj-postgres psql -U onlinejudge -d onlinejudge -c "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename IN ('contest_attempt', 'contest_attempt_problem_stat', 'discussion_message') ORDER BY tablename;"

echo ""
echo "Done! All missing tables are now created."
