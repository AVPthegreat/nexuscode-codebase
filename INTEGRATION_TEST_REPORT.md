# Integration Test Report
**Date:** November 4, 2025  
**Features Tested:** Editorial System, Dark Mode, Frozen Scoreboard  
**Status:** In Progress

---

## Test Environment
- **Backend:** http://localhost:8000 (Django + PostgreSQL)
- **Frontend:** http://localhost:8080 (Vue.js)
- **Database:** PostgreSQL 10
- **Test Problems:** CB101, CB102 (3 problems available)
- **Test Contests:** 3 contests available

---

## Feature 1: Dark Mode

### Test Case 1.1: Dark Mode Toggle Visibility
**Steps:**
1. Open http://localhost:8080
2. Look for sun/moon icon in navbar

**Expected Result:**
- Theme toggle button should be visible in the navbar
- Icon should show moon (🌙) for light mode or sun (☀️) for dark mode

**Status:** ⏳ Pending

---

### Test Case 1.2: Dark Mode Activation
**Steps:**
1. Click the theme toggle button
2. Observe page appearance change

**Expected Result:**
- Background should turn dark (#1a1a1a)
- Text should turn light (#e0e0e0)
- All UI components should update colors
- Smooth transition without page reload

**Status:** ⏳ Pending

---

### Test Case 1.3: Dark Mode Persistence
**Steps:**
1. Enable dark mode
2. Refresh the page (F5)
3. Navigate to different pages

**Expected Result:**
- Dark mode should remain active after refresh
- Theme should persist across all pages
- localStorage should contain 'theme: dark'

**Status:** ⏳ Pending

---

### Test Case 1.4: Dark Mode Components Coverage
**Steps:**
1. Enable dark mode
2. Visit these pages:
   - Home page
   - Problem list (/problem)
   - Contest list (/contest)
   - Submission status (/status)
   - Rank pages
   - Problem detail page

**Expected Result:**
- All pages should render correctly in dark mode
- No white backgrounds or unreadable text
- Cards, tables, forms all have proper dark styling

**Status:** ⏳ Pending

---

## Feature 2: Editorial System

### Test Case 2.1: Editorial Button Visibility
**Steps:**
1. Navigate to problem detail page: http://localhost:8080/problem/CB101
2. Scroll to bottom of problem description
3. Look for "Editorial" section

**Expected Result:**
- Editorial section should be visible
- "View Editorial" button should be present
- No editorial content shown initially

**Status:** ⏳ Pending

---

### Test Case 2.2: Editorial Permission - Unsolved Problem
**Steps:**
1. As a logged-out or non-solving user
2. Navigate to a problem page
3. Click "View Editorial" button

**Expected Result:**
- Warning message: "You need to solve this problem first to view the editorial, or wait for the contest to end."
- Editorial content NOT displayed
- HTTP 403 response expected

**Status:** ⏳ Pending

---

### Test Case 2.3: Add Editorial via Admin Panel
**Steps:**
1. Login as admin
2. Navigate to admin panel: http://localhost:8080/admin
3. Edit problem CB101
4. Add editorial content with rich text
5. Save problem

**Expected Result:**
- Editorial field should be available in problem edit form
- Rich text editor should work
- Editorial saved successfully to database

**Status:** ⏳ Pending

---

### Test Case 2.4: Editorial Access After Solving
**Steps:**
1. Submit correct solution to problem
2. Get Accepted (AC) status
3. Return to problem page
4. Click "View Editorial"

**Expected Result:**
- Editorial content loads successfully
- Editorial displayed in a card
- Rich text formatting preserved
- No permission error

**Status:** ⏳ Pending

---

### Test Case 2.5: Editorial API Response
**Steps:**
1. Make API call: GET /api/problem/editorial/?problem_id=1
2. Check response format

**Expected Result:**
```json
{
  "editorial": "<p>Editorial content here</p>",
  "problem_id": 1,
  "problem_title": "Hello Codebase"
}
```

**Status:** ⏳ Pending

---

## Feature 3: Frozen Scoreboard

### Test Case 3.1: Set Freeze Time
**Steps:**
1. Access database: `docker exec -it oj-postgres psql -U onlinejudge -d onlinejudge`
2. Update contest freeze time:
   ```sql
   UPDATE contest 
   SET freeze_time = NOW() - INTERVAL '1 hour'
   WHERE id = 2;
   ```
3. Verify:
   ```sql
   SELECT title, freeze_time, end_time FROM contest WHERE id = 2;
   ```

**Expected Result:**
- freeze_time should be set to 1 hour ago
- Contest should be in "frozen" state

**Status:** ⏳ Pending

---

### Test Case 3.2: Freeze Banner Visibility (Non-Admin)
**Steps:**
1. Logout or use non-admin account
2. Navigate to contest rank page
3. Check for freeze banner

**Expected Result:**
- Alert banner should appear at top of scoreboard
- Message: "Scoreboard is frozen! Submissions after [TIME] are hidden until the contest ends."
- Snow icon (❄️) should be visible

**Status:** ⏳ Pending

---

### Test Case 3.3: Frozen Submissions Display
**Steps:**
1. View frozen scoreboard as non-admin
2. Check problem columns for submissions after freeze_time

**Expected Result:**
- Submissions made after freeze_time show "?" icon
- AC time and error count hidden
- Pending/frozen indicator displayed
- No detailed submission info visible

**Status:** ⏳ Pending

---

### Test Case 3.4: Admin Override
**Steps:**
1. Login as admin
2. Navigate to same frozen contest rank page
3. Check problem columns

**Expected Result:**
- NO freeze banner shown to admin
- All submission details visible including frozen ones
- Full scoreboard data accessible
- Admin can see complete standings

**Status:** ⏳ Pending

---

### Test Case 3.5: Freeze State After Contest End
**Steps:**
1. Update contest end_time to past:
   ```sql
   UPDATE contest 
   SET end_time = NOW() - INTERVAL '1 minute'
   WHERE id = 2;
   ```
2. Refresh scoreboard page

**Expected Result:**
- Freeze banner should disappear
- All submissions now visible to everyone
- `is_frozen` property returns false
- Full standings revealed

**Status:** ⏳ Pending

---

## Cross-Feature Tests

### Test Case 4.1: Dark Mode + Editorial
**Steps:**
1. Enable dark mode
2. View a problem with editorial
3. Load editorial content

**Expected Result:**
- Editorial card has dark background
- Editorial text is readable (light color)
- Rich text formatting preserved in dark theme

**Status:** ⏳ Pending

---

### Test Case 4.2: Dark Mode + Frozen Scoreboard
**Steps:**
1. Enable dark mode
2. View frozen scoreboard

**Expected Result:**
- Freeze alert banner styled correctly in dark mode
- Scoreboard table readable
- Frozen indicators visible
- No color contrast issues

**Status:** ⏳ Pending

---

## Database Verification

### Check Editorial Column
```sql
SELECT id, title, editorial IS NOT NULL as has_editorial 
FROM problem 
LIMIT 5;
```

**Expected:** Editorial column exists and accepts NULL values

---

### Check Freeze Time Column
```sql
SELECT id, title, freeze_time, 
       CASE 
         WHEN freeze_time IS NULL THEN 'No freeze'
         WHEN NOW() < freeze_time THEN 'Not frozen yet'
         WHEN NOW() >= freeze_time AND NOW() < end_time THEN 'FROZEN'
         ELSE 'Contest ended'
       END as freeze_status
FROM contest;
```

**Expected:** freeze_time column exists and freeze logic works

---

## Manual Testing Checklist

### Dark Mode
- [ ] Toggle appears in navbar (both logged in/out)
- [ ] Click toggles theme instantly
- [ ] Theme persists after page reload
- [ ] All pages support dark mode
- [ ] No UI breaking issues
- [ ] Icons change (moon ↔ sun)

### Editorial System
- [ ] Editorial section appears on problem pages
- [ ] "View Editorial" button works
- [ ] Permission error shows for unsolved problems
- [ ] Editorial loads for solved problems
- [ ] Admin can add/edit editorials
- [ ] Rich text formatting works
- [ ] API returns correct data

### Frozen Scoreboard
- [ ] freeze_time can be set via admin/SQL
- [ ] Freeze banner shows during freeze period
- [ ] Submissions after freeze show "?"
- [ ] Admin sees full data
- [ ] Non-admin sees frozen data
- [ ] Both ACM and OI contests support freeze
- [ ] Freeze ends when contest ends

---

## Known Issues
*(To be filled during testing)*

---

## Test Results Summary
- **Total Test Cases:** 15
- **Passed:** 0
- **Failed:** 0
- **Pending:** 15
- **Blocked:** 0

---

## Next Steps
1. Execute manual tests via web browser
2. Document results for each test case
3. Fix any discovered issues
4. Perform regression testing
5. Mark feature as production-ready

---

## Notes
- Frontend running on http://localhost:8080
- Backend running on http://localhost:8000
- All servers healthy and responsive
- Database schema updated successfully
