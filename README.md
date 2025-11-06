
# Nexus Code by avpthegreat

Welcome to **Nexus Code**, a startup idea by avpthegreat. Nexus Code is a next-generation online judge platform designed to gamify the coding experience and offer SaaS solutions to colleges and universities. Our mission is to help institutions transition from pen-and-paper CS exams to a modern, engaging, and fair digital environment for students.

---

---

## Features

- **Contest Types:**
  - **ACM (ICPC):** Only fully correct solutions are accepted (AC). No partial credit.
  - **OI (Olympiad):** Partial scoring per test case. Each passed test case earns points.
- **Submission Results:**
  - **AC (Accepted):** Solution passed all test cases.
  - **WA (Wrong Answer):** Solution failed at least one test case.
  - **PC (Partial Correct):** (OI only) Some test cases passed, some failed.
- **User Authentication:**
  - Registration, login, password reset, and email verification.
  - Two-factor authentication (2FA) support.
- **Proctoring:**
  - Fullscreen enforcement during contests.
  - Tracks and warns on fullscreen exits; auto-submits after repeated violations.
  - Admin panel for real-time monitoring.
- **Contest Result Emails:**
  - After contest ends, users receive a summary of their results via email.
- **Admin Tools:**
  - Contest management, announcements, user management, and bulk result mailing.
- **Extensible API:**
  - RESTful endpoints for all major actions.

---

## How It Works

### Contest Flow
1. **User registers and verifies email.**
2. **User joins a contest (ACM or OI).**
3. **Submits solutions:**
   - ACM: Only AC counts.
   - OI: Partial scores possible.
4. **Proctoring active:**
   - Must stay in fullscreen.
   - Exiting fullscreen triggers warnings and is logged.
5. **After contest:**
   - Results are emailed to participants.
   - Admin can view all attempts and violations.

### Email Services
- **Authentication:**
  - Email verification after registration.
  - Password reset emails.
- **Contest Results:**
  - Automated summary sent to each participant after contest.

---

## Setup Guide

### 1. Install Dependencies
```bash
cd OnlineJudge
python3 -m venv venv
source venv/bin/activate
pip install -r deploy/requirements.txt
```

### 2. Configure SMTP (for email)
Set up SMTP via the admin API or Django admin panel. Example config:
```json
{
  "server": "smtp.gmail.com",
  "port": 587,
  "email": "youracct@gmail.com",
  "password": "app_password",
  "tls": true
}
```

### 3. Run Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 4. Start Dramatiq Worker (for async emails)
```bash
dramatiq OnlineJudge.account.tasks
```

### 5. Start the Server
```bash
python3 manage.py runserver
```

---

## API Endpoints (Highlights)
- `/api/register` — User registration
- `/api/verify_email` — Email verification
- `/api/apply_reset_password` — Request password reset
- `/api/contest/start` — Start contest
- `/api/contest/stop` — Stop contest
- `/api/contest/proctor` — Log proctoring events
- `/api/admin/contest/send_results` — Admin: send contest result emails

---


## Branding & Startup Vision
**Nexus Code** is powered by avpthegreat. Our vision is to:
- Gamify the coding experience for students and professionals
- Offer SaaS to colleges for digital CS exams, replacing pen-and-paper with a better, fairer, and more engaging platform
- Provide real-time proctoring, contest management, and automated feedback

---

## File Structure Overview
- `OnlineJudge/` — Django backend
  - `account/` — User management, authentication, email
  - `contest/` — Contest logic, attempts, proctoring
  - `utils/mail.py` — Email utilities
  - `account/templates/` — Email HTML templates
- `OnlineJudgeFE/` — Frontend (Vue.js)

---

## Contact & Support
For issues, feature requests, or support, contact the **avpthegreat** team.

---


## License
**Proprietary – All rights reserved.**

This software and its source code are proprietary to avpthegreat and Nexus Code. Unauthorized copying, distribution, modification, or use of this software, in whole or in part, is strictly prohibited.

This software is provided for demonstration and evaluation purposes only. Commercial use, redistribution, or deployment is not permitted without explicit written permission from avpthegreat.

For licensing inquiries, partnership, or SaaS offerings, contact avpthegreat directly.

---

## Credits
Developed and maintained by **avpthegreat** for Nexus Code.
