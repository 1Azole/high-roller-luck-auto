import os
import pytz
from datetime import datetime
from espn_api.football import League


def send_email(subject: str, body: str) -> None:
  # Determine email method
  sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
  recipient_email = os.environ.get("RECIPIENT_EMAIL")
  sender_email = os.environ.get("SENDER_EMAIL")
  if sendgrid_api_key:
    from email_sendgrid import send_via_sendgrid
    send_via_sendgrid(
      to_emails=recipient_email,
      subject=subject,
      html_content=body,
      sendgrid_api_key=sendgrid_api_key,
      from_email=sender_email
    )
  elif os.environ.get("SMTP_SERVER"):
    from email_smtp import send_via_smtp
    send_via_smtp(
      subject=subject,
      html_body=body,
      from_email=sender_email,
      to_emails=recipient_email,
      smtp_server=os.environ.get("SMTP_SERVER"),
      smtp_port=int(os.environ.get("SMTP_PORT", "587")),
      smtp_username=os.environ.get("SMTP_USERNAME"),
      smtp_password=os.environ.get("SMTP_PASSWORD")
    )
  else:
    # Fallback to printing the body
    print(body)


def compute_luck_and_sos(league: League) -> str:
  teams = league.teams
  pf = {team.team_id: 0 for team in teams}
  pa = {team.team_id: 0 for team in teams}

  # Sum points for and points against for each team
  scoreboard = league.scoreboard()
  weeks = len(scoreboard)
  for week_matchups in scoreboard:
    for matchup in week_matchups:
      home = matchup.home_team
      away = matchup.away_team
      pf[home.team_id] += home.score
      pa[home.team_id] += away.score
      pf[away.team_id] += away.score
      pa[away.team_id] += home.score

  # Calculate expected wins by comparing PF to every other team
  expected_wins = {}
  n_teams = len(teams)
  for team in teams:
    wins_vs_all = 0
    for opponent in teams:
      if opponent.team_id == team.team_id:
        continue
      if pf[team.team_id] > pf[opponent.team_id]:
        wins_vs_all += 1
      elif pf[team.team_id] == pf[opponent.team_id]:
        wins_vs_all += 0.5
    expected_win_rate = wins_vs_all / (n_teams - 1) if n_teams > 1 else 0
    expected_wins[team.team_id] = expected_win_rate * weeks

  entries = []
  for team in teams:
    tid = team.team_id
    luck_value = team.wins - expected_wins.get(tid, 0)
    sos_value = pf[tid] - pa[tid]
    entries.append({
      "team": team,
      "luck": luck_value,
      "sos": sos_value,
    })

  entries.sort(key=lambda x: (x["luck"], x["sos"]), reverse=True)
  lines = []
  for entry in entries:
    t = entry["team"]
    lines.append(f"{t.team_name}: Luck {entry['luck']:.2f}, SOS {entry['sos']:.1f}, Record {t.wins}-{t.losses}")

  return "\n".join(lines)


def get_injury_feed(league: League) -> str:
  # Placeholder for future injury integration
  return "Injury feed integration coming soon."


def get_faab_history(league: League) -> str:
  # Placeholder for FAAB history retrieval
  return "FAAB history feature coming soon."


def get_trade_projections(league: League) -> str:
  # Placeholder for trade impact projections
  return "Trade-impact projections feature coming soon."


def get_weekly_writeup(league: League) -> str:
  # Placeholder for AI-generated weekly write-ups
  return "Weekly AI write-up coming soon."


def get_manager_roasts(league: League) -> str:
  # Placeholder for manager roast mode
  parts = []
  for team in league.teams:
    parts.append(f"{team.team_name}: It's nothing personal, but this feature will roast managers soon!")
  return "\n".join(parts)


def main() -> None:
  # Load required environment variables
  league_id = os.environ.get("LEAGUE_ID")
  season = os.environ.get("SEASON")
  espn_s2 = os.environ.get("ESPN_S2")
  swid = os.environ.get("SWID")

  if not all([league_id, season, espn_s2, swid]):
    import os
import pytz
from datetime import datetime
from espn_api.football import League


# Helper function to send an email via SendGrid or SMTP.
def send_email(subject: str, body: str) -> None:
  sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
  recipient_email = os.environ.get("RECIPIENT_EMAIL")
  sender_email = os.environ.get("SENDER_EMAIL")
  if sendgrid_api_key:
    from email_sendgrid import send_via_sendgrid
    send_via_sendgrid(
      to_emails=recipient_email,
      subject=subject,
      html_content=body,
      sendgrid_api_key=sendgrid_api_key,
      from_email=sender_email
    )
  elif os.environ.get("SMTP_SERVER"):
    from email_smtp import send_via_smtp
    send_via_smtp(
      subject=subject,
      html_body=body,
      from_email=sender_email,
      to_emails=recipient_email,
      smtp_server=os.environ.get("SMTP_SERVER"),
      smtp_port=int(os.environ.get("SMTP_PORT", "587")),
      smtp_username=os.environ.get("SMTP_USERNAME"),
      smtp_password=os.environ.get("SMTP_PASSWORD")
    )
  else:
    # Fallback to printing the body
    print(body)


# Compute luck and strength of schedule index for each team.
def compute_luck_and_sos(league: League) -> str:
  teams = league.teams
  pf = {team.team_id: 0 for team in teams}
  pa = {team.team_id: 0 for team in teams}

  # Sum points for and points against for each team
  scoreboard = league.scoreboard()
  weeks = len(scoreboard)
  for week_matchups in scoreboard:
    for matchup in week_matchups:
      home = matchup.home_team
      away = matchup.away_team
      pf[home.team_id] += home.score
      pa[home.team_id] += away.score
      pf[away.team_id] += away.score
      pa[away.team_id] += home.score

  # Calculate expected wins by comparing PF to every other team
  expected_wins = {}
  n_teams = len(teams)
  for team in teams:
    wins_vs_all = 0
    for opponent in teams:
      if opponent.team_id == team.team_id:
        continue
      if pf[team.team_id] > pf[opponent.team_id]:
        wins_vs_all += 1
      elif pf[team.team_id] == pf[opponent.team_id]:
        wins_vs_all += 0.5
    expected_win_rate = wins_vs_all / (n_teams - 1) if n_teams > 1 else 0
    expected_wins[team.team_id] = expected_win_rate * weeks

  entries = []
  for team in teams:
    tid = team.team_id
    luck_value = team.wins - expected_wins.get(tid, 0)
    sos_value = pf[tid] - pa[tid]
    entries.append({
      "team": team,
      "luck": luck_value,
      "sos": sos_value,
    })

  entries.sort(key=lambda x: (x["luck"], x["sos"]), reverse=True)
  lines = []
  for entry in entries:
    t = entry["team"]
    lines.append(f"{t.team_name}: Luck {entry['luck']:.2f}, SOS {entry['sos']:.1f}, Record {t.wins}-{t.losses}")

  return "\n".join(lines)


# Placeholder for future injury integration.
def get_injury_feed(league: League) -> str:
  return "Injury feed integration coming soon."


# Placeholder for FAAB history retrieval.
def get_faab_history(league: League) -> str:
  return "FAAB history feature coming soon."


# Placeholder for trade impact projections.
def get_trade_projections(league: League) -> str:
  return "Trade-impact projections feature coming soon."


# Placeholder for AI-generated weekly write-ups.
def get_weekly_writeup(league: League) -> str:
  return "Weekly AI write-up coming soon."


# Placeholder for manager roast mode.
def get_manager_roasts(league: League) -> str:
  parts = []
  for team in league.teams:
    parts.append(f"{team.team_name}: It's nothing personal, but this feature will roast managers soon!")
  return "\n".join(parts)


# Main entry point for the weekly summary program.
def main() -> None:
  league_id = os.environ.get("LEAGUE_ID")
  season = os.environ.get("SEASON")
  espn_s2 = os.environ.get("ESPN_S2")
  swid = os.environ.get("SWID")

  if not all([league_id, season, espn_s2, swid]):
    print("Missing league credentials. Please set LEAGUE_ID, SEASON, ESPN_S2, and SWID.")
    return

  # Create the League instance
  league = League(league_id, int(season), espn_s2=espn_s2, swid=swid)

  # Determine the date in the user's timezone (Eastern Time)
  tz = pytz.timezone("America/New_York")
  today = datetime.now(tz).date()

  # Build all report sections
  sections = []
  sections.append("# Weekly Fantasy Report")
  sections.append("## Injury Report\n" + get_injury_feed(league))
  sections.append("## FAAB History\n" + get_faab_history(league))
  sections.append("## Trade Impact Projections\n" + get_trade_projections(league))
  sections.append("## Weekly AI Write-up\n" + get_weekly_writeup(league))
  sections.append("## Manager Roasts\n" + get_manager_roasts(league))
  sections.append("## Luck and Strength of Schedule Index\n" + compute_luck_and_sos(league))

  body = "\n\n".join(sections)
  subject = f"Fantasy Weekly Report - {today.strftime('%B %d, %Y')}"

  # Send the email
  send_email(subject, body)


if __name__ == "__main__":
  main()
print("Missing league credentials. Please set LEAGUE_ID, SEASON, ESPN_S2, and SWID.")
    return

  # Create League instance
  league = League(league_id, int(season), espn_s2=espn_s2, swid=swid)

  # Determine today's date in Eastern Time
  tz = pytz.timezone("America/New_York")
  today = datetime.now(tz).date()

  # Build the email body with all sections
  sections = []
  sections.append("# Weekly Fantasy Report")
  sections.append("## Injury Report\n" + get_injury_feed(league))
  sections.append("## FAAB History\n" + get_faab_history(league))
  sections.append("## Trade Impact Projections\n" + get_trade_projections(league))
  sections.append("## Weekly AI Write-up\n" + get_weekly_writeup(league))
  sections.append("## Manager Roasts\n" + get_manager_roasts(league))
  sections.append("## Luck and Strength of Schedule Index\n" + compute_luck_and_sos(league))

  body = "\n\n".join(sections)
  subject = f"Fantasy Weekly Report - {today.strftime('%B %d, %Y')}"

  # Send the email
  send_email(subject, body)


if __name__ == "__main__":
  main()
