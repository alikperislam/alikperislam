"""
Profile README asset generator (light design, one SVG per image).

Edit the CONTENT section, then run from the repo root:
    pip install fonttools brotli qrcode
    python scripts/generate_assets.py

Fonts are subset to the exact characters used, so always regenerate
instead of editing text inside the SVGs by hand.
"""
import base64, html, io, json, os, urllib.request

import qrcode
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "assets"

# ============================================================== CONTENT

HERO = dict(
    status="Mid. Flutter Developer at PITON Technology",
    first="Alikper", last="İslam", degree="M.Sc.",
    tagline=["Android and iOS apps in Flutter, built on", "Clean Architecture with Riverpod and Bloc."],
    file="alikper.dart",
    code=[
        [("kw", "final"), ("id", " alikper "), ("pu", "= "), ("ty", "FlutterDeveloper"), ("pu", "(")],
        [("id", "  level"), ("pu", ": "), ("st", "'Mid.'"), ("pu", ",")],
        [("id", "  team"), ("pu", ": "), ("st", "'PITON Technology'"), ("pu", ",")],
        [("id", "  architecture"), ("pu", ": "), ("ty", "CleanArchitecture"), ("pu", "(),")],
        [("id", "  state"), ("pu", ": ["), ("ty", "Riverpod"), ("pu", ", "), ("ty", "Bloc"), ("pu", "],")],
        [("id", "  ships"), ("pu", ": ["), ("id", "android"), ("pu", ", "), ("id", "iOS"), ("pu", "],")],
        [("pu", ");")],
    ],
    stats=[("7", "apps live on Google Play", "and the App Store"),
           ("2", "packages published", "on pub.dev"),
           ("50+", "public repositories", "on GitHub")],
)

TEPSIO = dict(
    label="Featured product",
    name="Tepsio",
    tagline=["QR menus, orders and staff management", "for restaurants and cafés."],
    features=[
        "AI menu import from a photo or PDF",
        "A QR code for every table",
        "Real-time orders with push alerts",
        "Roles, shifts and clock-in for staff",
        "Revenue and best-seller reports",
        "Multi-branch, Turkish and English",
    ],
    cta="Get it on Google Play",
    site="tepsio.com.tr",
    qr_url="https://tepsio.com.tr",
    tent=["Scan for the menu", "Table 4"],
    toast=["New order, table 4", "2 × Latte, 1 × Cheesecake"],
)

# Mirrors the real folder layout: presentation -> domain <- data
ARCH = [
    dict(folder="presentation", desc="Everything the user sees", color="violet",
         items=[("pages", "Screens, one per route"),
                ("providers", "Riverpod providers and Blocs"),
                ("states", "Immutable UI states"),
                ("widgets", "Reusable UI pieces")]),
    dict(folder="domain", desc="Business rules, plain Dart", color="mint",
         items=[("models", "Entities the app works with"),
                ("repositories", "Abstract contracts")]),
    dict(folder="data", desc="Where the data comes from", color="orange",
         items=[("DTOs", "API request and response shapes"),
                ("repositories", "Implement the domain contracts")]),
]
ARCH_ARROWS = ["depends on", "implements"]

TOOLBOX = [
    ("Mobile", [("flutter", "Flutter"), ("dart", "Dart"), ("android", "Android"), ("apple", "iOS")]),
    ("Architecture", [(None, "Clean Architecture"), (None, "Riverpod"), (None, "Bloc"), (None, "Repository pattern")]),
    ("Data", [(None, "Dio"), (None, "REST APIs"), ("firebase", "Firebase"), (None, "Hive")]),
    ("Backend", [("nodedotjs", "Node.js"), ("express", "Express"), ("mysql", "MySQL"), ("jsonwebtokens", "JWT")]),
    ("Shipping", [("googleplay", "Google Play"), ("appstore", "App Store"), ("figma", "Figma"), ("git", "Git")]),
    ("Earlier", [("dotnet", "C# and .NET"), ("python", "Python"), ("cplusplus", "C/C++"), ("espressif", "ESP32")]),
]

APPS = [
    dict(slug="enguide", glyph="enguide", tint="orange", kind="Education", title="Enguide",
         desc=["English exercises for all levels,", "on Android and iOS."],
         tags=[("googleplay", "Google Play"), ("appstore", "App Store")]),
    dict(slug="talkntrip", glyph="talk", tint="violet", kind="Communication", title="talkNtrip",
         desc=["Speak your own language and the other", "person hears theirs. 20 languages."],
         tags=[("googleplay", "Google Play"), ("appstore", "App Store")]),
    dict(slug="cappadocia-vpn", glyph="balloon", tint="mint", kind="Privacy", title="Cappadocia VPN",
         desc=["A VPN app for a private, secure", "connection on Android."],
         tags=[("googleplay", "Google Play")]),
    dict(slug="bg-cleaner", glyph="cutout", tint="pink", kind="Photo, AI", title="Bg Cleaner",
         desc=["AI background removal for photos,", "with no loss in image quality."],
         tags=[("appstore", "App Store")]),
]

CARDS = [
    dict(slug="call-sound-controller", icon="dart", kind="pub.dev plugin", title="call_sound_controller", mono=True,
         desc=["Read and set the voice-call volume on", "Android straight from Flutter code."],
         tags=[(None, "Flutter plugin"), (None, "Android"), (None, "MIT")]),
    dict(slug="simple-dial-code", icon="dart", kind="pub.dev package", title="simple_dial_code", mono=True,
         desc=["Zero-dependency Dart lookup between ISO", "country codes and dial codes, both ways."],
         tags=[(None, "Pure Dart"), (None, "No dependencies"), (None, "MIT")]),
    dict(slug="catalog-app", icon="flutter", kind="Flutter app, study case", title="Catalog app",
         desc=["Six screens, feature-based structure,", "with caching, routing and localization."],
         tags=[(None, "Riverpod"), (None, "Dio"), (None, "go_router"), (None, "Hive")]),
    dict(slug="secure-auth-app", icon="flutter", kind="Flutter app", title="Secure auth, end to end",
         desc=["Sign-up, sign-in and mail verification with", "AES-256 encrypted traffic and local storage."],
         tags=[(None, "AES-256"), (None, "Encrypted Hive"), (None, "Mail verification")]),
    dict(slug="auth-backend", icon="nodedotjs", kind="Node.js backend", title="Auth API",
         desc=["The backend behind the secure auth app:", "JWT sessions, bcrypt and mail verification."],
         tags=[(None, "Express"), (None, "MySQL"), (None, "JWT"), (None, "Nodemailer")]),
    dict(slug="smart-room", icon="espressif", kind="Flutter + IoT", title="Smart room",
         desc=["Live temperature and light data from an", "ESP32, visualized and automated in Flutter."],
         tags=[(None, "Flutter"), (None, "ESP32"), (None, "Real-time sensors")]),
]

BUTTONS = [
    ("portfolio", "globe", "Portfolio"),
    ("linkedin", "linkedin", "LinkedIn"),
    ("medium", "medium", "Medium"),
    ("google-play", "googleplay", "Google Play"),
    ("app-store", "appstore", "App Store"),
]

# ============================================================== THEME

T = dict(bg="#FFFFFF", tint="#F7F6FB", line="#E9E7F0", ink="#17161D", soft="#4D4B59", muted="#8E8B9A",
         violet="#6B4EFF", mint="#0FA37F", orange="#EE6A1F", pink="#E0457F", good="#12B76A",
         lilac="#DCD3FF", peach="#FFDCCB", sea="#CBEFE1",
         kw="#6B4EFF", ty="#0E9F74", st="#E35A0E", co="#A3A0AD", pu="#8E8B9A", id="#17161D")
BRAND = dict(flutter="#027DFD", dart="#0175C2", android="#22A564", apple="#17161D", firebase="#F57C00",
             nodedotjs="#4E8F3A", express="#17161D", mysql="#4479A1", jsonwebtokens="#17161D", figma="#F24E1E",
             git="#F03C2E", googleplay="#17161D", appstore="#0D96F6", dotnet="#512BD4", python="#3776AB",
             cplusplus="#00599C", espressif="#E7352C", medium="#17161D", linkedin="#0A66C2", globe="#6B4EFF")

ICONS = json.load(open(os.path.join(HERE, "icons.json")))
ICONS["globe"] = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.95a15.6 15.6 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.9 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a8.2 8.2 0 0 1 0-4h3.38a16.5 16.5 0 0 0 0 4H4.26zm.84 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.1 16zm2.95-8H5.1a7.99 7.99 0 0 1 4.33-3.56A15.6 15.6 0 0 0 8.05 8zM12 19.96A14.1 14.1 0 0 1 10.09 16h3.82A14.1 14.1 0 0 1 12 19.96zM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56zM16.36 14a16.5 16.5 0 0 0 0-4h3.38a8.2 8.2 0 0 1 0 4h-3.38z")
ICONS["linkedin"] = ("M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z")
FOLDER = "M2 6.5A2.5 2.5 0 0 1 4.5 4h4.38c.66 0 1.3.26 1.77.73L12.12 6.2c.19.19.44.3.71.3h6.67A2.5 2.5 0 0 1 22 9v8.5a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 17.5v-11z"

# ============================================================== FONTS

FONT_URLS = {
    "fonts/bric.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf",
    "fonts/jbm.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}
os.makedirs("fonts", exist_ok=True)
for p, u in FONT_URLS.items():
    if not os.path.exists(p):
        print("downloading", p); urllib.request.urlretrieve(u, p)

ROLES = {
    "display": ("fonts/bric.ttf", {"wght": 800, "wdth": 88, "opsz": 96}),
    "title": ("fonts/bric.ttf", {"wght": 700, "wdth": 100, "opsz": 32}),
    "medium": ("fonts/bric.ttf", {"wght": 580, "wdth": 100, "opsz": 18}),
    "body": ("fonts/bric.ttf", {"wght": 420, "wdth": 100, "opsz": 16}),
    "mono": ("fonts/jbm.ttf", {"wght": 450}),
    "monob": ("fonts/jbm.ttf", {"wght": 650}),
}
SANS = "'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
_fonts = {}

def font(role):
    if role not in _fonts:
        f, axes = ROLES[role]
        _fonts[role] = instancer.instantiateVariableFont(TTFont(f), axes)
    return _fonts[role]

def measure(role, size, s):
    f = font(role); cmap = f.getBestCmap(); hmtx = f["hmtx"]; upm = f["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap[32])][0] for c in s) * size / upm

def face(role, text):
    buf = io.BytesIO(); font(role).save(buf); buf.seek(0)
    f = TTFont(buf)
    o = subset.Options(); o.flavor = "woff2"; o.layout_features = ["kern", "liga", "calt"]; o.name_IDs = []
    s = subset.Subsetter(o); s.populate(text=text + " "); s.subset(f)
    out = io.BytesIO(); f.flavor = "woff2"; f.save(out)
    fam = MONO if role.startswith("mono") else SANS
    b64 = base64.b64encode(out.getvalue()).decode()
    return f"@font-face{{font-family:'{role}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}", fam

# ============================================================== SVG BUILDER

esc = lambda s: html.escape(s, quote=False)

class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.parts = []; self.used = {}; self.css = []
        self.add('<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%">'
                 '<feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#2A2250" flood-opacity=".08"/></filter>'
                 '<filter id="sh2" x="-20%" y="-20%" width="140%" height="160%">'
                 '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#2A2250" flood-opacity=".14"/></filter></defs>')
    def add(self, s): self.parts.append(s)
    def text(self, role, size, x, y, s, fill, anchor="start", extra="", cls=""):
        self.used[role] = self.used.get(role, "") + s
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        c = f' class="{cls}"' if cls else ""
        self.add(f'<text{c} x="{x:.1f}" y="{y:.1f}" font-family="{role}" font-size="{size}" fill="{fill}"{a}{extra}>{esc(s)}</text>')
    def spans(self, role, size, x, y, tokens):
        self.used[role] = self.used.get(role, "") + "".join(t for _, t in tokens)
        sp = "".join(f'<tspan fill="{T[c]}">{esc(t)}</tspan>' for c, t in tokens)
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{role}" font-size="{size}" xml:space="preserve">{sp}</text>')
    def icon(self, name, x, y, size, fill, d=None):
        self.add(f'<path transform="translate({x:.1f} {y:.1f}) scale({size/24:.4f})" d="{d or ICONS[name]}" fill="{fill}"/>')
    def render(self):
        faces, rules = [], []
        for role, txt in self.used.items():
            ff, fam = face(role, txt); faces.append(ff)
            rules.append(f"text[font-family='{role}']{{font-family:'{role}',{fam}}}")
        css = "\n".join(faces + rules + self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{html.escape(self.title)}">\n<title>{esc(self.title)}</title>\n<style>\n{css}\n</style>\n'
                + "\n".join(self.parts) + "\n</svg>\n")

M = 10  # outer margin so the drop shadow is not clipped

def frame(s, rx=26, fill=None):
    s.add(f'<rect x="{M}" y="{M-4}" width="{s.w-2*M}" height="{s.h-2*M}" rx="{rx}" fill="{fill or T["bg"]}" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh)"/>')
    s.add(f'<clipPath id="clip"><rect x="{M}" y="{M-4}" width="{s.w-2*M}" height="{s.h-2*M}" rx="{rx}"/></clipPath>')

def blob(s, gid, cx, cy, r, color, op=0.9):
    s.add(f'<defs><radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse">'
          f'<stop offset="0" stop-color="{color}" stop-opacity="{op}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
          f'</radialGradient></defs><rect x="0" y="0" width="{s.w}" height="{s.h}" fill="url(#{gid})" clip-path="url(#clip)"/>')

def dots(s, x, y, w, h, op=0.7):
    s.add(f'<defs><pattern id="dp" width="22" height="22" patternUnits="userSpaceOnUse">'
          f'<circle cx="2" cy="2" r="1.3" fill="{T["line"]}"/></pattern></defs>'
          f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#dp)" opacity="{op}" clip-path="url(#clip)"/>')

def arrow_out(s, x, y, color):
    s.add(f'<path transform="translate({x} {y})" d="M0 14 L14 0 M4 0 H14 V10" fill="none" stroke="{color}" '
          f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')

def chip(s, x, y, label, icon=None, size=16, h=32, fg=None, bg=None, border=None, icolor=None):
    pad = 13; isz = size + 2
    w = measure("medium", size, label) + pad * 2 + (isz + 7 if icon else 0)
    b = f' stroke="{border}" stroke-width="1.2"' if border else ""
    s.add(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{bg or T["tint"]}"{b}/>')
    tx = x + pad
    if icon:
        s.icon(icon, x + pad, y + (h - isz) / 2, isz, icolor or BRAND.get(icon, T["ink"])); tx += isz + 7
    s.text("medium", size, tx, y + h / 2 + size * 0.36, label, fg or T["soft"])
    return w

# ============================================================== HERO

def hero():
    W, H = 1200, 620
    s = SVG(W, H, f"{HERO['first']} {HERO['last']}, {HERO['degree']}. {HERO['status']}")
    frame(s, 30)
    blob(s, "b1", 1060, 80, 480, T["lilac"])
    blob(s, "b2", 760, 560, 380, T["sea"], .8)
    blob(s, "b3", 40, 40, 360, T["peach"], .75)
    dots(s, M, M, W - 2 * M, H - 2 * M, .55)

    pw = measure("medium", 17, HERO["status"]) + 58
    s.add(f'<rect x="64" y="60" width="{pw:.0f}" height="38" rx="19" fill="{T["bg"]}" stroke="{T["line"]}" stroke-width="1.5"/>')
    s.add(f'<circle cx="86" cy="79" r="9" fill="{T["good"]}" opacity=".18"/><circle cx="86" cy="79" r="4.5" fill="{T["good"]}"/>')
    s.text("medium", 17, 104, 85, HERO["status"], T["soft"])

    s.text("display", 126, 58, 226, HERO["first"], T["ink"], extra=' letter-spacing="-3"')
    s.text("display", 126, 58, 344, HERO["last"], T["ink"], extra=' letter-spacing="-3"')
    lw = measure("display", 126, HERO["last"]) - 3 * len(HERO["last"])
    s.text("title", 30, 58 + lw + 18, 344, HERO["degree"], T["violet"])
    for i, line in enumerate(HERO["tagline"]):
        s.text("body", 22, 64, 398 + i * 31, line, T["soft"])

    px, py, pw2, ph = 636, 60, 500, 376
    s.add(f'<rect x="{px}" y="{py}" width="{pw2}" height="{ph}" rx="20" fill="{T["bg"]}" fill-opacity=".92" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh)"/>')
    s.add(f'<line x1="{px}" y1="{py+52}" x2="{px+pw2}" y2="{py+52}" stroke="{T["line"]}" stroke-width="1.5"/>')
    s.icon("dart", px + 22, py + 16, 20, BRAND["dart"])
    s.text("mono", 16, px + 52, py + 32, HERO["file"], T["muted"])
    y0, lh, fs = py + 98, 37, 19
    for i, line in enumerate(HERO["code"]):
        y = y0 + i * lh
        s.add(f'<g class="l" style="animation-delay:{0.25 + i*0.11:.2f}s">')
        s.text("mono", fs, px + 40, y, str(i + 1), T["muted"], anchor="end", extra=' opacity=".55"')
        s.spans("mono", fs, px + 58, y, line)
        s.add("</g>")
    last = "".join(tx for _, tx in HERO["code"][-1])
    cx = px + 58 + measure("mono", fs, last) + 4
    s.add(f'<rect class="caret" x="{cx:.1f}" y="{y0 + (len(HERO["code"])-1)*lh - 17}" width="10" height="22" rx="2" fill="{T["violet"]}"/>')

    sy = 486
    s.add(f'<rect x="54" y="{sy}" width="{W-108}" height="92" rx="20" fill="{T["bg"]}" fill-opacity=".85" stroke="{T["line"]}" stroke-width="1.5"/>')
    cw = (W - 108) / len(HERO["stats"])
    for i, (num, l1, l2) in enumerate(HERO["stats"]):
        x = 54 + i * cw
        if i: s.add(f'<line x1="{x:.0f}" y1="{sy+20}" x2="{x:.0f}" y2="{sy+72}" stroke="{T["line"]}" stroke-width="1.5"/>')
        nx = x + 30
        s.text("display", 50, nx, sy + 64, num, T["violet"] if i == 0 else T["ink"], extra=' letter-spacing="-1"')
        lx = nx + measure("display", 50, num) - len(num) + 16
        s.text("body", 17, lx, sy + 42, l1, T["soft"])
        s.text("body", 17, lx, sy + 65, l2, T["muted"])

    s.css.append(""".l{opacity:0;animation:in .45s cubic-bezier(.2,.7,.2,1) forwards}
.caret{opacity:0;animation:blink 1.1s steps(1) 1.3s infinite}
@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
@media (prefers-reduced-motion: reduce){.l{animation:none;opacity:1}.caret{animation:none;opacity:1}}""")
    return s.render()

# ============================================================== TEPSIO

def qr_path(data, x, y, size):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    q.add_data(data); q.make(fit=True)
    m = q.get_matrix(); n = len(m); c = size / n
    return "".join(f"M{x + j*c:.2f} {y + i*c:.2f}h{c:.2f}v{c:.2f}h-{c:.2f}z"
                   for i, row in enumerate(m) for j, v in enumerate(row) if v)

def tepsio():
    W, H = 1200, 540
    P = TEPSIO
    s = SVG(W, H, f"{P['name']}: {' '.join(P['tagline'])}")
    frame(s)
    blob(s, "b1", 1000, 250, 440, T["peach"])
    blob(s, "b2", 1150, 520, 300, T["lilac"], .7)
    dots(s, 780, M, 410, H - 2 * M, .6)

    s.icon("googleplay", 58, 52, 20, T["orange"])
    s.text("medium", 18, 88, 69, P["label"], T["orange"])
    s.text("display", 92, 54, 158, P["name"], T["ink"], extra=' letter-spacing="-2"')
    for i, line in enumerate(P["tagline"]):
        s.text("body", 24, 58, 204 + i * 32, line, T["soft"])
    for i, f in enumerate(P["features"]):
        x = [58, 440][i // 3]; y = 302 + (i % 3) * 44
        s.add(f'<circle cx="{x+11}" cy="{y-6}" r="11" fill="{T["mint"]}" opacity=".14"/>'
              f'<path d="M{x+6} {y-6} l3.5 3.5 l6.5 -7" fill="none" stroke="{T["mint"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
        s.text("body", 19, x + 32, y, f, T["ink"])
    bw = measure("medium", 18, P["cta"]) + 70
    s.add(f'<rect x="58" y="{H-100}" width="{bw:.0f}" height="48" rx="24" fill="{T["ink"]}"/>')
    s.icon("googleplay", 78, H - 87, 22, "#FFFFFF")
    s.text("medium", 18, 110, H - 70, P["cta"], "#FFFFFF")
    s.text("body", 18, 58 + bw + 22, H - 70, P["site"], T["muted"])

    tx, ty, tw, th = 880, 64, 240, 320
    s.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="24" fill="#FFFFFF" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh2)"/>')
    s.text("medium", 17, tx + tw / 2, ty + 46, P["tent"][0], T["muted"], anchor="middle")
    q = 168
    s.add(f'<path d="{qr_path(P["qr_url"], tx + (tw-q)/2, ty + 70, q)}" fill="{T["ink"]}"/>')
    s.text("title", 26, tx + tw / 2, ty + th - 36, P["tent"][1], T["ink"], anchor="middle")

    ox, oy, ow, oh = 812, 356, 300, 76
    s.add(f'<g class="toast"><rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="18" fill="#FFFFFF" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh2)"/>'
          f'<circle cx="{ox+34}" cy="{oy+38}" r="16" fill="{T["orange"]}" opacity=".15"/><circle cx="{ox+34}" cy="{oy+38}" r="6" fill="{T["orange"]}"/>')
    s.text("medium", 17, ox + 62, oy + 33, P["toast"][0], T["ink"])
    s.text("body", 15, ox + 62, oy + 56, P["toast"][1], T["muted"])
    s.add("</g>")
    s.css.append(""".toast{opacity:0;animation:pop .5s cubic-bezier(.2,.8,.2,1) .6s forwards}
@keyframes pop{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){.toast{animation:none;opacity:1}}""")
    return s.render()

# ============================================================== ARCHITECTURE

def architecture():
    W, H = 1200, 470
    s = SVG(W, H, "Clean Architecture folder layout: presentation (pages, providers, states, widgets) depends on domain (models, repositories); data (DTOs, repositories) implements domain")
    frame(s)
    dots(s, M, M, W - 2 * M, H - 2 * M, .5)
    cw, gap, x0, y0, ch = 336, 56, 48, 42, 382
    for i, L in enumerate(ARCH):
        x = x0 + i * (cw + gap); col = T[L["color"]]
        s.add(f'<rect x="{x}" y="{y0}" width="{cw}" height="{ch}" rx="22" fill="{T["bg"]}" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh)"/>')
        s.add(f'<rect x="{x+24}" y="{y0+24}" width="44" height="44" rx="13" fill="{col}" opacity=".12"/>')
        s.icon(None, x + 33, y0 + 33, 26, col, d=FOLDER)
        s.text("monob", 23, x + 82, y0 + 46, L["folder"], T["ink"])
        s.text("body", 16, x + 82, y0 + 68, L["desc"], T["muted"])
        n = len(L["items"]); ih, ig = 60, 12
        iy = y0 + 96
        for j, (name, sub) in enumerate(L["items"]):
            yy = iy + j * (ih + ig)
            s.add(f'<rect x="{x+18}" y="{yy}" width="{cw-36}" height="{ih}" rx="14" fill="{T["tint"]}"/>')
            s.icon(None, x + 32, yy + 18, 22, col, d=FOLDER)
            s.text("mono", 17, x + 64, yy + 26, name, T["ink"])
            s.text("body", 15, x + 64, yy + 47, sub, T["muted"])
    ay = y0 + 160
    for k, (xa, xb) in enumerate([(x0 + cw + 8, x0 + cw + gap - 8), (x0 + 2 * cw + 2 * gap - 8, x0 + 2 * cw + gap + 8)]):
        d = 1 if xb > xa else -1
        s.add(f'<line x1="{xa}" y1="{ay}" x2="{xb - d*3}" y2="{ay}" stroke="{T["soft"]}" stroke-width="2.2" stroke-linecap="round"/>'
              f'<path d="M{xb - d*10} {ay-7} L{xb} {ay} L{xb - d*10} {ay+7}" fill="none" stroke="{T["soft"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
        mx = (xa + xb) / 2
        s.add(f'<g transform="rotate(-90 {mx} {ay + 70})">')
        s.text("body", 14, mx, ay + 75, ARCH_ARROWS[k], T["muted"], anchor="middle")
        s.add("</g>")
    return s.render()

# ============================================================== TOOLBOX

def toolbox():
    W = 1200; rh, top = 70, 40
    H = top * 2 + rh * len(TOOLBOX) - 6
    s = SVG(W, H, "Toolbox: " + "; ".join(f"{g}: {', '.join(n for _, n in items)}" for g, items in TOOLBOX))
    frame(s)
    for r, (group, items) in enumerate(TOOLBOX):
        y = top + r * rh; faded = group == "Earlier"
        if r: s.add(f'<line x1="44" y1="{y - 12}" x2="{W-44}" y2="{y - 12}" stroke="{T["line"]}" stroke-width="1"/>')
        s.text("medium", 19, 52, y + 30, group, T["muted"] if faded else T["soft"])
        x = 240
        s.add('<g opacity=".6">' if faded else "<g>")
        for slug, name in items:
            if slug:
                w = chip(s, x, y, name, icon=slug, size=19, h=46, fg=T["ink"], bg=T["bg"], border=T["line"])
            else:
                pad = 13; w = measure("medium", 19, name) + pad * 2 + 18
                s.add(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="46" rx="23" fill="{T["bg"]}" stroke="{T["line"]}" stroke-width="1.2"/>')
                s.add(f'<circle cx="{x+pad+5:.0f}" cy="{y+23}" r="5" fill="{T["violet"]}"/>')
                s.text("medium", 19, x + pad + 18, y + 30, name, T["ink"])
            x += w + 14
        s.add("</g>")
    return s.render()

# ============================================================== CARDS

def glyph(s, kind, x, y, col):
    if kind == "enguide":
        s.text("title", 24, x + 28, y + 37, "Aa", col, anchor="middle")
    elif kind == "talk":
        s.add(f'<path d="M{x+12} {y+14} h20 a5 5 0 0 1 5 5 v10 a5 5 0 0 1 -5 5 h-11 l-6 5 v-5 h-3 a5 5 0 0 1 -5 -5 v-10 a5 5 0 0 1 5 -5z" fill="{col}"/>'
              f'<path d="M{x+40} {y+24} h3 a5 5 0 0 1 5 5 v9 a5 5 0 0 1 -5 5 h-1 v5 l-6 -5 h-8 a4 4 0 0 1 -4 -3" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>')
    elif kind == "balloon":
        s.add(f'<path d="M{x+28} {y+9} c9 0 15 7 15 15 c0 8 -7 14 -11 19 h-8 c-4 -5 -11 -11 -11 -19 c0 -8 6 -15 15 -15z" fill="{col}"/>'
              f'<path d="M{x+28} {y+9} c-4 4 -5 10 -5 15 c0 7 2 13 3 19 M{x+28} {y+9} c4 4 5 10 5 15 c0 7 -2 13 -3 19" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity=".7"/>'
              f'<rect x="{x+24}" y="{y+45}" width="8" height="6" rx="1.5" fill="{col}"/>')
    elif kind == "cutout":
        c = 6
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 0:
                    s.add(f'<rect x="{x+16+j*c}" y="{y+16+i*c}" width="{c}" height="{c}" fill="{col}" opacity=".35"/>')
        s.add(f'<circle cx="{x+30}" cy="{y+26}" r="6" fill="{col}"/><path d="M{x+20} {y+42} c2 -7 6 -10 10 -10 s8 3 10 10z" fill="{col}"/>'
              f'<path d="M{x+42} {y+10} l1.6 3.8 3.8 1.6 -3.8 1.6 -1.6 3.8 -1.6 -3.8 -3.8 -1.6 3.8 -1.6z" fill="{col}"/>')

def card(c, app=False):
    W, H = 600, 264
    s = SVG(W, H, f"{c['title']}: {' '.join(c['desc'])}")
    frame(s, 22)
    if app:
        col = T[c["tint"]]
        s.add(f'<rect x="34" y="30" width="56" height="56" rx="16" fill="{col}" opacity=".12"/>')
        glyph(s, c["glyph"], 34, 30, col)
        s.text("title", 30, 106, 60, c["title"], T["ink"], extra=' letter-spacing="-.5"')
        s.text("medium", 16, 107, 83, c["kind"], T["muted"])
        ty0 = 132
    else:
        col = BRAND[c["icon"]]
        s.add(f'<rect x="34" y="30" width="40" height="40" rx="12" fill="{col}" opacity=".1"/>')
        s.icon(c["icon"], 43, 39, 22, col)
        s.text("medium", 17, 88, 56, c["kind"], T["muted"])
        role = "monob" if c.get("mono") else "title"
        s.text(role, 28 if c.get("mono") else 31, 34, 112, c["title"], T["ink"], extra=' letter-spacing="-.5"')
        ty0 = 150
    arrow_out(s, 548, 36, T["muted"])
    for i, line in enumerate(c["desc"]):
        s.text("body", 19, 36, ty0 + i * 27, line, T["soft"])
    x = 34
    for icon, tag in c["tags"]:
        if app:
            w = chip(s, x, 202, tag, icon=icon, size=15.5, h=34, fg=T["ink"], bg=T["bg"], border=T["line"])
        else:
            w = chip(s, x, 204, tag, size=15.5, h=32, fg=T["violet"], bg="#F0EDFF")
        x += w + 8
    return s.render()

# ============================================================== BUTTONS

def button(label, icon):
    w = int(measure("medium", 17, label) + 78); H = 60
    s = SVG(w, H, label)
    s.add(f'<rect x="4" y="3" width="{w-8}" height="{H-12}" rx="{(H-12)/2}" fill="{T["bg"]}" stroke="{T["line"]}" stroke-width="1.5" filter="url(#sh)"/>')
    s.icon(icon, 22, 16, 22, BRAND.get(icon, T["ink"]))
    s.text("medium", 17, 56, 33, label, T["ink"])
    return s.render()

# ============================================================== MAIN

if __name__ == "__main__":
    for d in ("", "/cards", "/apps", "/buttons"):
        os.makedirs(OUT + d, exist_ok=True)
    jobs = {"hero.svg": hero(), "tepsio.svg": tepsio(), "architecture.svg": architecture(), "toolbox.svg": toolbox()}
    for c in CARDS: jobs[f"cards/{c['slug']}.svg"] = card(c)
    for a in APPS: jobs[f"apps/{a['slug']}.svg"] = card(a, app=True)
    for slug, icon, label in BUTTONS: jobs[f"buttons/{slug}.svg"] = button(label, icon)
    for name, svg in jobs.items():
        open(f"{OUT}/{name}", "w", encoding="utf-8").write(svg)
    print("done", len(jobs))
