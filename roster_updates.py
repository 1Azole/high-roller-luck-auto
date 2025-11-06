import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from espn_api.football import League


def main():
    """
    Send a roster update summary email for all teams in a fantasy league.
    Fetches recent activity over the last 3 days and groups roster changes
    by team. If a team has no changes, note that explicitly. Email is
    delivered via SMTP using credentials defined in environment variables.
    """
    # Fetch environment variables
    league_id = os.environ.get("LEAGUE_ID", "").strip()
    season = os.environ.get("SEASON", "").strip()
    espn_s2 = os.environ.get("ESPN_S2", "").strip()
    swid = os.environ.get("SWID", "").strip()
    smtp_server = os.environ.get("SMTP_SERVER", "").strip()
    smtp_port = os.environ.get("SMTP_PORT", "").strip()
    smtp_username = os.environ.get("SMTP_USERNAME", "").strip()
    smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()
    sender_email = os.environ.get("SENDER_EMAIL", "").strip()
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "").strip()

    # Validate mandatory fields
    if not (league_id and season and espn_s2 and swid):
        raise RuntimeError("Missing league credentials")
    if not (smtp_server and smtp_username and smtp_password 
            and sender_email and recipient_email):
        raise RuntimeError("Missing SMTP credentials")

    # Initialize league
    league = League(int(league_id), int(season), espn_s2=espn_s2, swid=swid)

    # Compute time window (last 3 days)
    tz = pytz.timezone("America/New_York")
    now = datetime.now(tz)
    cutoff = now - timedelta(days=3)

    # Initialize dictionary for changes
    changes_by_team = {team.team_name: [] for team in league.teams}

    # Fetch and process recent activities
    activities = league.recent_activity(size=200)
    for activity in activities:
        # Parse the activity date; skip if date is invalid
        try:
            activity_dt = parser.isoparse(activity.date).astimezone(tz)
        except Exception:
            continue
        # Skip if older than cutoff
        if activity_dt < cutoff:
            continue
        # Process each action in the activity
        for team, action, player, bid_amount in activity.actions:
            description = ""
            if "ADDED" in action:
                description = f"Added {player.name}"
                if bid_amount:
                    description += f" (waiver bid {bid_amount})"
            elif "DROPPED" in action:
                description = f"Dropped {player.name}"
            elif "TRADED" in action:
                description = f"Traded {player.name}"
            else:
                # Fallback for other actions like moved to IR, etc.
                description = f"{action.title()} {player.name}"
            changes_by_team[team.team_name].append(description)

    # Build markdown summary
    period_str = f"{cutoff.strftime('%b %d')} - {now.strftime('%b %d')}"
    md_lines = []
    md_lines.append(f"### Roster Updates ({period_str})\n\n")
    for team_name in sorted(changes_by_team.keys()):
        entries = changes_by_team[team_name]
        if entries:
            md_lines.append(f"**{team_name}**\n")
            for entry in entries:
                md_lines.append(f"- {entry}\n")
            md_lines.append("\n")
        else:
            md_lines.append(f"**{team_name}**: No changes\n\n")
    markdown = "".join(md_lines)

    # Prepare subject and send email
    subject = f"Roster Updates ({now.strftime('%b %d')})"
    from email_smtp import send_via_smtp
    send_via_smtp(
        smtp_server=smtp_server,
        smtp_port=int(smtp_port or 587),
        username=smtp_username,
        password=smtp_password,
        sender=sender_email,
        recipient=recipient_email,
        subject=subject,
        markdown=markdown,
    )


if __name__ == "__main__":
    main()
