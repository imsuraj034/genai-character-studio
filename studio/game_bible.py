"""The Game Bible: the single source of truth every generated asset must obey.

Designers edit this (in the UI or data/game_bible.json). The generator reads it
to build prompts, and the consistency checker reads it to validate outputs.
"""
import copy
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BIBLE_PATH = DATA_DIR / "game_bible.json"

DEFAULT_BIBLE = {
    "world_name": "Aethervale",
    "genre": "High-fantasy action RPG",
    "tone": "Heroic and hopeful, with light humour",
    "age_rating": "PEGI 12",
    "art_style": "Hand-painted cel-shaded look, soft rim lighting, readable silhouettes",
    "tech_level": "Medieval: no firearms, no electricity, no modern machines",
    "forbidden_tech": [
        "gun", "pistol", "rifle", "shotgun", "laser", "robot", "cyborg", "electricity",
        "electric", "car", "computer", "phone", "plastic", "drone", "neon", "jetpack",
    ],
    "lore_facts": [
        "The Sun-Crown shattered 300 years ago, splitting the land into four factions.",
        "Dragons are extinct; only their bones and old songs remain.",
        "Magic comes from Aether shards, and each faction can only channel its own elements.",
        "The free market city of Lumen Ford is neutral ground for all factions.",
    ],
    # Patterns that contradict lore. Checked by the consistency checker.
    "lore_contradictions": [
        {
            "pattern": r"\b(rides?|riding|tamed?|tames|pet|companion|living|young|hatchling)\b[^.]{0,25}\bdragons?\b",
            "fact": "Dragons are extinct; only their bones and old songs remain.",
        },
        {
            "pattern": r"\b(rebuilt|restored|wears|wearing|wields)\b[^.]{0,20}\bsun-crown\b",
            "fact": "The Sun-Crown shattered 300 years ago and has never been restored.",
        },
    ],
    "factions": {
        "Frost Clan": {
            "elements": ["ice"],
            "homeland": "the Glacier Spires of Nordhal",
            "values": ["honour", "endurance", "loyalty"],
            "colors": ["silver", "pale blue", "white", "steel grey"],
            "name_starts": ["Ska", "Thor", "Vey", "Rin", "Hal", "Fros", "Ny", "Kael"],
            "name_ends": ["dra", "rik", "ven", "ja", "holt", "mir"],
            "rival": "Ember Covenant",
            "signature_items": ["a rime-forged greataxe", "a glacier-glass lantern", "a wolf-fur mantle stitched with runes"],
        },
        "Ember Covenant": {
            "elements": ["fire"],
            "homeland": "the Caldera of Pyrr",
            "values": ["passion", "ambition", "renewal"],
            "colors": ["crimson", "ember orange", "charcoal", "gold"],
            "name_starts": ["Pyr", "Ash", "Ignis", "Sol", "Cind", "Vul", "Ra", "Brann"],
            "name_ends": ["ax", "ra", "ion", "eth", "is", "ora"],
            "rival": "Frost Clan",
            "signature_items": ["a basalt flame-staff", "a smouldering brass censer", "an ash-grey war banner"],
        },
        "Verdant Circle": {
            "elements": ["nature", "earth"],
            "homeland": "the Elderroot Forest",
            "values": ["balance", "patience", "community"],
            "colors": ["moss green", "bark brown", "amber", "cream"],
            "name_starts": ["Syl", "Fen", "Oak", "Wil", "Bry", "Thal", "Mos", "Elo"],
            "name_ends": ["wyn", "lin", "ora", "eth", "ric", "a"],
            "rival": "Tidecallers",
            "signature_items": ["a living-wood longbow", "a seed pouch that hums softly", "a mask carved from elder bark"],
        },
        "Tidecallers": {
            "elements": ["water", "storm"],
            "homeland": "the Coral Isles of Maranel",
            "values": ["freedom", "curiosity", "trade"],
            "colors": ["teal", "deep navy", "pearl", "sea green"],
            "name_starts": ["Mar", "Nai", "Cor", "Del", "Wav", "Sel", "Ond", "Tem"],
            "name_ends": ["ina", "ys", "el", "ara", "o", "en"],
            "rival": "Verdant Circle",
            "signature_items": ["a coral trident", "a storm-glass compass", "a conch that echoes distant waves"],
        },
    },
    "classes": ["Warrior", "Mage", "Rogue", "Healer", "Ranger", "Bard"],
    "roles": ["Protagonist", "Companion", "Villain", "Merchant NPC", "Quest Giver", "Boss"],
    "neutral_places": ["Lumen Ford", "the Shattered Crown ruins", "the Whispering Pass"],
    "max_dialogue_words": 28,
}


def default_bible():
    return copy.deepcopy(DEFAULT_BIBLE)


def load_bible():
    if BIBLE_PATH.exists():
        try:
            return json.loads(BIBLE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return default_bible()


def save_bible(bible):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BIBLE_PATH.write_text(json.dumps(bible, indent=2, ensure_ascii=False), encoding="utf-8")


def bible_summary(bible):
    """Compact text version of the bible, injected into every model prompt."""
    lines = [
        f"WORLD: {bible['world_name']} ({bible['genre']}). Tone: {bible['tone']}. Rating: {bible['age_rating']}.",
        f"ART STYLE: {bible['art_style']}.",
        f"TECH LEVEL: {bible['tech_level']}. Never mention: {', '.join(bible['forbidden_tech'])}.",
        "LORE: " + " ".join(bible["lore_facts"]),
        "FACTIONS:",
    ]
    for name, f in bible["factions"].items():
        lines.append(
            f"- {name}: elements={'/'.join(f['elements'])}; home={f['homeland']}; "
            f"values={', '.join(f['values'])}; colours={', '.join(f['colors'])}; rival={f['rival']}"
        )
    return "\n".join(lines)
