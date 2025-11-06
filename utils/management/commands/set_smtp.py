from django.core.management.base import BaseCommand, CommandError
from options.options import SysOptions
from utils.shortcuts import send_email


class Command(BaseCommand):
    help = "Configure SMTP settings (server, port, email, password, tls). Optionally send a test email."

    def add_arguments(self, parser):
        parser.add_argument("--server", required=True, help="SMTP server, e.g. smtp.gmail.com")
        parser.add_argument("--port", required=True, type=int, help="SMTP port, e.g. 587")
        parser.add_argument("--email", required=True, help="SMTP account email")
        parser.add_argument("--password", required=True, help="SMTP password or app password")
        parser.add_argument("--tls", action="store_true", help="Enable TLS")
        parser.add_argument("--test", action="store_true", help="Send a test email to the configured address")

    def handle(self, *args, **options):
        smtp = {
            "server": options["server"],
            "port": options["port"],
            "email": options["email"],
            "password": options["password"],
            "tls": bool(options["tls"]),
        }
        SysOptions.smtp_config = smtp
        self.stdout.write(self.style.SUCCESS("SMTP configuration saved."))

        if options["test"]:
            try:
                send_email(
                    smtp_config=smtp,
                    from_name=SysOptions.website_name_shortcut,
                    to_name="SMTP Test",
                    to_email=options["email"],
                    subject="SMTP Test - Nexus Code",
                    content="<p>This is a test email from Nexus Code.</p>",
                )
                self.stdout.write(self.style.SUCCESS("Test email sent successfully."))
            except Exception as e:
                raise CommandError(f"Failed to send test email: {e}")
