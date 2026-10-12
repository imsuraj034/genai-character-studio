"""Generation engines.

* OfflineEngine - a seeded procedural generator that needs no internet or API key.
  At high "creativity" (temperature) it deliberately drifts off-bible, imitating
  the mistakes real LLMs make (off-faction magic, anachronisms, lore errors,
  copycat names). That gives the guardrails something real to catch.
* OllamaEngine  - uses a free local open-source model through Ollama, if installed.
  Any field it fails to produce is filled in by the offline engine.
"""
import json
import random
import re

from . import prompts
from .vocab import (ABILITY_POOL, APPEARANCE_BUILDS, APPEARANCE_FEATURES, ARC_TEMPLATES,
                    CLASS_ABILITIES, FLAWS, MOTIVATIONS, PERSONALITIES, SITUATIONS)

# Typical LLM mistakes injected when the engine "drifts".
DRIFT_ITEMS = ["a brass pistol with an engraved grip", "a pocket robot that follows them everywhere",
               "a glowing laser blade"]
DRIFT_LORE = ["As a child, {name} tamed a young dragon that still follows them.",
              "{name} secretly wears the restored Sun-Crown under a hood."]
DRIFT_NAMES = ["Kratoz", "Geralt Ashveil", "Zelda Thornwyn", "Sonik"]
DRIFT_COLORS = ["hot pink", "lime green", "purple"]
DRIFT_STYLE = ", in the style of Studio Ghibli"
POSSESSIVE = {"she/her": "her", "he/him": "his", "they/them": "their"}


def _rng(seed, *parts):
    return random.Random("-".join(str(p) for p in (seed, *parts)))


def drift_probability(temperature):
    """0 below temperature 0.5, rising to 0.6 at temperature 1.0."""
    return max(0.0, min(0.6, (temperature - 0.5) * 1.2))


class OfflineEngine:
    name = "Offline procedural engine"
    model_id = "offline-template-v1"
    available = True

    # ---------- field generators (each field has its own RNG stream) ----------
    def _name(self, spec, faction, seed, drift):
        if spec.get("custom_name"):
            return spec["custom_name"].strip()
        r = _rng(seed, "name")
        if drift and r.random() < drift:
            return r.choice(DRIFT_NAMES)
        return r.choice(faction["name_starts"]) + r.choice(faction["name_ends"])

    def _abilities(self, spec, faction, bible, seed, drift):
        r = _rng(seed, "abilities")
        pool = [(n, d, el) for el in faction["elements"] for n, d in ABILITY_POOL[el]]
        picks = r.sample(pool, k=min(2, len(pool)))
        abilities = [{"name": n, "element": el, "description": d} for n, d, el in picks]
        cls_name, cls_desc = CLASS_ABILITIES[spec["char_class"]]
        abilities.append({"name": cls_name, "element": "aether", "description": cls_desc})
        if drift and r.random() < drift:
            foreign = [el for el in ABILITY_POOL if el not in faction["elements"]]
            el = r.choice(foreign)
            n, d = r.choice(ABILITY_POOL[el])
            abilities[1] = {"name": n, "element": el, "description": d}
        return abilities

    def _item(self, faction, seed, drift):
        r = _rng(seed, "item")
        if drift and r.random() < drift:
            return r.choice(DRIFT_ITEMS)
        return r.choice(faction["signature_items"])

    def _palette(self, faction, seed, drift):
        r = _rng(seed, "palette")
        colors = r.sample(faction["colors"], k=3)
        if drift and r.random() < drift:
            colors[2] = r.choice(DRIFT_COLORS)
        return colors

    def _appearance(self, spec, seed):
        r = _rng(seed, "appearance")
        return f"{r.choice(APPEARANCE_BUILDS).capitalize()}, with {r.choice(APPEARANCE_FEATURES)}."

    def _backstory(self, spec, faction, name, seed, drift):
        r = _rng(seed, "backstory")
        pos = POSSESSIVE.get(spec.get("pronouns"), "their")
        upbringing = r.choice(["in a family of humble crafters", "as an orphan raised by temple keepers",
                               "as the youngest child of a proud war-house", "on the road with travelling traders"])
        event = r.choice([
            f"When the {faction['rival']} burned the border towns, {name} lost everything but {pos} courage.",
            f"A chance meeting in Lumen Ford set {name} on a path no one in {pos} family expected.",
            f"{name} was the only survivor of an expedition into the Shattered Crown ruins.",
            f"Trained in the ways of {' and '.join(faction['values'][:2])}, {name} quickly outgrew {pos} teachers.",
        ])
        story = f"Born in {faction['homeland']}, {name} grew up {upbringing}. {event}"
        if drift and r.random() < drift:
            story += " " + r.choice(DRIFT_LORE).format(name=name)
        notes = (spec.get("notes") or "").strip()
        if notes:
            story += f" {notes.rstrip('.')}."
        return story

    def _visual_prompt(self, char, bible, seed, drift):
        r = _rng(seed, "visual")
        vp = (f"{bible['art_style']}. Full-body concept art of {char['name']}, a {char['faction']} "
              f"{char['char_class'].lower()}. {char['appearance']} Colour palette: {', '.join(char['palette'])}. "
              f"Holding {char['signature_item']}. Background: {bible['factions'][char['faction']]['homeland']}")
        if drift and r.random() < drift:
            vp += DRIFT_STYLE
        return vp + "."

    # ---------- public API ----------
    def character(self, spec, bible, temperature=0.7, seed=1):
        faction = bible["factions"][spec["faction"]]
        drift = drift_probability(temperature)
        r = _rng(seed, "misc")
        name = self._name(spec, faction, seed, drift)
        char = {
            "name": name, "role": spec["role"], "faction": spec["faction"],
            "char_class": spec["char_class"], "pronouns": spec["pronouns"],
            "personality": spec["personality"], "age": r.randint(17, 64),
            "appearance": self._appearance(spec, seed),
            "palette": self._palette(faction, seed, drift),
            "abilities": self._abilities(spec, faction, bible, seed, drift),
            "signature_item": self._item(faction, seed, drift),
            "backstory": self._backstory(spec, faction, name, seed, drift),
            "motivation": f"Wants to {r.choice(MOTIVATIONS)}.",
            "flaw": f"{name} is {r.choice(FLAWS)}.",
            "catchphrase": r.choice(PERSONALITIES[spec["personality"]]["battle"]),
        }
        char["visual_prompt"] = self._visual_prompt(char, bible, seed, drift)
        return char

    def repair(self, char, issues, bible, seed=1):
        """Regenerate only the fields that broke rules, with drift switched off."""
        spec = {k: char[k] for k in ("role", "faction", "char_class", "pronouns", "personality")}
        spec["notes"] = ""
        faction = bible["factions"][char["faction"]]
        fixed = dict(char)
        fields = {i["field"] for i in issues}
        if "name" in fields:
            fixed["name"] = self._name({}, faction, f"{seed}r", 0)
        if "abilities" in fields:
            fixed["abilities"] = self._abilities(spec, faction, bible, seed, 0)
        if "signature_item" in fields:
            fixed["signature_item"] = self._item(faction, seed, 0)
        if "palette" in fields:
            fixed["palette"] = self._palette(faction, seed, 0)
        if "backstory" in fields or "name" in fields:
            fixed["backstory"] = self._backstory(spec, faction, fixed["name"], seed, 0)
        if "name" in fields:
            fixed["flaw"] = fixed["flaw"].replace(char["name"], fixed["name"])
        fixed["visual_prompt"] = self._visual_prompt(fixed, bible, seed, 0)
        return fixed

    def dialogue(self, char, situation, n, bible, temperature=0.7, seed=1):
        r = _rng(seed, "dialogue", situation)
        voice = PERSONALITIES[char["personality"]]
        key = SITUATIONS[situation]
        lines = list(voice[key])
        r.shuffle(lines)
        faction = bible["factions"][char["faction"]]
        flavour = [
            f"By the {faction['homeland'].split(' of ')[-1]} winds, I mean it.",
            f"The {faction['rival']} will hear of this.",
            f"For {faction['values'][0]}!",
            char["catchphrase"],
        ]
        r.shuffle(flavour)
        out = (lines + flavour)[:n]
        return [f"{char['name']}: {line}" for line in out]

    def variations(self, char, arcs, bible, temperature=0.7, seed=1):
        faction = bible["factions"][char["faction"]]
        r = _rng(seed, "arcs")
        fill = {
            "name": char["name"], "faction": char["faction"], "rival": faction["rival"],
            "homeland": faction["homeland"], "item": char["signature_item"],
            "place": r.choice(bible["neutral_places"]),
        }
        out = []
        for arc in arcs:
            t = ARC_TEMPLATES[arc]
            out.append({
                "type": arc,
                "title": f"{char['name']}: {r.choice(['The', 'A'])} {arc}",
                "logline": t["logline"].format(**fill),
                "beats": [b.format(**fill) for b in t["beats"]],
                "ending": t["ending"].format(**fill),
            })
        return out


class OllamaEngine(OfflineEngine):
    """Free local LLM via Ollama (https://ollama.com). No API key needed."""
    url = "http://localhost:11434"

    def __init__(self, model="llama3.2"):
        self.model = model
        self.model_id = f"ollama/{model}"
        self.name = f"Local LLM ({model} via Ollama)"
        self.available = self._ping()

    def _ping(self):
        try:
            import requests
            r = requests.get(f"{self.url}/api/tags", timeout=0.7)
            names = [m["name"].split(":")[0] for m in r.json().get("models", [])]
            return self.model in names
        except Exception:
            return False

    def _ask(self, prompt, temperature):
        import requests
        r = requests.post(f"{self.url}/api/generate", timeout=120, json={
            "model": self.model, "prompt": prompt, "format": "json", "stream": False,
            "options": {"temperature": temperature},
        })
        return json.loads(r.json()["response"])

    def character(self, spec, bible, temperature=0.7, seed=1):
        base = super().character(spec, bible, temperature, seed)
        try:
            data = self._ask(prompts.character_prompt(spec, bible), temperature)
        except Exception:
            return base
        for key in prompts.CHARACTER_SCHEMA:
            if data.get(key):
                base[key] = data[key]
        if spec.get("custom_name"):
            base["name"] = spec["custom_name"]
        if not isinstance(base["abilities"], list) or not all(isinstance(a, dict) for a in base["abilities"]):
            base["abilities"] = super().character(spec, bible, temperature, seed)["abilities"]
        return base

    def dialogue(self, char, situation, n, bible, temperature=0.7, seed=1):
        try:
            data = self._ask(prompts.dialogue_prompt(char, situation, n, bible), temperature)
            lines = [str(x) for x in data.get("lines", [])][:n]
            if lines:
                return [l if l.startswith(char["name"]) else f"{char['name']}: {l}" for l in lines]
        except Exception:
            pass
        return super().dialogue(char, situation, n, bible, temperature, seed)

    def variations(self, char, arcs, bible, temperature=0.7, seed=1):
        try:
            data = self._ask(prompts.variations_prompt(char, arcs, bible), temperature)
            out = data.get("arcs", [])
            if out and all(isinstance(a, dict) and "logline" in a for a in out):
                for a in out:
                    a.setdefault("beats", [])
                    a.setdefault("ending", "")
                    a.setdefault("title", a.get("type", "Arc"))
                return out
        except Exception:
            pass
        return super().variations(char, arcs, bible, temperature, seed)


def get_engine(prefer_local=True, model="llama3.2"):
    if prefer_local:
        eng = OllamaEngine(model)
        if eng.available:
            return eng
    return OfflineEngine()
