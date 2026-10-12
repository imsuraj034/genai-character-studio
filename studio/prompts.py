"""Prompt templates. Every prompt is grounded in the Game Bible.

The offline engine does not need these to generate, but they are still built
so token cost can be measured exactly as it would be for a real model.
"""
import json

from .game_bible import bible_summary

CHARACTER_SCHEMA = {
    "name": "string", "age": "integer", "appearance": "string", "palette": ["colour"],
    "abilities": [{"name": "string", "element": "string", "description": "string"}],
    "signature_item": "string", "backstory": "string (3-4 sentences)", "motivation": "string",
    "flaw": "string", "catchphrase": "string", "visual_prompt": "string",
}

SYSTEM = (
    "You are a narrative designer for a video game. Obey the GAME BIBLE exactly. "
    "Never copy existing copyrighted characters, names or franchises. "
    "Keep content suitable for the stated age rating. Reply with JSON only."
)


def character_prompt(spec, bible):
    return (
        f"{SYSTEM}\n\nGAME BIBLE:\n{bible_summary(bible)}\n\n"
        f"TASK: Create one original character.\n"
        f"Role: {spec['role']}. Faction: {spec['faction']}. Class: {spec['char_class']}. "
        f"Pronouns: {spec['pronouns']}. Personality: {spec['personality']}.\n"
        f"Abilities must only use the faction's elements: "
        f"{', '.join(bible['factions'][spec['faction']]['elements'])}.\n"
        f"Designer notes: {spec.get('notes') or 'none'}\n"
        f"Return JSON matching this schema: {json.dumps(CHARACTER_SCHEMA)}"
    )


def repair_prompt(character, issues, bible):
    problems = "\n".join(f"- [{i['field']}] {i['message']}" for i in issues)
    return (
        f"{SYSTEM}\n\nGAME BIBLE:\n{bible_summary(bible)}\n\n"
        f"The character below breaks these rules:\n{problems}\n"
        f"Rewrite ONLY the listed fields so every rule is satisfied. Keep everything else.\n"
        f"CHARACTER: {json.dumps(character)}"
    )


def dialogue_prompt(character, situation, n, bible):
    return (
        f"{SYSTEM}\n\nGAME BIBLE:\n{bible_summary(bible)}\n\n"
        f"CHARACTER: {character['name']}, a {character['personality']} {character['faction']} "
        f"{character['char_class']}. Catchphrase: \"{character['catchphrase']}\".\n"
        f"Write {n} short in-voice dialogue lines (max {bible['max_dialogue_words']} words each) "
        f"for the situation: {situation}. Return JSON: {{\"lines\": [\"...\"]}}"
    )


def variations_prompt(character, arcs, bible):
    return (
        f"{SYSTEM}\n\nGAME BIBLE:\n{bible_summary(bible)}\n\n"
        f"CHARACTER: {json.dumps({k: character[k] for k in ('name', 'faction', 'char_class', 'backstory', 'signature_item')})}\n"
        f"Write one story arc for each of these types: {', '.join(arcs)}. "
        f"Return JSON: {{\"arcs\": [{{\"type\": str, \"title\": str, \"logline\": str, "
        f"\"beats\": [str, str, str], \"ending\": str}}]}}"
    )
