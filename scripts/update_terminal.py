"""Fill assets/terminal.template.svg with live GitHub numbers and write assets/terminal.svg.

Runs daily from .github/workflows/refresh.yml. Standard library only.
Set GITHUB_TOKEN for the contribution count (GraphQL needs auth); without it that field shows "—".
"""

import json
import os
import urllib.request
from datetime import date
from pathlib import Path

USER = "Vicky2487"
STARTED = date(2026, 3, 1)  # first day shipping code professionally
ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("GITHUB_TOKEN")


def request(url, body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body else None
    with urllib.request.urlopen(urllib.request.Request(url, data, headers)) as r:
        return json.load(r)


def contributions():
    if not TOKEN:
        return "—"
    query = "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions}}}}"
    res = request("https://api.github.com/graphql", {"query": query, "variables": {"u": USER}})
    return f"{res['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']:,}"


def uptime(today):
    months = (today.year - STARTED.year) * 12 + today.month - STARTED.month
    years, months = divmod(months, 12)
    parts = [f"{years} year{'s' * (years != 1)}"] if years else []
    parts.append(f"{months} month{'s' * (months != 1)}")
    return ", ".join(parts) + " shipping"


def main():
    today = date.today()
    user = request(f"https://api.github.com/users/{USER}")
    repos = request(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    values = {
        "repos": str(user["public_repos"]),
        "followers": str(user["followers"]),
        "stars": str(sum(r["stargazers_count"] for r in repos if not r["fork"])),
        "contrib": contributions(),
        "uptime": uptime(today),
        "updated": today.strftime("%d %b %Y"),
    }
    svg = (ROOT / "assets/terminal.template.svg").read_text()
    for key, value in values.items():
        svg = svg.replace("{{" + key + "}}", value)
    (ROOT / "assets/terminal.svg").write_text(svg)
    print(values)


if __name__ == "__main__":
    main()
