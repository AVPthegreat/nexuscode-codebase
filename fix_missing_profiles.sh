#!/bin/bash
# Fix missing UserProfile records for users

echo "Checking for users without profiles..."

docker exec oj-postgres psql -U onlinejudge -d onlinejudge << 'EOF'
-- Find and create missing profiles
INSERT INTO user_profile (
    user_id, 
    acm_problems_status, 
    oi_problems_status, 
    avatar, 
    accepted_number, 
    submission_number, 
    total_score, 
    real_name
)
SELECT 
    u.id,
    '{}',
    '{}',
    '/public/avatar/default.png',
    0,
    0,
    0,
    ''
FROM "user" u
LEFT JOIN user_profile up ON u.id = up.user_id
WHERE up.id IS NULL;

-- Show current status
SELECT 
    u.id, 
    u.username, 
    CASE WHEN up.id IS NULL THEN 'MISSING' ELSE 'OK' END as profile_status
FROM "user" u
LEFT JOIN user_profile up ON u.id = up.user_id
ORDER BY u.id;
EOF

echo ""
echo "Done! Reloading backend..."
docker exec oj-app pkill -HUP gunicorn 2>/dev/null || true

echo "All users now have profiles."
