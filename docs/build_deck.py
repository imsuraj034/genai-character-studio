"""Builds the presentation deck (PPTX) with real app screenshots and live evaluation numbers.

Run (after docs/capture_screens.py):  python docs/build_deck.py
"""
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

DOCS = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS.parent))
sys.path.insert(0, str(DOCS))
from evaluate import evaluate  # noqa: E402

SHOTS = DOCS / "screenshots" / "crops"
OUT = DOCS / "Case_Study_65_Presentation.pptx"
STUDENT, USN = "Suraj T", "1DS23AI058"

# palette (matches the app)
BG, PANEL, PANEL2, LINE = "0B0F19", "141B2B", "1B2438", "2A3550"
TEXT, MUTED, ACCENT = "E9ECF4", "9AA3B8", "7C83FD"
TEAL, AMBER, CORAL, VIOLET = "3DD6C3", "F6B64B", "F47174", "B48CF2"
HEAD, BODY = "Calibri", "Calibri"


def rgb(h):
    return RGBColor.from_string(h)


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


# ------------------------------------------------------------------ primitives
def new_slide(notes=""):
    s = prs.slides.add_slide(BLANK)
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(BG)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def text(s, x, y, w, h, runs, size=16, color=TEXT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         font=BODY, spacing=None, italic=False, line=1.1, para_after=0):
    """runs: str, or list of paragraphs; each paragraph a str or list of (text, {opts})."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        p.space_after = Pt(para_after)
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            if o.get("spacing", spacing):
                r._r.get_or_add_rPr().set("spc", str(int(o.get("spacing", spacing) * 100)))
    return tb


def box(s, x, y, w, h, fill=PANEL, line=LINE, radius=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_w=1.0,
        dash=False):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(line_w)
        if dash:
            sh.line.dash_style = 4  # dash
    else:
        sh.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh


def header(s, eyebrow, title):
    text(s, 0.6, 0.42, 12, 0.3, eyebrow.upper(), size=12, color=ACCENT, bold=True, spacing=2.2)
    text(s, 0.6, 0.72, 12.1, 0.8, title, size=32, bold=True, font=HEAD)


def picture(s, path, x, y, w=None, h=None, border=LINE):
    pic = s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    av = pic._element.spPr.find(qn("a:prstGeom")).find(qn("a:avLst"))
    etree.SubElement(av, qn("a:gd"), name="adj", fmla="val 2500")
    pic.line.color.rgb = rgb(border)
    pic.line.width = Pt(1.25)
    return pic


def badge(s, x, y, n, color=ACCENT, d=0.42, size=14):
    c = box(s, x, y, d, d, fill=color, line=None, shape=MSO_SHAPE.OVAL)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(n)
    r.font.size, r.font.bold, r.font.name = Pt(size), True, BODY
    r.font.color.rgb = rgb(BG)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return c


def point(s, x, y, w, n, title, body, color=ACCENT, title_size=17, body_size=14, gap=0.36):
    badge(s, x, y, n, color)
    text(s, x + 0.6, y - 0.02, w - 0.6, 0.35, title, size=title_size, bold=True)
    text(s, x + 0.6, y + gap, w - 0.6, 0.9, body, size=body_size, color=MUTED, line=1.15)


def stat(s, x, y, w, h, value, label, color=ACCENT, vsize=40):
    box(s, x, y, w, h, fill=PANEL)
    text(s, x + 0.25, y + 0.18, w - 0.5, h * 0.55, value, size=vsize, bold=True, color=color, font=HEAD,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25, y + h * 0.62, w - 0.5, h * 0.33, label, size=13, color=MUTED, line=1.1)


def arrow(s, x1, y1, x2, y2, color=MUTED, dash=False, width=1.5):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        etree.SubElement(ln, qn("a:prstDash")).set("val", "dash")
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return c


def footer(s, n):
    text(s, 0.6, 7.03, 8, 0.25, f"Case Study 65 · GenAI for Video Game Character Design", size=10, color=MUTED)
    text(s, 11.73, 7.03, 1.0, 0.25, str(n), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


# ------------------------------------------------------------------ data
rows, guard = evaluate()
hi = rows[-1]
saving = hi["large_model_cost_per_char_usd"] / hi["cost_per_char_usd"]

# ================================================================== 1. title
s = new_slide("Introduce yourself and the case study. One sentence: this is a working GenAI tool that designs "
              "game characters, and keeps the AI inside the game's rules, safe, original, cheap and under the "
              "designer's control.")
text(s, 0.75, 0.9, 6.4, 0.35, "CASE STUDY 65", size=13, color=ACCENT, bold=True, spacing=3)
text(s, 0.75, 1.35, 6.6, 1.9, "Character Design Studio", size=50, bold=True, font=HEAD, line=0.95)
text(s, 0.75, 3.3, 6.0, 1.2, "A GenAI workflow that designs video-game characters while keeping them consistent, "
                             "safe, original, affordable and under human control", size=18, color=MUTED, line=1.2)
box(s, 0.75, 5.05, 4.5, 1.25, fill=PANEL)
text(s, 1.05, 5.25, 4.0, 0.4, STUDENT, size=20, bold=True)
text(s, 1.05, 5.68, 4.0, 0.4, f"USN {USN}", size=15, color=MUTED)
for i in range(4):
    picture(s, SHOTS / f"portrait_{i}.png", 7.45 + (i % 2) * 2.62, 0.55 + (i // 2) * 3.27, w=2.45, border=LINE)

# ================================================================== 2. problem
s = new_slide("Studios want speed from GenAI, but raw output creates five problems. These five map exactly to the "
              "constraints in the case study, and the rest of the talk shows how each one is solved.")
header(s, "The problem", "Raw GenAI output isn't ready for a game")
problems = [
    ("Breaks the rules", "Fire magic for an ice faction, guns in a medieval world, living dragons that should be extinct", CORAL),
    ("Copies others' IP", "Look-alike names (Kratoz, Pikachoo), franchise terms, 'in the style of' a real studio", VIOLET),
    ("Unsafe content", "Gore or adult themes in a PEGI 12 game; prompt injection hidden in a brief", AMBER),
    ("Costs add up", "Every call costs tokens; hundreds of NPCs on the largest model gets expensive fast", TEAL),
    ("Designers lose control", "Unreviewed AI content shipping with no record of who decided what", ACCENT),
]
cw, gap = 2.3, 0.15
for i, (t, b, col) in enumerate(problems):
    x = 0.6 + i * (cw + gap)
    box(s, x, 1.85, cw, 3.75, fill=PANEL)
    badge(s, x + 0.3, 2.15, i + 1, col, d=0.5, size=16)
    text(s, x + 0.3, 2.95, cw - 0.55, 0.85, t, size=19, bold=True, line=1.0)
    text(s, x + 0.3, 3.9, cw - 0.55, 1.6, b, size=14, color=MUTED, line=1.2)
text(s, 0.6, 5.95, 12.1, 0.5, [[("Goal: ", {"bold": True, "color": ACCENT}), ("keep the speed of GenAI and remove all five "
     "risks, which are exactly the constraints set in the case study.", {})]], size=17, color=TEXT)
footer(s, 2)

# ================================================================== 3. solution pipeline
s = new_slide("The core idea: don't trust the model, wrap it. Walk left to right. Red stages are guardrails, green "
              "stages control cost and keep a human in charge. The Game Bible feeds both the generator and the "
              "checker, and errors loop back through auto-repair.")
header(s, "The solution", "Wrap the model in a guarded pipeline")
stages = [("Designer brief", ACCENT), ("Input guardrail", CORAL), ("Cache, budget, routing", TEAL),
          ("Generator", ACCENT), ("Output guardrail", CORAL), ("Consistency check", ACCENT),
          ("Human review", TEAL), ("Export + provenance", ACCENT)]
bw, bg_, y = 1.33, 0.18, 2.5
for i, (t, col) in enumerate(stages):
    x = 0.6 + i * (bw + bg_)
    box(s, x, y, bw, 1.2, fill=PANEL, line=col, line_w=1.75)
    text(s, x + 0.1, y + 0.1, bw - 0.2, 1.0, t, size=14, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if i < len(stages) - 1:
        arrow(s, x + bw + 0.02, y + 0.6, x + bw + bg_ - 0.02, y + 0.6)
gx = 0.6 + 3 * (bw + bg_)
cx = 0.6 + 5 * (bw + bg_)
ox = 0.6 + 4 * (bw + bg_)
box(s, gx, 4.75, cx + bw - gx, 0.85, fill=PANEL, line=AMBER, line_w=1.75)
text(s, gx + 0.2, 4.75, cx + bw - gx - 0.4, 0.85, [[("Game Bible  ", {"bold": True, "color": AMBER}),
                                                     ("rules, lore, factions, banned content", {"color": MUTED})]],
     size=15, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
arrow(s, gx + bw / 2, 4.75, gx + bw / 2, y + 1.22, color=AMBER, dash=True)
arrow(s, cx + bw / 2, 4.75, cx + bw / 2, y + 1.22, color=AMBER, dash=True)
box(s, ox, 1.7, cx + bw - ox, 0.6, fill=None, line=CORAL, dash=True)
text(s, ox + 0.1, 1.7, cx + bw - ox - 0.2, 0.6, "Auto-repair loop: errors regenerate only the broken fields", size=12,
     color=CORAL, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
legend = [(CORAL, "Guardrails"), (TEAL, "Cost and human control"), (AMBER, "Grounding")]
for i, (col, t) in enumerate(legend):
    box(s, 0.6 + i * 3.1, 6.15, 0.22, 0.22, fill=col, line=None, radius=0.3)
    text(s, 0.95 + i * 3.1, 6.1, 2.6, 0.3, t, size=13, color=MUTED)
footer(s, 3)

# ================================================================== 6. generation
s = new_slide("One click runs the whole pipeline. The step tracker shows every stage; here the consistency check "
              "failed on the first draft and auto-repair fixed it. The result is a full character package with "
              "generated concept art.")
header(s, "Generation", "One brief in, a full character package out")
picture(s, SHOTS / "03_generate_result.png", 0.6, 1.7, h=5.05)
pts = [("Step-by-step trace", "Every pipeline stage is shown: passed or flagged"),
       ("Full character", "Look, palette, abilities, item, backstory, motivation, flaw, catchphrase"),
       ("Concept art", "A portrait drawn from the validated data, plus a prompt for any image model"),
       ("Grounded in the Game Bible", "4 factions, lore, tech level; 7 rules score every output")]
for i, (t, b) in enumerate(pts):
    point(s, 7.75, 1.85 + i * 1.22, 4.98, i + 1, t, b, body_size=14, gap=0.36)
footer(s, 4)

# ================================================================== 7. self-correction
s = new_slide("The most important slide. At high creativity the AI made five mistakes in one character: a laser in a "
              "medieval world, a tamed dragon, a name copied from Geralt, and Studio Ghibli's style. The checker caught "
              "every one and auto-repair regenerated only the broken fields: 53 to 100. Across the evaluation runs, "
              "no repaired character still had an error.")
header(s, "Self-correction", "The AI makes mistakes. The pipeline catches and fixes them")
picture(s, SHOTS / "04_self_correction.png", 0.6, 1.7, w=7.25)
stat(s, 8.3, 1.7, 2.1, 1.55, "53", "score of the raw AI draft", CORAL, 44)
text(s, 10.4, 1.7, 0.5, 1.55, "→", size=34, color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
stat(s, 10.9, 1.7, 1.85, 1.55, "100", "after auto-repair", TEAL, 44)
stat(s, 8.3, 3.5, 4.45, 1.45, f"{hi['drafts_with_violations_pct']}% → {hi['final_with_errors_pct']}%",
     f"of characters with rule errors at max creativity, before vs. after repair ({hi['runs']} runs)", ACCENT, 36)
text(s, 8.3, 5.2, 4.45, 1.4, "Only broken fields are regenerated, so the parts the designer liked are kept and "
                             "repair costs a fraction of a full regeneration.", size=14, color=MUTED, line=1.2)
footer(s, 5)

# ================================================================== 8. guardrails
s = new_slide("Guardrails run on the way in and on the way out. An unsafe brief is blocked before it ever reaches the "
              "model. Copyright issues are flagged, not blocked, because a human should judge borderline cases: for "
              "example 'Maro' is 89% similar to 'Mario'.")
header(s, "Responsible AI", "Guardrails for safety and copyright")
picture(s, SHOTS / "08_guardrail_block.png", 5.45, 1.7, w=7.28)
tiles = [(guard["unsafe_blocked"], "unsafe or injection briefs blocked", TEAL),
         (guard["safe_false_blocks"], "safe briefs wrongly blocked", TEAL),
         (guard["copycat_names_flagged"], "copycat names flagged", VIOLET),
         (guard["original_names_false_flags"], "original names wrongly flagged", VIOLET)]
for i, (v, l, c) in enumerate(tiles):
    stat(s, 0.6 + (i % 2) * 2.33, 1.7 + (i // 2) * 1.75, 2.18, 1.6, v, l, c, 32)
text(s, 0.6, 5.35, 4.5, 1.5, [[("Content filter ", {"bold": True, "color": TEXT}),
                               ("violence, adult, self-harm, drugs, hate, profanity", {})],
                              [("Injection filter ", {"bold": True, "color": TEXT}), ("“ignore previous instructions…”", {})],
                              [("IP detector ", {"bold": True, "color": TEXT}), ("names, franchises, traits, artist styles", {})]],
     size=14, color=MUTED, line=1.15, para_after=6)
footer(s, 6)

# ================================================================== 9. dialogue & story
s = new_slide("The same character gets dialogue in its own voice for different game situations, and several "
              "branching story arcs. Every arc is checked against lore and safety rules too.")
header(s, "Narrative", "Dialogue and branching story variations")
picture(s, SHOTS / "05_dialogue_story.png", 0.6, 1.7, h=5.05)
pts = [("6 situations", "Greeting, boss fight, trading, betrayal, victory, defeat"),
       ("Personality voice", "Brave, sarcastic, wise, cunning, gentle or ruthless"),
       ("5 story arcs", "Redemption, betrayal, sacrifice, rise to power, hidden heir; each lore-checked")]
for i, (t, b) in enumerate(pts):
    point(s, 7.75, 1.95 + i * 1.55, 4.98, i + 1, t, b)
footer(s, 7)

# ================================================================== 10. human control
s = new_slide("AI never has the final say. The designer approves, rejects, edits or regenerates; picks one of three "
              "concept-art variations or uploads their own; and every action is versioned with author, score and a "
              "diff. Only approved characters can be exported.")
header(s, "Human in the loop", "The designer always has the final say")
picture(s, SHOTS / "06_review.png", 0.6, 1.7, w=5.95, h=4.58)
picture(s, SHOTS / "07_concept_art.png", 6.78, 1.7, w=5.95, h=4.58)
caps = [("Approve · reject · edit · regenerate", "Edits are re-checked automatically"),
        ("Pick concept art or upload your own", "Every choice is logged")]
for i, (t, b) in enumerate(caps):
    text(s, 0.6 + i * 6.18, 6.4, 5.95, 0.6, [[(t, {"bold": True, "color": TEXT}), ("   " + b, {"color": MUTED})]],
         size=14)
footer(s, 8)

# ================================================================== 11. cost
s = new_slide(f"Cost is one of the four required constraints. Every call is metered. Cheap models handle repair and "
              f"dialogue, the medium model handles creative work, repeats are cached for free, and a budget cap stops "
              f"overspending. The result is about {saving:.0f} times cheaper per character than using the biggest "
              f"model for everything.")
header(s, "Computational cost", f"About {saving:.0f}× cheaper than using the biggest model for everything")
cd = CategoryChartData()
cd.categories = [f"Creativity {r['temperature']}" for r in rows]
cd.add_series("Largest model only", [r["large_model_cost_per_char_usd"] for r in rows])
cd.add_series("Our routed pipeline", [r["cost_per_char_usd"] for r in rows])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.75), Inches(7.4), Inches(4.95), cd)
ch = gf.chart
ch.has_title = True
ch.chart_title.text_frame.text = "Estimated cost per character (USD)"
tp = ch.chart_title.text_frame.paragraphs[0]
tp.runs[0].font.size, tp.runs[0].font.bold, tp.runs[0].font.name = Pt(14), True, BODY
tp.runs[0].font.color.rgb = rgb(TEXT)
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
ch.legend.font.size, ch.legend.font.name = Pt(12), BODY
ch.legend.font.color.rgb = rgb(MUTED)
for ser, col in zip(ch.series, [CORAL, TEAL]):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
plot = ch.plots[0]
plot.gap_width, plot.overlap = 70, -10
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format, dl.number_format_is_linked = '"$"0.000', False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size, dl.font.name = Pt(11), BODY
dl.font.color.rgb = rgb(TEXT)
for ax in (ch.category_axis, ch.value_axis):
    ax.tick_labels.font.size, ax.tick_labels.font.name = Pt(11), BODY
    ax.tick_labels.font.color.rgb = rgb(MUTED)
    ax.format.line.color.rgb = rgb(LINE)
ch.value_axis.major_gridlines.format.line.color.rgb = rgb(LINE)
ch.value_axis.tick_labels.number_format, ch.value_axis.tick_labels.number_format_is_linked = '"$"0.00', False
ch.value_axis.has_title = False
strategies = [("Model routing", "cheap model for repair and dialogue"),
              ("Response caching", "identical requests cost $0"),
              ("Targeted repair", "regenerate broken fields only"),
              ("Budget cap", "generation stops at the session limit"),
              ("Offline / local engine", "$0 for prototyping")]
box(s, 8.4, 1.75, 4.35, 4.95, fill=PANEL)
for i, (t, b) in enumerate(strategies):
    badge(s, 8.7, 2.05 + i * 0.9, i + 1, TEAL, d=0.36, size=12)
    text(s, 9.22, 2.02 + i * 0.9, 3.35, 0.3, t, size=15, bold=True)
    text(s, 9.22, 2.33 + i * 0.9, 3.35, 0.5, b, size=12, color=MUTED)
text(s, 0.6, 6.72, 7.4, 0.25, "Prices are illustrative tiers (editable in the app); token counts use ~4 characters per token.",
     size=10, color=MUTED, italic=True)
footer(s, 9)

# ================================================================== 15. conclusion
s = new_slide("Wrap up with the four constraints, then switch to the live demo using docs/DEMO_SCRIPT.md.")
text(s, 0.75, 0.9, 7, 0.35, "CONCLUSION", size=13, color=ACCENT, bold=True, spacing=3)
text(s, 0.75, 1.35, 7.2, 1.7, "GenAI speeds up character design when it is wrapped in the right engineering",
     size=34, bold=True, font=HEAD, line=1.0)
con = [("Consistent", "grounded in the Game Bible, checked and auto-repaired", AMBER),
       ("Safe & original", "content filters, injection blocking, IP detection", CORAL),
       ("Affordable", f"routing and caching, about {saving:.0f}× cheaper", TEAL),
       ("Human-led", "nothing ships without designer approval", ACCENT)]
for i, (t, b, c) in enumerate(con):
    y = 3.55 + i * 0.78
    badge(s, 0.75, y, i + 1, c)
    text(s, 1.35, y - 0.02, 6.6, 0.48, [[(t, {"bold": True, "color": TEXT}), ("   " + b, {"color": MUTED})]],
         size=17, anchor=MSO_ANCHOR.MIDDLE)
box(s, 8.45, 0.9, 4.28, 2.95, fill=PANEL)
text(s, 8.75, 1.15, 3.8, 0.3, "NEXT STEPS", size=12, bold=True, color=ACCENT, spacing=2)
nxt = ["Trained moderation model + embedding similarity",
       "Licensed IP database for copyright checks",
       "Local image model for concept art",
       "Multi-role review: writer, art director, legal"]
text(s, 8.75, 1.6, 3.75, 2.7, [[("›  ", {"color": ACCENT, "bold": True}), (n, {})] for n in nxt],
     size=14, color=TEXT, line=1.15, para_after=8)
stat(s, 8.45, 4.05, 2.04, 1.55, "9/9", "automated tests pass", TEAL, 30)
stat(s, 10.69, 4.05, 2.04, 1.55, "$0", "offline, no API key", TEAL, 30)
text(s, 8.45, 5.95, 4.28, 0.5, [[("Thank you", {"bold": True, "size": 24, "color": TEXT}),
                                 (f"   {STUDENT} · {USN}", {"size": 13, "color": MUTED})]], size=13)

prs.save(OUT)
print(OUT)
