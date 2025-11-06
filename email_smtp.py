import smtplib, ssl
from email.mime.text import MIMEText


def send_via_smtp(smtp_server, smtp_port, username, password, sender, recipient, subject, markdown):
    if not all([smtp_server, smtp_port, username, password, sender, recipient]):
        raise RuntimeError("Missing SMTP secrets (server/port/username/password/sender/recipient).")
    # Render Markdown as preformatted text in HTML so alignment stays perfect
    html = f'<pre style="font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap;">{markdown}</pre>'
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(sender, [recipient], msg.as_string())
