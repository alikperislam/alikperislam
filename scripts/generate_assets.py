"""
Profile README asset generator (hero + project cards, dark & light).

Edit CODE / CARDS below, then run from the repo root:
    pip install fonttools brotli
    python scripts/generate_assets.py

Fonts are subset to the exact characters used, so always regenerate
instead of editing text inside the SVGs by hand.
"""
import os, urllib.request
import base64, io, html
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset


FONT_URLS = {
  "fonts/bric.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf",
  "fonts/jbm.ttf":  "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}
os.makedirs("fonts", exist_ok=True)
for path, url in FONT_URLS.items():
    if not os.path.exists(path):
        print("downloading", path); urllib.request.urlretrieve(url, path)

FONTS = {
  # role: (file, axes)
  "display": ("fonts/bric.ttf", {"wght": 800, "wdth": 88, "opsz": 96}),
  "title":   ("fonts/bric.ttf", {"wght": 700, "wdth": 100, "opsz": 32}),
  "body":    ("fonts/bric.ttf", {"wght": 420, "wdth": 100, "opsz": 16}),
  "mono":    ("fonts/jbm.ttf",  {"wght": 450}),
  "monob":   ("fonts/jbm.ttf",  {"wght": 650}),
}
FALLBACK = {
  "display": "'Segoe UI', Helvetica, Arial, sans-serif",
  "title": "'Segoe UI', Helvetica, Arial, sans-serif",
  "body": "'Segoe UI', Helvetica, Arial, sans-serif",
  "mono": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
  "monob": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}
_inst = {}
def instance(role):
    if role not in _inst:
        f, axes = FONTS[role]
        _inst[role] = instancer.instantiateVariableFont(TTFont(f), axes)
    return _inst[role]

def font_face(role, text):
    font = instance(role)
    buf = io.BytesIO(); font.save(buf); buf.seek(0)
    f = TTFont(buf)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = []; opts.notdef_outline = True
    s = subset.Subsetter(opts); s.populate(text=text + " "); s.subset(f)
    out = io.BytesIO(); f.flavor = "woff2"; f.save(out)
    b64 = base64.b64encode(out.getvalue()).decode()
    return f"@font-face{{font-family:'{role}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"

THEMES = {
  "dark": dict(bg="#0A1626", border="#1B2D45", ink="#E8EEF6", soft="#B4C2D3", muted="#6F829B",
               accent="#5CC8FF", kw="#5CC8FF", type="#6EE7C8", str="#FFC46B", com="#6F829B", punc="#93A4BA"),
  "light": dict(bg="#F3F6FA", border="#DCE4EE", ink="#0C1B2E", soft="#3C4D63", muted="#7A8BA0",
               accent="#0A62C9", kw="#0A62C9", type="#0B8268", str="#B15C00", com="#8394A8", punc="#5A6B80"),
}
esc = lambda s: html.escape(s, quote=False)

def wrap_svg(w, h, title, css, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
<title>{esc(title)}</title>
<style>
{css}
</style>
{body}
</svg>
'''

# ---------------------------------------------------------------- hero
CODE = [  # list of (token_class, text)
  [("kw","final"),("id"," alikper "),("pu","= "),("ty","Developer"),("pu","(")],
  [("id","  role"),("pu",": "),("st","'Flutter Developer'"),("pu",",")],
  [("id","  team"),("pu",": "),("st","'PITON Technology'"),("pu",",")],
  [("id","  from"),("pu",": "),("st","'Eskişehir, TR'"),("pu",",")],
  [("id","  ships"),("pu",": ["),("id","android"),("pu",", "),("id","iOS"),("pu","],")],
  [("id","  packages"),("pu",": "),("kw","2"),("pu",", "),("co","// on pub.dev")],
  [("pu",");")],
]

def hero(theme):
    t = THEMES[theme]
    W, H = 1200, 420
    name1, name2 = "Alikper", "İslam"
    url = "alikperislam.appinionsoft.com"
    code_text = "".join(tx for line in CODE for _, tx in line) + "1234567"
    css = "\n".join([
        font_face("display", name1 + name2),
        font_face("body", url),
        font_face("mono", code_text),
    ])
    css += f"""
.name{{font-family:'display',{FALLBACK['display']};font-size:124px;letter-spacing:-3px;fill:{t['ink']}}}
.url{{font-family:'body',{FALLBACK['body']};font-size:22px;fill:{t['accent']}}}
.code{{font-family:'mono',{FALLBACK['mono']};font-size:23px}}
.ln{{fill:{t['muted']};opacity:.55}}
.kw{{fill:{t['kw']}}} .ty{{fill:{t['type']}}} .st{{fill:{t['str']}}} .co{{fill:{t['com']};font-style:italic}} .pu{{fill:{t['punc']}}} .id{{fill:{t['ink']}}}
.l{{opacity:0;animation:in .45s cubic-bezier(.2,.7,.2,1) forwards}}
.caret{{fill:{t['accent']};opacity:0;animation:blink 1.1s steps(1) 1.4s infinite}}
@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion: reduce){{.l{{animation:none;opacity:1}}.caret{{animation:none;opacity:1}}}}"""
    x_num, x_code, y0, lh = 626, 664, 112, 40
    lines = []
    for i, line in enumerate(CODE):
        y = y0 + i * lh
        spans = "".join(f'<tspan class="{c}">{esc(tx)}</tspan>' for c, tx in line)
        lines.append(f'<g class="l" style="animation-delay:{0.25 + i*0.12:.2f}s">'
                     f'<text class="code ln" x="{x_num}" y="{y}" text-anchor="end">{i+1}</text>'
                     f'<text class="code" x="{x_code}" y="{y}" xml:space="preserve">{spans}</text></g>')
    last_len = sum(len(tx) for _, tx in CODE[-1])
    caret_x = x_code + last_len * 23 * 0.6 + 4
    caret_y = y0 + (len(CODE)-1) * lh - 20
    body = f'''<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="{t['bg']}" stroke="{t['border']}" stroke-width="2"/>
<text class="name" x="60" y="182">{esc(name1)}</text>
<text class="name" x="60" y="300">{esc(name2)}</text>
<text class="url" x="66" y="{y0 + 6*lh}">{esc(url)}</text>
<path d="M{66 + 322} {y0 + 6*lh - 14} l9 -9 m-6 0 h6 v6" fill="none" stroke="{t['accent']}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<line x1="590" y1="84" x2="590" y2="{y0 + 6*lh + 8}" stroke="{t['border']}" stroke-width="2"/>
{chr(10).join(lines)}
<rect class="caret" x="{caret_x:.1f}" y="{caret_y}" width="12" height="26" rx="2"/>'''
    return wrap_svg(W, H, "Alikper İslam, Flutter Developer at PITON Technology", css, body)

# ---------------------------------------------------------------- cards
CARDS = [
  dict(slug="call-sound-controller", kind="pub.dev plugin", title="call_sound_controller", mono=True,
       desc=["Read and set the voice-call volume on", "Android straight from Flutter code."],
       tags="Flutter plugin  /  Android  /  MIT"),
  dict(slug="simple-dial-code", kind="pub.dev package", title="simple_dial_code", mono=True,
       desc=["Zero-dependency Dart lookup between ISO", "country codes and dial codes, both ways."],
       tags="Pure Dart  /  No dependencies  /  MIT"),
  dict(slug="catalog-app", kind="Flutter app, study case", title="Catalog app",
       desc=["Six screens on a feature-based MVVM setup,", "with caching, routing and localization."],
       tags="Riverpod  /  Dio  /  GetIt  /  go_router  /  Hive"),
  dict(slug="secure-auth-app", kind="Flutter app", title="Secure auth, end to end",
       desc=["Sign-up, sign-in and mail verification with", "AES-256 encrypted traffic and local storage."],
       tags="Provider  /  MVVM  /  Hive  /  AES-256"),
  dict(slug="auth-backend", kind="Node.js backend", title="Auth API",
       desc=["The backend behind the secure auth app:", "JWT sessions, bcrypt and mail verification."],
       tags="Express  /  MySQL  /  JWT  /  Nodemailer"),
  dict(slug="smart-room", kind="Flutter + IoT", title="Smart room",
       desc=["Live temperature and light data from an", "ESP32, visualized and automated in Flutter."],
       tags="Flutter  /  ESP32  /  Real-time sensors"),
]

def card(c, theme):
    t = THEMES[theme]
    W, H = 600, 230
    title_role = "monob" if c.get("mono") else "title"
    css = "\n".join([
        font_face(title_role, c["title"]),
        font_face("body", c["kind"] + "".join(c["desc"]) + c["tags"]),
    ])
    title_size = 30 if c.get("mono") else 33
    css += f"""
.kind{{font-family:'body',{FALLBACK['body']};font-size:17px;fill:{t['muted']}}}
.title{{font-family:'{title_role}',{FALLBACK[title_role]};font-size:{title_size}px;fill:{t['ink']};letter-spacing:{'-0.5px' if c.get('mono') else '-0.6px'}}}
.desc{{font-family:'body',{FALLBACK['body']};font-size:19.5px;fill:{t['soft']}}}
.tags{{font-family:'body',{FALLBACK['body']};font-size:17px;fill:{t['accent']}}}"""
    body = f'''<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="{t['bg']}" stroke="{t['border']}" stroke-width="2"/>
<text class="kind" x="34" y="50">{esc(c['kind'])}</text>
<path d="M548 46 l14 -14 m-10 0 h10 v10" fill="none" stroke="{t['muted']}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<text class="title" x="32" y="94">{esc(c['title'])}</text>
<text class="desc" x="34" y="136">{esc(c['desc'][0])}</text>
<text class="desc" x="34" y="163">{esc(c['desc'][1])}</text>
<text class="tags" x="34" y="202" xml:space="preserve">{esc(c['tags'])}</text>'''
    return wrap_svg(W, H, f"{c['title']}: {' '.join(c['desc'])}", css, body)

if __name__ == "__main__":
    out = "assets"; os.makedirs(f"{out}/cards", exist_ok=True)
    for th in THEMES:
        open(f"{out}/hero-{th}.svg", "w", encoding="utf-8").write(hero(th))
        for c in CARDS:
            open(f"{out}/cards/{c['slug']}-{th}.svg", "w", encoding="utf-8").write(card(c, th))
    print("done")
