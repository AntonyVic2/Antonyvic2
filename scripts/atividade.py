"""Gera assets/atividade.svg: contribuições do último ano em pixel + sequência atual e recorde.
Roda no GitHub Actions (GITHUB_TOKEN) todo dia; só biblioteca padrão."""
import json, os, urllib.request, datetime as dt

USER = os.environ.get("PERFIL_USER", "AntonyVic2")
Q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

def buscar():
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]

def sequencias(dias):
    hoje = dt.date.today().isoformat()
    cont = [c for d, c in dias if d <= hoje]
    rec = run = 0
    for c in cont:
        run = run + 1 if c else 0; rec = max(rec, run)
    atual, i = 0, len(cont) - 1
    if i >= 0 and cont[i] == 0: i -= 1          # hoje ainda sem commit não zera a sequência
    while i >= 0 and cont[i]: atual += 1; i -= 1
    return atual, rec

RAMPA = ["#2A121A", "#5E2838", "#A8304A", "#E5566F", "#F3A3B0"]
def nivel(c, mx):
    if c == 0: return 0
    return min(4, 1 + int(3 * c / max(mx, 1)))

def svg(total, semanas, atual, rec):
    dias = [d for w in semanas for d in w]
    mx = max([c for _, c in dias] or [1])
    C, G, x0, y0 = 11, 3, 40, 82
    cel = []
    meses, ult = [], None
    for i, w in enumerate(semanas):
        m = w[0][0][5:7]
        if m != ult:
            ult = m; meses.append(f'<text x="{x0+i*(C+G)}" y="{y0-8}">{["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"][int(m)-1]}</text>')
        for j, (d, c) in enumerate(w):
            dj = dt.date.fromisoformat(d).weekday(); r = (dj + 1) % 7
            cel.append(f'<rect class="c" style="animation-delay:{i*0.025:.2f}s" x="{x0+i*(C+G)}" y="{y0+r*(C+G)}" width="{C}" height="{C}" fill="{RAMPA[nivel(c,mx)]}"><title>{d}: {c}</title></rect>')
    fogo = ["....R....", "....RR...", "...RRR..R", "..RRRRR.R", ".RRRYRRRR", ".RRYYYRRR",
            "RRYYYYYRR", "RRYYWYYRR", "RRYYWWYRR", ".RRYYYYR.", "..RRRRR.."]
    cor = {"R": "#E5566F", "Y": "#E8B56A", "W": "#F6E7DC"}
    fx, fy = 468, 221                              # 33 px de altura, centrado no número (cap 226-252)
    fpx = "".join(f'<rect x="{fx+c*3}" y="{fy+r*3}" width="3" height="3" fill="{cor[v]}"/>'
                  for r, row in enumerate(fogo) for c, v in enumerate(row) if v != ".")
    W, H = 900, 300
    leg = "".join(f'<rect x="{770+k*14}" y="{y0+7*(C+G)+8}" width="10" height="10" fill="{c}"/>' for k, c in enumerate(RAMPA))
    def bloco(x, num, rot):
        return (f'<text class="n" x="{x}" y="252">{num}</text>'
                f'<text class="mono" x="{x}" y="274" font-size="12" fill="#F6E7DC" fill-opacity=".6">{rot}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contribuições no último ano; sequência atual {atual} dias; recorde {rec} dias">
<style>.mono{{font-family:Consolas,Menlo,'Courier New',monospace}}
.c{{animation:in .5s ease-out both}}@keyframes in{{from{{opacity:0}}}}
.n{{font-family:Consolas,Menlo,monospace;font-size:34px;font-weight:700;fill:#F6E7DC}}
.f{{animation:f 1.2s steps(2) infinite}}@keyframes f{{50%{{transform:translateY(-2px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="#140A0F" stroke="#4A1F2B"/>
<path d="M1 11a10 10 0 0 1 10-10h{W-22}a10 10 0 0 1 10 10v24H1z" fill="#2A121A"/>
<circle cx="24" cy="18" r="5" fill="#E5566F"/><circle cx="42" cy="18" r="5" fill="#E8B56A"/><circle cx="60" cy="18" r="5" fill="#F3A3B0"/>
<text class="mono" x="{W/2}" y="23" text-anchor="middle" font-size="12" fill="#F6E7DC" fill-opacity=".55">antony@dados: ~/atividade</text>
<g class="mono" font-size="11" fill="#F6E7DC" fill-opacity=".5">{"".join(meses)}</g>
{"".join(cel)}
<text class="mono" x="{x0}" y="{y0+7*(C+G)+17}" font-size="11" fill="#F6E7DC" fill-opacity=".5">último ano</text>
<text class="mono" x="740" y="{y0+7*(C+G)+17}" font-size="11" fill="#F6E7DC" fill-opacity=".5">−</text>{leg}<text class="mono" x="842" y="{y0+7*(C+G)+17}" font-size="11" fill="#F6E7DC" fill-opacity=".5">+</text>
<rect x="40" y="200" width="{W-80}" height="1" fill="#4A1F2B"/>
{bloco(40, total, "contribuições no ano")}
<g class="f">{fpx}</g>{bloco(506, atual, "dias seguidos agora")}
{bloco(720, rec, "maior sequência")}
</svg>'''

if __name__ == "__main__":
    total, semanas = buscar()
    a, r = sequencias([d for w in semanas for d in w])
    assert a <= r, (a, r)
    open(os.path.join(os.path.dirname(__file__), "..", "assets", "atividade.svg"), "w", encoding="utf-8").write(svg(total, semanas, a, r))
    print(total, a, r)
