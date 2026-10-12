"""Safety and copyright guardrails.

Runs on the designer's INPUT (before generation) and on the model's OUTPUT
(after generation). Three checks:
  1. Inappropriate content for the age rating (blocked)
  2. Prompt-injection attempts in designer notes (blocked)
  3. Copyright / IP similarity to famous characters, franchises and artist styles (flagged)
"""
import re
from difflib import SequenceMatcher

# Category -> terms. Kept deliberately mild; a production system would use a
# trained moderation classifier in addition to this list.
CONTENT_RULES = {
    "graphic violence": ["gore", "gory", "dismember", "dismembered", "decapitate", "decapitated",
                         "disembowel", "torture", "tortured", "mutilate", "bloodbath", "massacre"],
    "sexual content": ["nude", "naked", "sexual", "sexy", "erotic", "explicit", "seductive"],
    "self-harm": ["suicide", "self-harm", "self harm", "cutting herself", "cutting himself"],
    "drugs": ["cocaine", "heroin", "meth", "overdose"],
    "hate / harassment": ["slur", "racist", "genocide", "ethnic cleansing", "nazi"],
    "strong profanity": ["fuck", "shit", "bitch", "bastard"],
}

INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|above|prior) (instructions|rules)",
    r"disregard (the )?(game bible|rules|instructions)",
    r"you are no longer",
    r"system prompt",
    r"jailbreak",
]

# Well-known protected characters and franchises (sample list).
PROTECTED_NAMES = [
    "Mario", "Luigi", "Pikachu", "Link", "Zelda", "Ganondorf", "Kratos", "Master Chief", "Lara Croft",
    "Geralt", "Yennefer", "Sonic", "Kirby", "Cloud Strife", "Sephiroth", "Solid Snake", "Ezio",
    "Arthas", "Sylvanas", "Samus", "Donkey Kong", "Pac-Man", "Steve", "Harry Potter", "Hermione",
    "Gandalf", "Frodo", "Aragorn", "Darth Vader", "Yoda", "Spider-Man", "Batman", "Elsa", "Goku",
    "Naruto", "Aloy", "Doomguy", "Ellie", "Joel", "Kirito",
]
FRANCHISE_TERMS = [
    "hogwarts", "jedi", "sith", "lightsaber", "triforce", "hyrule", "pokemon", "pokeball", "mushroom kingdom",
    "azeroth", "tamriel", "middle-earth", "mordor", "witcher", "spartan-117", "chakra", "super saiyan",
]
STYLE_PATTERNS = [
    r"in the style of ([A-Z]\w*(?: [A-Z]\w*){0,3})",
    r"\b(Studio Ghibli|Pixar|Disney|Greg Rutkowski|Akira Toriyama|Hayao Miyazaki)\b",
]
# Trait combinations strongly associated with a famous character.
SIGNATURE_TRAITS = [
    ({"red", "cap", "plumber"}, "Mario"),
    ({"lightning", "scar", "wizard"}, "Harry Potter"),
    ({"blue", "hedgehog"}, "Sonic"),
    ({"green", "tunic", "sword", "fairy"}, "Link"),
    ({"white", "hair", "witcher"}, "Geralt"),
    ({"bald", "ash", "spartan"}, "Kratos"),
]


def _norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def _contains(text, term):
    return re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", text) is not None


def check_content(text):
    low = text.lower()
    hits = []
    for cat, terms in CONTENT_RULES.items():
        for t in terms:
            if _contains(low, t):
                hits.append({"category": cat, "term": t, "severity": "block",
                             "message": f"Inappropriate for the age rating ({cat}): '{t}'."})
    return hits


def check_injection(text):
    low = text.lower()
    return [{"category": "prompt injection", "term": m.group(0), "severity": "block",
             "message": f"Possible prompt-injection attempt: '{m.group(0)}'."}
            for p in INJECTION_PATTERNS for m in [re.search(p, low)] if m]


def name_similarity(name):
    """Best match of a character name against protected names (0-1)."""
    best, who = 0.0, None
    tokens = [name] + name.split()
    for pn in PROTECTED_NAMES:
        for tok in tokens:
            s = SequenceMatcher(None, _norm(tok), _norm(pn)).ratio()
            if s > best:
                best, who = s, pn
    return best, who


def check_copyright(char_or_text, name=None):
    if isinstance(char_or_text, dict):
        name = char_or_text.get("name", "")
        text = " ".join(str(v) for k, v in char_or_text.items() if isinstance(v, str))
        text += " " + " ".join(f"{a.get('name', '')} {a.get('description', '')}" for a in char_or_text.get("abilities", []))
    else:
        text = char_or_text
    flags = []
    if name:
        sim, who = name_similarity(name)
        if sim >= 0.8:
            flags.append({"category": "character name", "term": name, "severity": "flag",
                          "message": f"Name '{name}' is {sim:.0%} similar to the protected character '{who}'."})
    low = text.lower()
    for term in FRANCHISE_TERMS:
        if _contains(low, term):
            flags.append({"category": "franchise term", "term": term, "severity": "flag",
                          "message": f"'{term}' belongs to an existing franchise."})
    for p in STYLE_PATTERNS:
        m = re.search(p, text)
        if m:
            flags.append({"category": "artist / studio style", "term": m.group(0), "severity": "flag",
                          "message": f"\"{m.group(0)}\" imitates a specific studio or artist's style. "
                                     f"Describe the style in your own words instead."})
            break
    words = set(re.findall(r"[a-z]+", low))
    for traits, who in SIGNATURE_TRAITS:
        if traits <= words:
            flags.append({"category": "signature traits", "term": ", ".join(sorted(traits)), "severity": "flag",
                          "message": f"Trait combination ({', '.join(sorted(traits))}) closely resembles '{who}'."})
    return flags


def scan_input(spec):
    text = " ".join(str(spec.get(k, "")) for k in ("notes", "custom_name"))
    issues = check_content(text) + check_injection(text)
    if spec.get("custom_name"):
        issues += check_copyright(text, name=spec["custom_name"])
    return issues


def scan_output(char):
    text = " ".join(str(v) for v in char.values() if isinstance(v, str))
    text += " " + " ".join(a.get("description", "") for a in char.get("abilities", []))
    return check_content(text) + check_copyright(char)


def scan_text(text):
    return check_content(text) + check_copyright(text)


def is_blocked(issues):
    return any(i["severity"] == "block" for i in issues)


def redact(text):
    """Mask blocked terms so flagged output can still be shown safely."""
    for terms in CONTENT_RULES.values():
        for t in terms:
            text = re.sub(rf"(?<![a-zA-Z]){re.escape(t)}(?![a-zA-Z])", "█" * len(t), text, flags=re.IGNORECASE)
    return text
