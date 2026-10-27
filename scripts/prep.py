"""Build compact estimator data: live K26 turnout per ballot box x K25 bloc split of its twin box.
usage: python3 -I prep.py <repo_dir> <out.json>
"""
import csv, json, sys
from collections import defaultdict

repo, out = sys.argv[1], sys.argv[2]
BLOC = {'מחל': 'R', 'ט': 'R', 'שס': 'R', 'ג': 'R',
        'פה': 'L', 'כן': 'L', 'ל': 'L', 'אמת': 'L', 'מרצ': 'L',
        'עם': 'A', 'ום': 'A', 'ד': 'A'}
META = {'סמל ועדה', 'ברזל', 'שם ישוב', 'סמל ישוב', 'קלפי', 'ריכוז', 'שופט', 'בזב', 'מצביעים', 'פסולים', 'כשרים'}


def norm(b):
    b = str(b).strip()
    try:
        f = float(b)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return b


rows = list(csv.DictReader(open(f'{repo}/ballot25.csv', encoding='utf-8-sig')))
parties = [c for c in rows[0] if c not in META]
k25, bysett = {}, defaultdict(lambda: [0, 0, 0, 0])
nat = [0, 0, 0, 0]
IDX = {'R': 0, 'L': 1, 'A': 2, 'O': 3}
env = [0, 0, 0, 0]
elig25 = 0
for x in rows:
    elig25 += int(x['בזב'] or 0)
    if x['שם ישוב'].strip() == 'מעטפות חיצוניות':  # 2022 double-envelope votes (soldiers, diplomats, hospitals...)
        for p in parties:
            env[IDX[BLOC.get(p, 'O')]] += int(x[p] or 0)
    v = [0, 0, 0, 0]
    for p in parties:
        v[IDX[BLOC.get(p, 'O')]] += int(x[p] or 0)
    k25[(x['שם ישוב'].strip(), norm(x['קלפי']))] = v
    s = bysett[x['שם ישוב'].strip()]
    for i in range(4):
        s[i] += v[i]; nat[i] += v[i]

d = json.load(open(f'{repo}/site/data/turnout_day_26.json'))
# first pass: resolve shares; collect population-group averages
resolved = []
popavg = defaultdict(lambda: [0, 0, 0, 0])
for s in d['stations']:
    name, ballot, lat, lng, E, V, T, k25t, pace, win, bloc, pop, dist = s[:13]
    kn, kb = s[16], s[17]
    v, how = None, 2
    if kn and kb and (kn, norm(kb)) in k25:
        v, how = k25[(kn, norm(kb))], 0
    elif name in bysett:
        v, how = bysett[name], 1
    elif kn in bysett:
        v, how = bysett[kn], 1
    if v:
        for i in range(4):
            popavg[pop][i] += v[i]
    resolved.append((s, v, how))

stations = []
for s, v, how in resolved:
    name, ballot, lat, lng, E, V, T, k25t, pace, win, bloc, pop, dist = s[:13]
    if not v:
        v = popavg[pop] if sum(popavg[pop]) else nat
    tot = sum(v) or 1
    sh = [round(v[i] / tot * 1000) for i in range(3)]  # per-mille R,L,A ; O = remainder
    stations.append([name, ballot, round(lat, 4) if lat else None, round(lng, 4) if lng else None,
                     E or 0, V, k25t, dist, pop, sh[0], sh[1], sh[2], how])

n = d['national']
outd = {
    'as_of': d['meta']['as_of'],
    'national': {k: n[k] for k in ('eligible', 'voters', 'turnout', 'ballots')},
    'history': [{'as_of': h['as_of'], 'voters': h['national']['voters'], 'turnout': h['national']['turnout']}
                for h in d['history']],
    'historical': json.load(open(f'{repo}/site/data/historical_turnout.json'))['elections'],
    'k25_nat': nat,
    'k25_env': env,
    'k25_elig': elig25,
    'stations': stations,
}
json.dump(outd, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
print(out, len(stations), n['turnout'], d['meta']['as_of'])
