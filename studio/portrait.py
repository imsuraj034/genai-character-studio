"""Concept-art generator: draws an SVG character portrait from the character data.

The art is built from the SAME validated fields (faction, palette, class, build,
element, personality, role), so it cannot drift from the Game Bible. Each
`variant` gives a different take (hair, skin, pose details) for the designer to pick from.
"""
import base64
import math
import random

SWATCH = {
    "silver": "#c0c0c8", "pale blue": "#a9cbe8", "white": "#f4f4f4", "steel grey": "#71797e",
    "crimson": "#b3122e", "ember orange": "#e8692b", "charcoal": "#36454f", "gold": "#d4a72c",
    "moss green": "#6b8e3d", "bark brown": "#6b4423", "amber": "#ffbf00", "cream": "#f3e5c0",
    "teal": "#1b8a8a", "deep navy": "#1b2a4a", "pearl": "#eae0c8", "sea green": "#2e8b57",
    "hot pink": "#ff3ea5", "lime green": "#7fff00", "purple": "#7b3fbf",
}
ELEMENT_COLOR = {"ice": "#9fe3ff", "fire": "#ff7b29", "nature": "#7ddf64", "earth": "#c49a6c",
                 "water": "#3fc1d9", "storm": "#ffe45c", "aether": "#c9a2ff"}
SKIN = ["#f1c9a5", "#e0ac83", "#c68c5f", "#a26b44", "#7a4a2b", "#f6d8c3"]
HAIR = ["#2b1d14", "#5a3a22", "#a8672f", "#d9b56b", "#e8e8e8", "#3b3b4f", "#8b1e1e", "#1f3b5c"]
SCENES = {
    "Frost Clan": ("#0f1d33", "#6f9cc7"),
    "Ember Covenant": ("#1c0f0f", "#a8321c"),
    "Verdant Circle": ("#0f2414", "#7a8f3a"),
    "Tidecallers": ("#0a1a2e", "#1f7f8f"),
}


def _hex(name, default="#888888"):
    return SWATCH.get(str(name).lower(), default)


def _background(faction, uid, r):
    top, bottom = SCENES.get(faction, ("#1a1a2a", "#555577"))
    s = [f'<defs><linearGradient id="{uid}bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
         f'<radialGradient id="{uid}aura"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/>'
         f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="360" height="460" fill="url(#{uid}bg)"/>']
    if faction == "Frost Clan":
        for x, h in [(20, 170), (85, 230), (150, 150), (230, 210), (300, 180)]:
            s.append(f'<polygon points="{x - 45},330 {x},{330 - h} {x + 45},330" fill="#dce9f5" opacity=".28"/>')
            s.append(f'<polygon points="{x - 12},{330 - h + 40} {x},{330 - h} {x + 12},{330 - h + 40}" fill="#fff" opacity=".5"/>')
        for _ in range(28):
            s.append(f'<circle cx="{r.randint(0, 360)}" cy="{r.randint(0, 330)}" r="{r.choice([1, 1.5, 2])}" fill="#fff" opacity=".7"/>')
    elif faction == "Ember Covenant":
        s.append('<polygon points="40,330 150,150 175,165 200,150 320,330" fill="#2a1010" opacity=".8"/>')
        s.append('<polygon points="150,150 175,165 200,150 190,200 160,200" fill="#ff7b29" opacity=".7"/>')
        s.append('<ellipse cx="175" cy="140" rx="60" ry="25" fill="#ff7b29" opacity=".18"/>')
        for _ in range(24):
            s.append(f'<circle cx="{r.randint(0, 360)}" cy="{r.randint(40, 330)}" r="{r.choice([1, 1.5, 2.5])}" fill="#ffb347" opacity=".8"/>')
    elif faction == "Verdant Circle":
        for x in [25, 95, 270, 335]:
            h = r.randint(150, 230)
            s.append(f'<rect x="{x - 7}" y="{330 - h}" width="14" height="{h}" fill="#3b2a18" opacity=".7"/>')
            s.append(f'<circle cx="{x}" cy="{330 - h}" r="{r.randint(38, 55)}" fill="#2f5d2a" opacity=".75"/>')
        for _ in range(16):
            x, y = r.randint(0, 360), r.randint(30, 330)
            s.append(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="2" fill="#ffbf00" opacity=".7" transform="rotate({r.randint(0, 180)} {x} {y})"/>')
    elif faction == "Tidecallers":
        for i, y in enumerate([250, 280, 310]):
            s.append(f'<path d="M0 {y} Q45 {y - 18} 90 {y} T180 {y} T270 {y} T360 {y} V460 H0Z" '
                     f'fill="#3fc1d9" opacity="{.12 + i * .08}"/>')
        for _ in range(18):
            s.append(f'<circle cx="{r.randint(0, 360)}" cy="{r.randint(30, 330)}" r="{r.choice([2, 3, 4])}" '
                     f'fill="none" stroke="#bff3ff" stroke-width="1" opacity=".6"/>')
    s.append('<rect y="330" width="360" height="130" fill="#000" opacity=".25"/>')
    return s


def _emblem(faction, cx, cy, size, color):
    k = size / 10
    if faction == "Frost Clan":
        return "".join(f'<line x1="{cx}" y1="{cy - 10 * k}" x2="{cx}" y2="{cy + 10 * k}" stroke="{color}" '
                       f'stroke-width="{2 * k}" transform="rotate({a} {cx} {cy})"/>' for a in (0, 60, 120))
    if faction == "Ember Covenant":
        return (f'<path d="M{cx} {cy - 11 * k} Q{cx + 9 * k} {cy} {cx + 5 * k} {cy + 8 * k} Q{cx} {cy + 11 * k} '
                f'{cx - 5 * k} {cy + 8 * k} Q{cx - 9 * k} {cy} {cx} {cy - 11 * k}Z" fill="{color}"/>')
    if faction == "Verdant Circle":
        return (f'<path d="M{cx} {cy - 10 * k} Q{cx + 10 * k} {cy} {cx} {cy + 10 * k} Q{cx - 10 * k} {cy} {cx} {cy - 10 * k}Z" '
                f'fill="{color}"/><line x1="{cx}" y1="{cy - 8 * k}" x2="{cx}" y2="{cy + 10 * k}" stroke="#00000055" stroke-width="{k}"/>')
    return (f'<path d="M{cx - 10 * k} {cy + 2 * k} Q{cx - 5 * k} {cy - 6 * k} {cx} {cy + 2 * k} T{cx + 10 * k} {cy + 2 * k}" '
            f'fill="none" stroke="{color}" stroke-width="{2.4 * k}"/>')


def _weapon(cls, hx, hy, lx, ly, elem, uid, faction, accent):
    metal = "#d7dde5"
    wood = "#6b4423"
    if cls == "Warrior":
        return (f'<rect x="{hx - 3}" y="{hy - 120}" width="7" height="112" rx="2" fill="{metal}" stroke="#555" stroke-width="1"/>'
                f'<rect x="{hx - 14}" y="{hy - 10}" width="29" height="6" rx="2" fill="{accent}"/>'
                f'<rect x="{hx - 3}" y="{hy - 4}" width="7" height="18" fill="{wood}"/>'
                f'<circle cx="{lx - 4}" cy="{ly}" r="30" fill="{accent}" stroke="{metal}" stroke-width="4"/>'
                + _emblem(faction, lx - 4, ly, 16, metal))
    if cls in ("Mage", "Healer"):
        top = (f'<circle cx="{hx}" cy="{hy - 150}" r="26" fill="url(#{uid}aura)"/>'
               f'<circle cx="{hx}" cy="{hy - 150}" r="11" fill="{elem}" stroke="#fff" stroke-width="1.5"/>')
        if cls == "Healer":
            top += (f'<path d="M{hx} {hy - 175} Q{hx + 16} {hy - 160} {hx} {hy - 140} Q{hx - 16} {hy - 160} {hx} {hy - 175}Z" '
                    f'fill="#7ddf64" opacity=".85"/>')
        return f'<line x1="{hx}" y1="{hy - 140}" x2="{hx}" y2="{hy + 95}" stroke="{wood}" stroke-width="7" stroke-linecap="round"/>' + top
    if cls == "Rogue":
        return "".join(f'<path d="M{x} {y} L{x + d * 6} {y - 46} L{x + d * 12} {y}Z" fill="{metal}" stroke="#555"/>'
                       f'<rect x="{x - 2}" y="{y}" width="16" height="5" fill="{accent}" transform="translate({-2 if d > 0 else -14} 0)"/>'
                       for x, y, d in [(hx - 4, hy, 1), (lx + 4, ly, -1)])
    if cls == "Ranger":
        return (f'<path d="M{lx - 6} {ly - 95} Q{lx - 55} {ly} {lx - 6} {ly + 95}" fill="none" stroke="{wood}" stroke-width="6"/>'
                f'<line x1="{lx - 6}" y1="{ly - 95}" x2="{lx - 6}" y2="{ly + 95}" stroke="#eee" stroke-width="1.2"/>'
                f'<line x1="{hx + 10}" y1="{hy - 70}" x2="{hx + 22}" y2="{hy + 10}" stroke="{wood}" stroke-width="3"/>')
    # Bard - lute
    return (f'<line x1="{hx - 10}" y1="{hy - 10}" x2="{hx + 40}" y2="{hy - 80}" stroke="{wood}" stroke-width="6"/>'
            f'<ellipse cx="{hx - 18}" cy="{hy + 6}" rx="22" ry="28" fill="#a8672f" stroke="#6b4423" stroke-width="2" '
            f'transform="rotate(-35 {hx - 18} {hy + 6})"/><circle cx="{hx - 18}" cy="{hy + 6}" r="6" fill="#3b2a18"/>')


def _face(c, cx, cy, r, uid, skin, beard=False, hair="#e8e8e8"):
    pers = c.get("personality", "Brave")
    villain = c.get("role") in ("Villain", "Boss")
    eye = "#d61f1f" if villain else "#1d1d24"
    feature = c.get("appearance", "").lower()
    eye2 = "#2a7fd4" if "mismatched" in feature else eye
    s = []
    if villain:
        s.append(f'<circle cx="{cx - 13}" cy="{cy}" r="7" fill="#ff3030" opacity=".35"/>'
                 f'<circle cx="{cx + 13}" cy="{cy}" r="7" fill="#ff3030" opacity=".35"/>')
    s.append(f'<ellipse cx="{cx - 13}" cy="{cy}" rx="4" ry="5" fill="{eye}"/>'
             f'<ellipse cx="{cx + 13}" cy="{cy}" rx="4" ry="5" fill="{eye2}"/>'
             f'<circle cx="{cx - 12}" cy="{cy - 2}" r="1.3" fill="#fff"/><circle cx="{cx + 14}" cy="{cy - 2}" r="1.3" fill="#fff"/>')
    brow = {"Ruthless": (4, -4), "Cunning": (2, -2), "Brave": (0, 0), "Wise": (-1, 1),
            "Gentle": (-3, 3), "Sarcastic": (-3, 2)}.get(pers, (0, 0))
    s.append(f'<line x1="{cx - 20}" y1="{cy - 11 - brow[0]}" x2="{cx - 6}" y2="{cy - 11 + brow[0]}" stroke="#2b1d14" stroke-width="2.4" stroke-linecap="round"/>'
             f'<line x1="{cx + 6}" y1="{cy - 11 + brow[1]}" x2="{cx + 20}" y2="{cy - 11 - brow[1]}" stroke="#2b1d14" stroke-width="2.4" stroke-linecap="round"/>')
    mouth = {
        "Gentle": f"M{cx - 9} {cy + 15} Q{cx} {cy + 23} {cx + 9} {cy + 15}",
        "Brave": f"M{cx - 9} {cy + 16} Q{cx} {cy + 21} {cx + 9} {cy + 16}",
        "Sarcastic": f"M{cx - 9} {cy + 18} Q{cx + 2} {cy + 18} {cx + 10} {cy + 13}",
        "Cunning": f"M{cx - 8} {cy + 17} Q{cx + 3} {cy + 20} {cx + 10} {cy + 14}",
        "Wise": f"M{cx - 8} {cy + 17} L{cx + 8} {cy + 17}",
        "Ruthless": f"M{cx - 9} {cy + 19} Q{cx} {cy + 14} {cx + 9} {cy + 19}",
    }.get(pers, f"M{cx - 8} {cy + 17} L{cx + 8} {cy + 17}")
    s.append(f'<path d="{mouth}" fill="none" stroke="#5a2a20" stroke-width="2.2" stroke-linecap="round"/>')
    if "scar" in feature:
        s.append(f'<line x1="{cx + 10}" y1="{cy - 20}" x2="{cx + 18}" y2="{cy - 3}" stroke="#a33" stroke-width="2"/>')
    if beard:
        s.append(f'<path d="M{cx - 18} {cy + 14} Q{cx} {cy + 52} {cx + 18} {cy + 14} Q{cx} {cy + 30} {cx - 18} {cy + 14}Z" fill="{hair}"/>')
    return s


def portrait_svg(c, variant=0, size=360):
    """Return an SVG string for character `c`. `variant` changes stylistic details."""
    uid = f"p{abs(hash((c.get('id'), c.get('name'), variant))) % 10**8}"
    r = random.Random(f"{c.get('id')}-{c.get('name')}-{variant}")
    pal = ([_hex(p) for p in c.get("palette", ["silver", "steel grey", "gold"])] + ["#888888"] * 3)[:3]
    k = variant % 3  # each variation rotates which bible colour goes on tunic / cloak / trim
    main, cloak, accent = pal[k], pal[(k + 1) % 3], pal[(k + 2) % 3]
    elements = [a.get("element", "aether") for a in c.get("abilities", []) if a.get("element") != "aether"]
    elem = ELEMENT_COLOR.get(elements[0] if elements else "aether", "#c9a2ff")
    skin, hair = r.choice(SKIN), r.choice(HAIR)
    if c.get("age", 30) > 55:
        hair = r.choice(["#d8d8d8", "#9a9a9a", "#bfb6a8"])
    headgear = r.choice(["none", "none", "circlet", "helm" if c.get("char_class") == "Warrior" else "band"])
    beard = c.get("personality") == "Wise" or (c.get("age", 30) > 45 and r.random() < 0.5)
    app = c.get("appearance", "").lower()
    sw = 58 if "broad" in app else 40 if "wiry" in app else 46
    scale = 0.9 if "small" in app else 1.0
    stretch = 1.05 if "tall" in app else 1.0
    cx, hy = 180, 150
    cls, faction, role = c.get("char_class", "Warrior"), c.get("faction", ""), c.get("role", "")

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 460" width="{size}" height="{size * 460 // 360}">']
    s += _background(faction, uid, r)
    s.append(f'<circle cx="{cx}" cy="230" r="150" fill="{elem}" opacity=".16"/>')
    s.append(f'<circle cx="{cx}" cy="230" r="105" fill="{elem}" opacity=".14"/>')
    for _ in range(10):
        a, d = r.uniform(0, 6.28), r.randint(95, 150)
        s.append(f'<circle cx="{cx + d * math.cos(a):.0f}" cy="{230 + d * math.sin(a):.0f}" r="{r.choice([2, 3])}" fill="{elem}" opacity=".8"/>')
    s.append(f'<ellipse cx="{cx}" cy="402" rx="85" ry="12" fill="#000" opacity=".35"/>')

    s.append(f'<g transform="translate({cx} 400) scale({scale} {scale * stretch}) translate({-cx} -400)">')
    hood = cls == "Rogue" or r.random() < 0.15
    # cloak
    s.append(f'<path d="M{cx - sw - 4} 195 Q{cx - sw - 30} 300 {cx - sw - 22} 385 L{cx + sw + 22} 385 '
             f'Q{cx + sw + 30} 300 {cx + sw + 4} 195Z" fill="{cloak}" stroke="#00000040" stroke-width="2"/>')
    if hood:
        s.append(f'<circle cx="{cx}" cy="{hy - 2}" r="47" fill="{cloak}" stroke="#00000040" stroke-width="2"/>')
    # legs + boots
    s.append(f'<rect x="{cx - 26}" y="320" width="20" height="70" rx="6" fill="#2d2a33"/>'
             f'<rect x="{cx + 6}" y="320" width="20" height="70" rx="6" fill="#2d2a33"/>'
             f'<rect x="{cx - 30}" y="378" width="26" height="16" rx="6" fill="#3b2a18"/>'
             f'<rect x="{cx + 4}" y="378" width="26" height="16" rx="6" fill="#3b2a18"/>')
    # arms
    s.append(f'<path d="M{cx - sw} 198 L{cx - sw - 16} 300 L{cx - sw + 2} 302 L{cx - sw + 16} 215Z" fill="{main}" stroke="#00000033"/>'
             f'<path d="M{cx + sw} 198 L{cx + sw + 16} 300 L{cx + sw - 2} 302 L{cx + sw - 16} 215Z" fill="{main}" stroke="#00000033"/>')
    # torso + tunic
    s.append(f'<path d="M{cx - sw} 195 Q{cx} 180 {cx + sw} 195 L{cx + 36} 290 L{cx + sw + 6} 335 L{cx - sw - 6} 335 L{cx - 36} 290Z" '
             f'fill="{main}" stroke="#00000040" stroke-width="2"/>')
    s.append(f'<rect x="{cx - 38}" y="284" width="76" height="11" rx="3" fill="{accent}"/>'
             f'<rect x="{cx - 7}" y="283" width="14" height="13" rx="2" fill="#e7d27a" stroke="#6b5a1e"/>')
    if sw >= 56 or role == "Boss":
        s.append(f'<path d="M{cx - sw - 10} 205 Q{cx - sw} 180 {cx - sw + 22} 192Z" fill="{accent}"/>'
                 f'<path d="M{cx + sw + 10} 205 Q{cx + sw} 180 {cx + sw - 22} 192Z" fill="{accent}"/>')
    s.append(_emblem(faction, cx, 235, 13, accent))
    if role == "Merchant NPC":
        s.append(f'<ellipse cx="{cx + 26}" cy="305" rx="11" ry="13" fill="#a8672f"/><circle cx="{cx + 26}" cy="300" r="3" fill="#ffd34d"/>')
    # neck + head
    s.append(f'<rect x="{cx - 10}" y="{hy + 25}" width="20" height="20" fill="{skin}"/>')
    s.append(f'<circle cx="{cx}" cy="{hy}" r="34" fill="{skin}" stroke="#00000030" stroke-width="1.5"/>')
    s.append(f'<circle cx="{cx - sw - 8}" cy="303" r="9" fill="{skin}"/><circle cx="{cx + sw + 8}" cy="303" r="9" fill="{skin}"/>')
    # hair
    if hood:
        s.append(f'<path d="M{cx - 47} {hy} Q{cx - 45} {hy - 50} {cx} {hy - 52} Q{cx + 45} {hy - 50} {cx + 47} {hy} '
                 f'Q{cx + 36} {hy - 30} {cx} {hy - 34} Q{cx - 36} {hy - 30} {cx - 47} {hy}Z" fill="{cloak}" stroke="#00000040"/>')
    else:
        style = r.choice(["short", "long", "bun", "braid", "spiky"])
        if "braid" in app:
            style = "braid"
        top = (f'<path d="M{cx - 35} {hy - 2} Q{cx - 36} {hy - 42} {cx} {hy - 40} Q{cx + 36} {hy - 42} {cx + 35} {hy - 2} '
               f'Q{cx + 22} {hy - 26} {cx} {hy - 24} Q{cx - 22} {hy - 26} {cx - 35} {hy - 2}Z" fill="{hair}"/>')
        if style == "long":
            s.append(f'<path d="M{cx - 36} {hy - 5} L{cx - 40} {hy + 60} L{cx - 22} {hy + 50} L{cx - 26} {hy}Z" fill="{hair}"/>'
                     f'<path d="M{cx + 36} {hy - 5} L{cx + 40} {hy + 60} L{cx + 22} {hy + 50} L{cx + 26} {hy}Z" fill="{hair}"/>')
        s.append(top)
        if style == "bun":
            s.append(f'<circle cx="{cx}" cy="{hy - 44}" r="12" fill="{hair}"/>')
        elif style == "braid":
            for i in range(6):
                s.append(f'<circle cx="{cx + 32}" cy="{hy + 4 + i * 12}" r="6" fill="{hair}"/>')
            s.append(f'<circle cx="{cx + 32}" cy="{hy + 30}" r="3" fill="{accent}"/><circle cx="{cx + 32}" cy="{hy + 54}" r="3" fill="{accent}"/>')
        elif style == "spiky":
            s.append("".join(f'<polygon points="{cx + dx - 9},{hy - 30} {cx + dx},{hy - 56} {cx + dx + 9},{hy - 30}" fill="{hair}"/>'
                             for dx in (-20, 0, 20)))
    if role != "Boss" and not hood:
        if headgear == "helm":
            s.append(f'<path d="M{cx - 37} {hy - 4} Q{cx - 38} {hy - 46} {cx} {hy - 46} Q{cx + 38} {hy - 46} {cx + 37} {hy - 4} '
                     f'L{cx + 30} {hy - 10} L{cx - 30} {hy - 10}Z" fill="#b8c0c8" stroke="#555" stroke-width="1.5"/>'
                     f'<rect x="{cx - 3}" y="{hy - 46}" width="6" height="34" fill="{accent}"/>')
        elif headgear == "circlet":
            s.append(f'<path d="M{cx - 33} {hy - 16} Q{cx} {hy - 30} {cx + 33} {hy - 16}" fill="none" stroke="#e7d27a" stroke-width="3"/>'
                     f'<circle cx="{cx}" cy="{hy - 23}" r="4.5" fill="{elem}" stroke="#fff"/>')
        elif headgear == "band":
            s.append(f'<path d="M{cx - 34} {hy - 14} Q{cx} {hy - 26} {cx + 34} {hy - 14}" fill="none" stroke="{accent}" stroke-width="6"/>')
    if role == "Boss":
        s.append(f'<polygon points="{cx - 22},{hy - 34} {cx - 16},{hy - 58} {cx - 8},{hy - 38} {cx},{hy - 62} '
                 f'{cx + 8},{hy - 38} {cx + 16},{hy - 58} {cx + 22},{hy - 34}" fill="#d4a72c" stroke="#6b5a1e"/>')
    s += _face(c, cx, hy, 34, uid, skin, beard, hair)
    s.append(_weapon(cls, cx + sw + 8, 303, cx - sw - 8, 290, elem, uid, faction, accent))
    s.append("</g>")
    if role in ("Villain", "Boss"):
        s.append(f'<rect width="360" height="460" fill="#000" opacity=".18"/>')
    if role == "Protagonist":
        s.append(f'<rect x="3" y="3" width="354" height="454" fill="none" stroke="#d4a72c" stroke-width="3" rx="8"/>')
    # name banner
    s.append('<rect x="0" y="412" width="360" height="48" fill="#000" opacity=".55"/>')
    s.append(f'<text x="180" y="434" text-anchor="middle" font-family="Georgia, serif" font-size="20" '
             f'font-weight="bold" fill="#fff">{_esc(c.get("name", ""))}</text>')
    s.append(f'<text x="180" y="452" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="11" '
             f'fill="#ddd">{_esc(faction)} · {_esc(cls)} · {_esc(role)}</text>')
    s.append("</svg>")
    return "".join(s)


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()
