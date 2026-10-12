"""Export approved characters as JSON (for the game engine) or a PDF character sheet."""
import io
import json

from fpdf import FPDF

from .art import art_bytes

_REPL = {"—": "-", "–": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
         "…": "...", "→": "->", "█": "#"}


def _t(s):
    s = str(s)
    for a, b in _REPL.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


def to_json(item):
    latest = item["versions"][-1]
    return json.dumps({
        "character": latest["character"],
        "dialogue": item["extras"].get("dialogue", {}),
        "story_arcs": item["extras"].get("arcs", []),
        "concept_art": {k: v for k, v in item["extras"].get("art", {"type": "ai", "variant": 0}).items() if k != "data"},
        "provenance": [{k: v.get(k) for k in ("v", "time", "author", "action", "score", "note")}
                       for v in item["versions"]],
    }, indent=2, ensure_ascii=False)


def to_pdf(item, bible):
    c = item["versions"][-1]["character"]
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()
    pdf.set_fill_color(32, 44, 74)
    pdf.rect(0, 0, 210, 34, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(12, 8)
    pdf.cell(0, 10, _t(c["name"]))
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(12, 20)
    pdf.cell(0, 6, _t(f"{c['role']} | {c['faction']} {c['char_class']} | {c['personality']} | "
                      f"{bible['world_name']}"))
    pdf.set_text_color(20, 20, 20)
    pdf.set_y(42)

    # concept art on the right, text flows beside it
    art_w = 62
    try:
        data, _ = art_bytes(item)
        pdf.image(io.BytesIO(data), x=210 - 12 - art_w, y=42, w=art_w)
        pdf.set_right_margin(12 + art_w + 6)
    except Exception:
        art_w = 0

    def section(title, body):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(32, 44, 74)
        pdf.cell(0, 7, _t(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 5.5, _t(body), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    section("Appearance", f"{c['appearance']} Age {c['age']}. Palette: {', '.join(c['palette'])}.")
    section("Abilities", "\n".join(f"- {a['name']} ({a['element']}): {a['description']}" for a in c["abilities"]))
    section("Signature item", c["signature_item"])
    section("Backstory", c["backstory"])
    section("Motivation & flaw", f"{c['motivation']} {c['flaw']}")
    section("Catchphrase", f"\"{c['catchphrase']}\"")
    if pdf.get_y() < 42 + art_w * 460 / 360 + 4:
        pdf.set_y(42 + art_w * 460 / 360 + 4)
    pdf.set_right_margin(10)
    dlg = item["extras"].get("dialogue", {})
    if dlg:
        section("Dialogue", "\n".join(f"[{sit}] {line}" for sit, lines in dlg.items() for line in lines))
    for a in item["extras"].get("arcs", []):
        section(f"Story arc - {a.get('title', a.get('type'))}",
                a.get("logline", "") + "\n" + "\n".join(f"{i + 1}. {b}" for i, b in enumerate(a.get("beats", [])))
                + f"\nEnding: {a.get('ending', '')}")
    section("Concept-art prompt", c["visual_prompt"])
    v = item["versions"]
    section("Provenance", "\n".join(f"v{x['v']} {x['time']} - {x['author']}: {x['action']}"
                                    + (f" (score {x['score']})" if x.get("score") is not None else "")
                                    for x in v))
    return bytes(pdf.output())
