import os
import requests
from typing import List, Dict, Callable
from decimal import Decimal, ROUND_HALF_UP

# fetch environment variables
LEAGUE_ID = os.environ.get("LEAGUE_ID", "").strip()
SEASON = os.environ.get("SEASON", "").strip()
ESPN_S2 = os.environ.get("ESPN_S2", "").strip()
SWID = os.environ.get("SWID", "").strip()

# Email config
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "").strip()
SMTP_SERVER = os.environ.get("SMTP_SERVER", "").strip()
SMTP_PORT = os.environ.get("SMTP_PORT", "").strip()
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "").strip()
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "").strip()

SUBJECT = "High Roller Luck Rankings (Auto)"

def round2(x: float) -> float:
    return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def fetch_league_json(league_id: str, season: str, swid: str, espn_s2: str) -> dict:
    assert league_id and season and swid and espn_s2, "Missing league or auth cookies."
    url = (
        f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{season}"
        f"/segments/0/leagues/{league_id}?view=mTeam&view=mStandings"
    )
    headers = {"Cookie": f"SWID={swid}; espn_s2={espn_s2}"}
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"ESPN API error {r.status_code}: {r.text[:400]}")
    return r.json()

def extract_rows(data: dict) -> List[Dict]:
    rows = []
    for t in data.get("teams", []):
        name = f"{t.get('location','')} {t.get('nickname','')}".strip()
        rec = (t.get("record") or {}).get("overall", {})
        wins = int(rec.get("wins") or 0)
        pf = float(rec.get("pointsFor") or 0.0)
        pa = float(rec.get("pointsAgainst") or 0.0)
        pfpa = (pf / pa) if pa > 0 else 0.0
        rows.append({"name": name, "wins": wins, "pf": pf, "pa": pa, "pfpa": pfpa})
    return rows

def standings_sort(a: Dict, b: Dict) -> int:
    if a["wins"] != b["wins"]:
        return -1 if a["wins"] > b["wins"] else 1
    if a["pf"] != b["pf"]:
        return -1 if a["pf"] > b["pf"] else 1
    return -1 if a["name"] < b["name"] else (1 if a["name"] > b["name"] else 0)

def pfpa_sort(a: Dict, b: Dict) -> int:
    ar, br = round2(a["pfpa"]), round2(b["pfpa"])
    if ar != br:
        return -1 if ar > br else 1
    return -1 if a["name"] < b["name"] else (1 if a["name"] > b["name"] else 0)

def stable_sort(items: List[Dict], cmp: Callable[[Dict, Dict], int]) -> List[Dict]:
    class K:
        def __init__(self, obj):
            self.obj = obj
        def __lt__(self, other):
            return cmp(self.obj, other.obj) < 0
    return sorted(items, key=K)

def tie_rank_map(sorted_rows: List[Dict], key_fn: Callable[[Dict], str]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    i = 0
    n = len(sorted_rows)
    while i < n:
        rank = i + 1
        key = key_fn(sorted_rows[i])
        j = i + 1
        while j < n and key_fn(sorted_rows[j]) == key:
            j += 1
        display = f"T{rank}" if (j - i) > 1 else f"{rank}"
        for k in range(i, j):
            out[sorted_rows[k]["name"]] = {"rank": rank, "display": display}
        i = j
    return out

def build_markdown(enriched: List[Dict]) -> str:
    header = "| Team Name | Standings | PF/PA | Luck |\n|---|---|---|---|"
    lines = []
    for r in enriched:
        pfpa_str = f"{r['pfpa']:.2f}"
        pfpa_col = f"{pfpa_str} ({r['pfpaDisp']})"
        luck_str = f"+{r['luck']}" if r['luck'] >= 0 else str(r['luck'])
        lines.append(f"| {r['name']} | {r['standingsDisp']} | {pfpa_col} | {luck_str} |")
    return header + "\n" + "\n".join(lines)

def main():
    d    # Send emails only during fantasy season: from the 2nd Tuesday in September to the 4th Tuesday in December
    import calendar
    import pytz
    from datetime import datetime, date
    tz = pytz.timezone('America/New_York')
    today = datetime.now(tz).date()
    year = today.year
    def nth_weekday_of_month(y: int, month: int, weekday: int, n: int) -> date:
        cal = calendar.monthcalendar(y, month)
        count = 0
        for week in cal:
            if week[weekday] != 0:
                count += 1
                if count == n:
                    return date(y, month, week[weekday])
        return None
    second_tuesday_september = nth_weekday_of_month(year, 9, calendar.TUESDAY, 2)
    fourth_tuesday_december = nth_weekday_of_month(year, 12, calendar.TUESDAY, 4)
    if second_tuesday_september and fourth_tuesday_december:
        if today < second_tuesday_september or today > fourth_tuesday_december:
            print("Outside active season. Skipping email.")
            return
data = fetch_league_json(LEAGUE_ID, SEASON, SWID, ESPN_S2)
    rows = extract_rows(data)

    standings_sorted = stable_sort(rows, standings_sort)
    standings_rank = tie_rank_map(standings_sorted, lambda r: f"{r['wins']}|{int(round(r['pf']))}")

    pfpa_sorted = stable_sort(rows, pfpa_sort)
    pfpa_rank = tie_rank_map(pfpa_sorted, lambda r: f"{round2(r['pfpa']):.2f}")

    enriched: List[Dict] = []
    for r in rows:
        s = standings_rank[r["name"]]
        p = pfpa_rank[r["name"]]
        enriched.append({
            "name": r["name"],
            "pf": r["pf"],
            "pa": r["pa"],
            "pfpa": round2(r["pfpa"]),
            "pfpaRank": p["rank"],
            "pfpaDisp": p["display"],
            "standingsRank": s["rank"],
            "standingsDisp": s["display"],
            "luck": p["rank"] - s["rank"]
        })

    enriched.sort(key=lambda x: (-x["luck"], x["pfpa"], x["name"]))

    md = build_markdown(enriched)

    if SENDGRID_API_KEY:
        from email_sendgrid import send_via_sendgrid
        send_via_sendgrid(SENDGRID_API_KEY, SENDER_EMAIL, RECIPIENT_EMAIL, SUBJECT, md)
    else:
        from email_smtp import send_via_smtp
        send_via_smtp(
            smtp_server=SMTP_SERVER,
            smtp_port=int(SMTP_PORT or 587),
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            sender=SENDER_EMAIL,
            recipient=RECIPIENT_EMAIL,
            subject=SUBJECT,
            markdown=md
        )

if __name__ == "__main__":
    main()
