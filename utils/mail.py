from datetime import datetime
from django.template.loader import render_to_string
from options.options import SysOptions
from utils.shortcuts import send_email as send_email_sync


def send_verification_email(user):
    """Ensure user has a verification token and send verification email."""
    if not user.email or not SysOptions.smtp_config:
        return
    token = user.email_verify_token
    if not token:
        from utils.shortcuts import rand_str
        from django.utils.timezone import now as dj_now
        from datetime import timedelta
        token = rand_str()
        user.email_verify_token = token
        user.email_verify_token_expire_time = dj_now() + timedelta(hours=24)
        user.save(update_fields=["email_verify_token", "email_verify_token_expire_time"])
    link = f"{SysOptions.website_base_url}/verify-email/{token}"
    data = {"username": user.username, "website_name": SysOptions.website_name, "link": link}
    try:
        html = render_to_string("verify_email.html", data)
    except Exception:
        html = f"<p>Hello {user.username}, verify: <a href='{link}'>{link}</a></p>"
    # Direct synchronous send (simplified; removed async for reliability in your environment)
    send_email_sync(smtp_config=SysOptions.smtp_config,
                    from_name=SysOptions.website_name_shortcut,
                    to_email=user.email,
                    to_name=user.username,
                    subject="Verify your email",
                    content=html)


def send_contest_result_email(user, contest, attempt, problem_stats):
    """Send a summary of contest results to a user.

    problem_stats: iterable of dict with keys (problem_id, attempts, passed_cases, total_cases, score, best_result)
    """
    if not user.email or not SysOptions.smtp_config:
        return
    summary_rows = []
    total_score = 0
    for ps in problem_stats:
        total_score += ps.get("score", 0)
        passed = f"{ps.get('passed_cases', 0)}/{ps.get('total_cases', 0)}"
        summary_rows.append(f"<tr><td>{ps.get('problem_id')}</td><td>{ps.get('attempts')}</td><td>{passed}</td><td>{ps.get('score')}</td></tr>")
    table_html = """
    <table style='border-collapse:collapse;width:100%;'>
      <thead><tr style='background:#eee'><th>Problem</th><th>Attempts</th><th>Passed</th><th>Score</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """.replace("{rows}", "".join(summary_rows))
    started = attempt.started_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.started_at else 'N/A'
    finished = attempt.finished_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.finished_at else 'N/A'
    violations = attempt.fullscreen_exit_count
    html = f"""
    <h3>Contest Result: {contest.title}</h3>
    <p>User: {user.username}</p>
    <p>Attempt #{attempt.attempt_no}</p>
    <p>Started: {started}<br/>Finished: {finished}</p>
    <p>Fullscreen exits / violations: {violations}</p>
    <p>Total Score: <strong>{total_score}</strong></p>
    {table_html}
    <p>Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
    """
    send_email_sync(smtp_config=SysOptions.smtp_config,
                    from_name=SysOptions.website_name_shortcut,
                    to_email=user.email,
                    to_name=user.username,
                    subject=f"Contest Result - {contest.title}",
                    content=html)
