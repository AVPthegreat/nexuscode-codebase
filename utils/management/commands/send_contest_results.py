from django.core.management.base import BaseCommand
from django.utils.timezone import now

from contest.models import Contest, ContestAttempt, ContestAttemptProblemStat
from utils.mail import send_contest_result_email


class Command(BaseCommand):
    help = "Send contest result emails to participants. By default, processes all ended contests not yet emailed."

    def add_arguments(self, parser):
        parser.add_argument("--contest-id", type=int, help="Send for a specific contest id")
        parser.add_argument("--dry-run", action="store_true", help="Only print counts; do not send emails")
        parser.add_argument("--resend", action="store_true", help="Ignore results_emailed_at guard and resend")
        parser.add_argument("--user-id", type=int, help="Restrict sending to a single user id (for targeted testing)")

    def handle(self, *args, **options):
        contest_id = options.get("contest_id")
        dry_run = options.get("dry_run")
        resend = options.get("resend")
        user_id = options.get("user_id")

        if contest_id:
            contests = Contest.objects.filter(id=contest_id)
        else:
            contests = Contest.objects.filter(end_time__lt=now())
            if not resend:
                contests = contests.filter(results_emailed_at__isnull=True)

        total_sent = 0
        processed_contests = 0

        for contest in contests:
            attempts_qs = ContestAttempt.objects.filter(contest=contest, started=True).select_related("user")
            if user_id:
                attempts_qs = attempts_qs.filter(user_id=user_id)
            attempts = attempts_qs
            if not attempts.exists():
                self.stdout.write(self.style.WARNING(f"Contest {contest.id} has no attempts; skipping"))
                if not resend and contest.results_emailed_at is None:
                    contest.results_emailed_at = now()
                    contest.save(update_fields=["results_emailed_at"])
                continue

            scope_info = f" (filtered to user {user_id})" if user_id else ""
            self.stdout.write(f"Processing contest {contest.id} - {contest.title}: {attempts.count()} attempts{scope_info}")

            sent = 0
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

                if dry_run:
                    continue
                try:
                    send_contest_result_email(attempt.user, contest, attempt, problem_stats)
                    sent += 1
                except Exception:
                    # continue sending others even if one fails
                    pass

            if not dry_run:
                # mark to avoid duplicates
                contest.results_emailed_at = now()
                contest.save(update_fields=["results_emailed_at"])

            total_sent += sent
            processed_contests += 1
            self.stdout.write(self.style.SUCCESS(f"Contest {contest.id}: emails {'simulated' if dry_run else 'sent'} for {attempts.count()} attempts"))

        summary = f"Processed {processed_contests} contest(s). Total emails {'simulated' if dry_run else 'sent'}: {total_sent}."
        self.stdout.write(self.style.SUCCESS(summary))
