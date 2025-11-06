import os
import sys
import threading
import time
from django.apps import AppConfig
from django.utils.timezone import now


class ContestConfig(AppConfig):
    name = 'contest'
    verbose_name = 'Contest'

    _auto_sender_started = False

    def ready(self):
        # Start a lightweight background thread to auto-send contest results when contests end.
        # This is best-effort for dev/single-process deploys. In production, prefer a scheduler
        # triggering the management command `send_contest_results`.
        if not self._should_start_auto_sender():
            return
        if ContestConfig._auto_sender_started:
            return
        ContestConfig._auto_sender_started = True

        t = threading.Thread(target=self._auto_sender_loop, name="contest_auto_result_sender", daemon=True)
        t.start()

    def _should_start_auto_sender(self) -> bool:
        if os.environ.get('DISABLE_AUTO_SEND_CONTEST_RESULTS') == '1':
            return False
        # Avoid running inside management commands other than runserver/gunicorn
        cmd = sys.argv[1] if len(sys.argv) > 1 else ''
        blocked = {
            'makemigrations', 'migrate', 'shell', 'dbshell', 'collectstatic', 'loaddata', 'dumpdata',
            'send_contest_results', 'set_smtp', 'inituser', 'createsuperuser', 'test', 'changepassword',
        }
        if cmd in blocked:
            return False
        # Dev server autoreload spawns a master process; run thread only in the child
        if cmd == 'runserver' and os.environ.get('RUN_MAIN') != 'true':
            return False
        return True

    def _auto_sender_loop(self):
        from contest.models import Contest, ContestAttempt, ContestAttemptProblemStat
        from utils.mail import send_contest_result_email

        interval = int(os.environ.get('AUTO_SEND_POLL_SECONDS', '60'))
        batch_size = int(os.environ.get('AUTO_SEND_BATCH_SIZE', '10'))
        while True:
            try:
                # Find a small batch of ended contests not yet emailed
                qs = Contest.objects.filter(end_time__lt=now(), results_emailed_at__isnull=True).order_by('end_time')[:batch_size]
                contests = list(qs)
                for contest in contests:
                    # Atomically mark as processed to avoid duplicates across processes
                    updated = Contest.objects.filter(id=contest.id, results_emailed_at__isnull=True).update(results_emailed_at=now())
                    if updated == 0:
                        continue

                    attempts = ContestAttempt.objects.filter(contest=contest, started=True).select_related("user")
                    for attempt in attempts:
                        stats = ContestAttemptProblemStat.objects.filter(attempt=attempt)
                        problem_stats = [
                            {
                                "problem_id": s.problem_id,
                                "attempts": s.attempts,
                                "best_result": s.best_result,
                                "passed_cases": s.passed_cases,
                                "total_cases": s.total_cases,
                                "score": s.score,
                            }
                            for s in stats
                        ]
                        try:
                            send_contest_result_email(attempt.user, contest, attempt, problem_stats)
                        except Exception:
                            # best-effort; continue with others
                            pass
            except Exception:
                # Swallow errors to keep the loop alive; next tick will retry new contests.
                pass
            time.sleep(interval)
