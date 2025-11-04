# Local setup and fixes (macOS, Docker Desktop)

This repo contains three services: OnlineJudge (Django backend), JudgeServer, and the FE. These notes document the fixes applied to run everything end-to-end on macOS (Apple Silicon) and how to verify.

## Summary of changes

- Judge test case mount
  - JudgeServer must mount the backend test cases directory: `./OnlineJudge/data/backend/test_case -> /test_case:ro`.
- Native ARM JudgeServer image
  - Built a local ARM64 JudgeServer image from source to avoid Rosetta/QEMU errors (mmap failures).
  - Switched base image to Debian bookworm and used generic packages for Python/gcc/g++/node/JDK.
- Docker security on macOS
  - Docker Desktop has limitations around seccomp. To allow libjudger to load sandbox filters, the JudgeServer runs with:
    - `security_opt: ["seccomp:unconfined"]`
    - `cap_add: ["SYS_PTRACE"]`
    - `privileged: true` (macOS-only workaround; remove or tighten on Linux servers).

## Files changed

- `docker-compose.yml`
  - JudgeServer uses local image `oj-judge-server:local`.
  - Volumes: `./OnlineJudge/data/backend/test_case:/test_case:ro` and `./OnlineJudge/data/log:/log`.
  - Security options as above.
- `JudgeServer/Dockerfile`
  - Fixed COPY path when building from repo root.
  - Switched to bookworm base and generic packages; builds python venv and libjudger.
- `OnlineJudge/judge/dispatcher.py`
  - Clear `statistic_info.err_info` on successful judge to prevent stale error messages in UI.

## Build and run

```bash
# From repo root
# 1) Build native JudgeServer image (ARM64 on Apple Silicon)
docker build -f JudgeServer/Dockerfile -t oj-judge-server:local .

# 2) Start stack
docker compose up -d

# 3) (Optional) Restart only judge-server after changes
docker compose up -d judge-server
```

## Verify JudgeServer

```bash
# From host: judge-server ping (token is sha256 of CHANGE_THIS)
curl -s -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-Judge-Server-Token: b824cecedb22b06c3883b1f1dd9dd3150608fc24f8d0c16b0f85af8c8c761667' \
  http://localhost:12358/ping
```

Expected: a JSON with `{"err": null, "data": { ..., "action": "pong" }}`

## Re-enqueue a submission (quick smoke test)

```bash
# Inside backend container
docker exec -it oj-backend sh -lc \
  "python3 manage.py shell -c 'from submission.models import Submission; from judge.tasks import judge_task; s=Submission.objects.order_by(\"-create_time\").first(); print(s.id, s.language); judge_task.send(s.id, s.problem.id); print(\"enqueued\")'"

# Tail logs on host
tail -n 200 OnlineJudge/data/log/gunicorn.log
tail -n 200 OnlineJudge/data/log/compile.log
tail -n 200 OnlineJudge/data/log/judger.log
```

Expected: submission transitions to JUDGING then ACCEPTED; compile/run logs show no Rosetta or seccomp errors.

## Known macOS notes

- `privileged: true` is added only to work around Docker Desktop’s seccomp limitations on macOS. If you deploy on Linux, remove `privileged` and try keeping only `security_opt: seccomp:unconfined` (or a minimal custom seccomp profile).
- With the volume fix, test cases must exist in `./OnlineJudge/data/backend/test_case/<case_id>` and include an `info` file plus `N.in`/`N.out` pairs.
- After a successful judge, old `statistic_info.err_info` values are cleared automatically.

## Language Configuration Fixes

The platform supports multiple programming languages, each requiring specific compiler/interpreter configuration. This section documents all language fixes applied to ensure multi-language support.

### Configuration Storage

Language configurations are stored in two places:
1. **Source code**: `OnlineJudge/judge/languages.py` - defines default language configs
2. **Database**: `conf_sysoptions` table, key `languages` - runtime configs used by judge dispatcher

**To sync DB with source code:**
```bash
docker exec oj-backend python manage.py shell -c "from options.options import SysOptions; SysOptions.reset_languages(); print('Languages reset to defaults')"
```

### Language Test Results

All languages tested with simple A+B problem (input: two integers on one line, output: their sum):

| Language   | Status   | Time | Memory  | Submission ID                    |
|------------|----------|------|---------|----------------------------------|
| C          | ✓ ACCEPTED | 0ms  | 1.2MB   | f97cfe894867c880acf9f551a797fe13 |
| C++        | ✓ ACCEPTED | 1ms  | 2.9MB   | 6695f4e4bc9b999bf3ec51328d80ca52 |
| Java       | ✓ ACCEPTED | 57ms | 42MB    | e6cc3453698dfff9032d52a3286759b2 |
| Python3    | ✓ ACCEPTED | 4ms  | 6.9MB   | f759f724f299c253b8dfd32985ae4504 |
| JavaScript | ✓ ACCEPTED | 24ms | 39MB    | dbcb7391f032d0ebce394439728666ee |
| Golang     | ✓ ACCEPTED | 0ms  | 3.4MB   | a20e2a704dbe09867d3616eed5e471a7 |

**Test code (A+B):**
```python
# Python3
a, b = map(int, input().split())
print(a + b)
```

### Python3 Fix

**Problem**: Runtime Error when submitting simple Python code (exit_code=2, result=4)

**Root Cause**: Old configuration compiled Python to `.pyc` bytecode for Python 3.6, but judge-server runs Python 3.12. Version mismatch caused runtime errors.

**Solution**: Run `.py` source files directly with `-BS` flags:
- `-B`: Don't write `.pyc` bytecode files
- `-S`: Skip site-specific initialization

**Changes applied:**

1. **Database update** (`conf_sysoptions.languages`):
```python
# Updated Python3 config
{
  "compile": {
    "exe_name": "solution.py",  # Changed from "solution.pyc"
    "command": "/usr/bin/python3 -m py_compile {src_path}",
    # ... other compile settings
  },
  "run": {
    "command": "/usr/bin/python3 -BS {exe_path}",  # Changed from running .pyc
    "env": ["PYTHONIOENCODING=utf-8", "LANG=en_US.UTF-8"]
  }
}
```

2. **Source code update** (`OnlineJudge/judge/languages.py`):
```python
_py3_lang_config = {
    "run": {
        "command": "/usr/bin/python3 -BS {exe_path}",
        "env": ["PYTHONIOENCODING=utf-8"] + _default_env
    },
    # ...
}
```

**Verification**:
```bash
# Test Python3 manually in judge-server
docker exec oj-judge-server sh -lc 'echo "a, b = map(int, input().split())\nprint(a + b)" > /tmp/solution.py && echo "5 7" | python3 -BS /tmp/solution.py'
# Output: 12
```

### Java Fix

**Problem**: Submissions stuck at result=-1 (JUDGING state) even though code executed successfully (exit_code=0, correct output)

**Root Cause**: Java run command included `-Djava.security.manager -Djava.security.policy==/etc/java_policy`, but `/etc/java_policy` file doesn't exist in judge-server. Security manager initialization failed silently, preventing result processing.

**Solution**: Remove security manager flags from run command.

**Changes applied:**

1. **Database update** (`conf_sysoptions.languages`):
```python
# Old (broken) config:
"command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k -Djava.security.manager -Dfile.encoding=UTF-8 -Djava.security.policy==/etc/java_policy -Djava.awt.headless=true Main"

# New (working) config:
"command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k Main"
```

2. **Source code update** (`OnlineJudge/judge/languages.py`):
```python
# Added documentation note about security manager removal
# Run command simplified to: /usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k Main
```

**Verification**:
```bash
# Test Java manually
docker exec oj-judge-server sh -lc 'echo "import java.util.Scanner; class Main { public static void main(String[] args) { Scanner sc = new Scanner(System.in); int a = sc.nextInt(); int b = sc.nextInt(); System.out.println(a + b); sc.close(); }}" > /tmp/Main.java && javac /tmp/Main.java && echo "5 7" | java -cp /tmp Main'
# Output: 12
```

### JavaScript (Node.js) - Verified Working

**Status**: No changes required

**Configuration**:
- Compiler: Node.js 20.x
- Run command: `/usr/bin/node {exe_path}`
- Memory: 39MB typical usage
- Performance: ~24ms for simple A+B

**Verification**: Tested with submission `dbcb7391f032d0ebce394439728666ee` - ACCEPTED

### C / C++ - Verified Working

**Status**: No changes required

**Configuration**:
- C Compiler: GCC 13
- C++ Compiler: G++ 13
- Compile flags: `-DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99` (C), `-DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++17` (C++)
- Memory: 1-3MB typical usage
- Performance: 0-1ms for simple A+B

**Verification**: Tested with submissions `f97cfe894867c880acf9f551a797fe13` (C) and `6695f4e4bc9b999bf3ec51328d80ca52` (C++) - both ACCEPTED

### Golang - Now Operational ✓

**Status**: ✅ WORKING - Compiler installed and tested

**Configuration**:
- Compiler: Go 1.19.8
- Compile command: `/usr/bin/go build -o {exe_path} {src_path}`
- Run command: `{exe_path}`
- Memory: 3.4MB typical usage
- Performance: ~0ms for simple A+B

**Fix Applied**: Added `golang` package to `JudgeServer/Dockerfile`:

```dockerfile
needed="python3-minimal \
    python3-venv \
    libpython3-stdlib \
    libpython3-dev \
    temurin-21-jdk \
    gcc \
    g++ \
    golang \  # <-- ADDED
    nodejs \
    strace"
```

**Verification**: Tested with submission `a20e2a704dbe09867d3616eed5e471a7` - ACCEPTED

**Test code (A+B)**:
```go
package main
import "fmt"

func main() {
    var a, b int
    fmt.Scan(&a, &b)
    fmt.Println(a + b)
}
```

### How to Update Language Configurations

**Method 1: Direct DB update (immediate effect)**
```bash
docker exec oj-backend python manage.py shell -c "
from options.options import SysOptions
import json

# Get current languages
langs = SysOptions.languages

# Example: Update Python3 run command
langs['Python3']['config']['run']['command'] = '/usr/bin/python3 -BS {exe_path}'

# Save back to DB
SysOptions.languages = langs
print('Updated languages config')
"
```

**Method 2: Reset from source code (use after editing languages.py)**
```bash
# 1. Edit OnlineJudge/judge/languages.py
# 2. Restart backend to reload Python modules (if not bind-mounted)
docker compose restart backend
# 3. Reset DB to match source
docker exec oj-backend python manage.py shell -c "from options.options import SysOptions; SysOptions.reset_languages()"
```

**Method 3: Rebuild backend image (persistent changes)**
```bash
# After editing OnlineJudge/judge/languages.py
docker compose build backend
docker compose up -d backend
# Then reset DB
docker exec oj-backend python manage.py shell -c "from options.options import SysOptions; SysOptions.reset_languages()"
```

### Testing New Language Configurations

**Quick test script:**
```bash
# Create test submission for a specific problem and language
docker exec oj-backend python manage.py shell -c "
from submission.models import Submission
from problem.models import Problem
from account.models import User

# Get test problem and user
problem = Problem.objects.get(id='CB102')  # A+B problem
user = User.objects.first()

# Test code (adjust for language)
code = '''a, b = map(int, input().split())
print(a + b)'''

# Create submission
s = Submission.objects.create(
    problem=problem,
    user_id=user.id,
    username=user.username,
    code=code,
    language='Python3',  # Change to: C, C++, Java, JavaScript, etc.
    contest_id=None
)

print(f'Created submission: {s.id}')

# Enqueue for judging
from judge.tasks import judge_task
judge_task.send(s.id, problem.id)
print('Enqueued for judging')
"

# Check result after a few seconds
docker exec oj-backend python manage.py shell -c "
from submission.models import Submission
s = Submission.objects.latest('create_time')
print(f'Result: {s.result} | Time: {s.statistic_info.get(\"time_cost\")}ms | Memory: {s.statistic_info.get(\"memory_cost\")}KB')
if s.statistic_info.get('err_info'):
    print(f'Error: {s.statistic_info[\"err_info\"]}')
"
```

### Summary of Working Languages

**Fully Operational (6/6)** ✅:
- ✓ C (GCC 13)
- ✓ C++ (G++ 13)
- ✓ Java (Temurin JDK 21) - after security manager fix
- ✓ Python3 (3.12) - after -BS flag fix
- ✓ JavaScript (Node.js 20)
- ✓ Golang (Go 1.19.8) - after installing compiler

**All languages tested and verified working!**

## Troubleshooting

- Test case not found
  - Ensure host path: `OnlineJudge/data/backend/test_case/<case_id>/info` exists
  - Inside judge-server: `docker exec -it oj-judge-server ls -la /test_case/<case_id>`
- Ping fails or 401
  - Confirm token header is sha256 of the backend `JUDGE_SERVER_TOKEN` env var (default `CHANGE_THIS`).
- Rosetta mmap/secccomp errors
  - Rebuild the local image (ARM) and ensure compose uses `oj-judge-server:local` with security options enabled.
- Judge server not selected
  - Check `conf_judgeserver` table for fresh `last_heartbeat` and `is_disabled=False`.
- Language Runtime Error
  - Check `submission.statistic_info.err_info` for detailed error messages
  - Verify compiler is installed: `docker exec oj-judge-server which <compiler>`
  - Test compiler manually in judge-server container
- Submission stuck at result=-1 (JUDGING)
  - Check judge logs: `tail -n 100 OnlineJudge/data/log/judger.log`
  - Verify judge-server is running: `docker ps | grep judge-server`
  - Check Dramatiq worker is processing: `docker logs oj-backend | grep dramatiq`
- Wrong Answer despite correct output
  - Ensure output format matches expected (check trailing newlines, whitespace)
  - Verify test case files: `docker exec oj-backend cat /data/backend/test_case/<case_id>/1.out`
  - MD5 comparison uses `rstrip()` to ignore trailing whitespace
```
