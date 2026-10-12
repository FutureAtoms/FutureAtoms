#!/usr/bin/env python3
"""Build contribution cards for a GitHub profile README, counts only.

  python3 build_stats.py --accounts AC-e-AI,FutureAtoms --out stats [--combined] [--label AC-e-AI=Work --label FutureAtoms=Studio]

Reads each account's public contribution calendar through the GitHub GraphQL API (private work appears
as daily counts only when the account shows private contributions), merges it into stats/history.json so
the record survives even if an account disappears or private work later drops out of its public calendar, and writes dark and light SVG cards: one per account
and, with --combined, one for all accounts together. No repository, organisation or project name is
ever fetched or written. Standard library only; reads the token from GITHUB_TOKEN or GH_TOKEN.
"""
import argparse, datetime as dt, json, os, urllib.request
from pathlib import Path

API = 'https://api.github.com/graphql'
THEMES = {
    'dark': dict(bg='#0E0F10', line='#232426', head='#EDEAE3', text='#C9C9C4', muted='#86868A', accent='#C2A877',
                 scale=['#1A1B1D', '#3D3424', '#6E5B34', '#A8894F', '#D9B66E']),
    'light': dict(bg='#F7F6F3', line='#E4E2DC', head='#141412', text='#23231F', muted='#6F6E69', accent='#7A5A1E',
                  scale=['#EBE8E1', '#E6D3A6', '#CFAE67', '#A9823A', '#7A5A1E']),
}
FONT = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def gql(query, variables):
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    req = urllib.request.Request(API, data=json.dumps({'query': query, 'variables': variables}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json',
                                          'User-Agent': 'profile-stats'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get('errors'):
        raise RuntimeError(data['errors'][0].get('message'))
    return data['data']


def fetch_days(login):
    """Every day since the account was created, as {date: count}."""
    created = gql('query($l:String!){user(login:$l){createdAt}}', {'l': login})['user']['createdAt'][:10]
    start = dt.date.fromisoformat(created)
    today = dt.date.today()
    days = {}
    while start <= today:
        end = min(start + dt.timedelta(days=364), today)
        q = ('query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t)'
             '{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}')
        cal = gql(q, {'l': login, 'f': f'{start}T00:00:00Z', 't': f'{end}T23:59:59Z'})
        for w in cal['user']['contributionsCollection']['contributionCalendar']['weeks']:
            for d in w['contributionDays']:
                if start.isoformat() <= d['date'] <= end.isoformat():
                    days[d['date']] = d['contributionCount']
        start = end + dt.timedelta(days=1)
    return days


def summarise(days):
    today = dt.date.today()
    dates = sorted(days)
    last_year = [(today - dt.timedelta(days=i)).isoformat() for i in range(365)]
    total_year = sum(days.get(d, 0) for d in last_year)
    active_year = sum(1 for d in last_year if days.get(d, 0) > 0)
    longest = run = 0
    for d in (dt.date.fromisoformat(dates[0]) + dt.timedelta(days=i) for i in range((today - dt.date.fromisoformat(dates[0])).days + 1)) if dates else []:
        run = run + 1 if days.get(d.isoformat(), 0) > 0 else 0
        longest = max(longest, run)
    current, d = 0, today
    if days.get(d.isoformat(), 0) == 0:
        d -= dt.timedelta(days=1)  # today may not have started yet
    while days.get(d.isoformat(), 0) > 0:
        current += 1
        d -= dt.timedelta(days=1)
    best = max(((days.get(x, 0), x) for x in last_year), default=(0, ''))
    return dict(total_year=total_year, active_year=active_year, total_all=sum(days.values()), since=dates[0][:4] if dates else '',
                current=current, longest=longest, best_count=best[0], best_day=best[1])


def fmt(n):
    return f'{n:,}'


def card(title, subtitle, days, s, theme):
    t = THEMES[theme]
    w, h = 840, 300
    cell, gap = 11, 3
    today = dt.date.today()
    first = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)  # a Sunday, 53 columns back
    year = [days.get((first + dt.timedelta(days=i)).isoformat(), 0) for i in range((today - first).days + 1)]
    nonzero = sorted(c for c in year if c > 0)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)] if nonzero else [1, 2, 3]
    def level(c):
        if c <= 0:
            return 0
        return 1 + sum(c > x for x in cuts)
    rects = []
    for i, c in enumerate(year):
        col, row = divmod(i, 7)
        x, y = 28 + col * (cell + gap), 168 + row * (cell + gap)
        rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{t["scale"][level(c)]}"/>')
    stats = [(fmt(s['current']), 'day streak now'), (fmt(s['longest']), 'longest streak'),
             (f'{s["active_year"]}', 'active days, 12 months'), (fmt(s['total_all']), f'all-time since {s["since"]}')]
    cols = ''.join(
        f'<text x="{300 + i * 130}" y="78" font-size="22" font-weight="700" fill="{t["head"]}">{v}</text>'
        f'<text x="{300 + i * 130}" y="98" font-size="11.5" fill="{t["muted"]}">{lbl}</text>' for i, (v, lbl) in enumerate(stats))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}: {fmt(s['total_year'])} contributions in the last 12 months">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{t['bg']}" stroke="{t['line']}"/>
<g font-family="{FONT}">
<text x="28" y="40" font-size="12" font-weight="600" letter-spacing="1.6" fill="{t['accent']}">{title.upper()}</text>
<text x="28" y="88" font-size="46" font-weight="800" fill="{t['head']}">{fmt(s['total_year'])}</text>
<text x="28" y="112" font-size="13" fill="{t['text']}">contributions in the last 12 months</text>
{cols}
<text x="300" y="132" font-size="11.5" fill="{t['muted']}">{subtitle}</text>
{''.join(rects)}
<text x="{w - 28}" y="{h - 14}" font-size="10.5" text-anchor="end" fill="{t['muted']}">Updated {today:%d %b %Y}</text>
</g></svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--accounts', required=True)
    ap.add_argument('--out', default='stats')
    ap.add_argument('--combined', action='store_true')
    ap.add_argument('--label', action='append', default=[])
    ap.add_argument('--combined-title', default='Shipping every day')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    labels = dict(x.split('=', 1) for x in a.label)
    hist_path = out / 'history.json'
    history = json.loads(hist_path.read_text()) if hist_path.exists() else {}
    for login in a.accounts.split(','):
        try:
            fresh = fetch_days(login)
            saved = history.setdefault(login, {})
            for d, c in fresh.items():  # keep the highest count ever seen, so work that later disappears from the public calendar stays on record
                saved[d] = max(c, saved.get(d, 0))
        except Exception as e:  # keep the last good record if the account is gone or the API fails
            print(f'{login}: kept the saved history ({e})')
    hist_path.write_text(json.dumps(history, indent=0, sort_keys=True) + '\n')
    for login in a.accounts.split(','):
        days = history.get(login, {})
        if not days:
            continue
        s = summarise(days)
        name = labels.get(login, login)
        for theme in THEMES:
            (out / f'{login.lower()}-{theme}.svg').write_text(card(name, 'Daily contribution counts, public and private repositories', days, s, theme))
        print(login, s)
    if a.combined:
        merged = {}
        for login in a.accounts.split(','):
            for d, c in history.get(login, {}).items():
                merged[d] = merged.get(d, 0) + c
        s = summarise(merged)
        for theme in THEMES:
            (out / f'combined-{theme}.svg').write_text(card(a.combined_title, 'Work and studio accounts together, daily counts only', merged, s, theme))
        print('combined', s)


if __name__ == '__main__':
    main()
