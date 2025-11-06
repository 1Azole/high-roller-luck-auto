from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_via_sendgrid(api_key, sender, recipient, subject, markdown):
    if not all([api_key, sender, recipient]):
        raise RuntimeError("Missing SendGrid secrets (API key / sender / recipient).")
    html = f'<pre style="font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap;">{markdown}</pre>'
    message = Mail(
        from_email=sender,
        to_emails=recipient,
        subject=subject,
        html_content=html
    )
    sg = SendGridAPIClient(api_key)
    sg.send(message)
