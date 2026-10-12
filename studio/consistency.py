"""Consistency checker: validates generated content against the Game Bible.

Each rule returns issues of the form
    {"rule": id, "severity": "error"|"warning", "field": field, "message": text}
Errors block approval; warnings are shown to the designer.
"""
import re

from .vocab import ELEMENT_KEYWORDS

PENALTY = {"error": 20, "warning": 7}

RULES = {
    "R1": "Abilities use only the faction's elements",
    "R2": "No technology beyond the world's tech level",
    "R3": "No contradictions with established lore",
    "R4": "Colour palette matches the faction",
    "R5": "Name follows faction naming conventions",
    "R6": "Dialogue lines respect the length limit",
    "R7": "Character is placed in a valid faction, class and role",
}


def _words(text):
    return set(re.findall(r"[a-z][a-z-]*", text.lower()))


def detect_elements(text):
    words = _words(text)
    return {el for el, kws in ELEMENT_KEYWORDS.items() if any(k in words for k in kws)}


def _text_fields(char):
    yield "backstory", char.get("backstory", "")
    yield "signature_item", char.get("signature_item", "")
    yield "appearance", char.get("appearance", "")
    yield "motivation", char.get("motivation", "")
    yield "visual_prompt", char.get("visual_prompt", "")
    for a in char.get("abilities", []):
        yield "abilities", f"{a.get('name', '')} {a.get('description', '')}"


def check_character(char, bible):
    issues = []
    faction = bible["factions"].get(char.get("faction"))

    # R7 structure
    if not faction:
        return [{"rule": "R7", "severity": "error", "field": "faction",
                 "message": f"Unknown faction '{char.get('faction')}'."}]
    if char.get("char_class") not in bible["classes"]:
        issues.append({"rule": "R7", "severity": "error", "field": "char_class",
                       "message": f"Class '{char.get('char_class')}' is not in the bible."})

    # R1 elements
    allowed = set(faction["elements"]) | {"aether"}
    for a in char.get("abilities", []):
        found = detect_elements(f"{a.get('name', '')} {a.get('description', '')}")
        declared = {str(a.get("element", "")).lower()} - {""}
        bad = (found | declared) - allowed
        if bad:
            issues.append({"rule": "R1", "severity": "error", "field": "abilities",
                           "message": f"Ability '{a.get('name')}' uses {', '.join(sorted(bad))} magic, "
                                      f"but the {char['faction']} can only channel {', '.join(faction['elements'])}."})

    # R2 tech level
    forbidden = set(bible["forbidden_tech"])
    seen = set()
    for field, text in _text_fields(char):
        for w in sorted(_words(text) & forbidden):
            if w in seen:
                continue
            seen.add(w)
            issues.append({"rule": "R2", "severity": "error", "field": field,
                           "message": f"'{w}' breaks the tech level ({bible['tech_level']})."})

    # R3 lore
    for field, text in _text_fields(char):
        for lc in bible.get("lore_contradictions", []):
            m = re.search(lc["pattern"], text, re.IGNORECASE)
            if m:
                issues.append({"rule": "R3", "severity": "error", "field": field,
                               "message": f"\"{m.group(0)}\" contradicts lore: {lc['fact']}"})

    # R4 palette
    off = [c for c in char.get("palette", []) if c.lower() not in [x.lower() for x in faction["colors"]]]
    if off:
        issues.append({"rule": "R4", "severity": "warning", "field": "palette",
                       "message": f"Colour(s) {', '.join(off)} are not in the {char['faction']} palette "
                                  f"({', '.join(faction['colors'])})."})

    # R5 naming
    name = char.get("name", "")
    if name and not any(name.lower().startswith(s.lower()) for s in faction["name_starts"]):
        issues.append({"rule": "R5", "severity": "warning", "field": "name",
                       "message": f"'{name}' does not follow {char['faction']} naming "
                                  f"(should start with e.g. {', '.join(faction['name_starts'][:4])})."})
    return issues


def check_dialogue(lines, bible):
    issues = []
    limit = bible["max_dialogue_words"]
    for i, line in enumerate(lines):
        spoken = line.split(":", 1)[-1]
        n = len(spoken.split())
        if n > limit:
            issues.append({"rule": "R6", "severity": "warning", "field": "dialogue",
                           "message": f"Line {i + 1} has {n} words (limit {limit})."})
        for w in sorted(_words(spoken) & set(bible["forbidden_tech"])):
            issues.append({"rule": "R2", "severity": "error", "field": "dialogue",
                           "message": f"Line {i + 1}: '{w}' breaks the tech level."})
    return issues


def score(issues):
    return max(0, 100 - sum(PENALTY[i["severity"]] for i in issues))


def has_errors(issues):
    return any(i["severity"] == "error" for i in issues)
