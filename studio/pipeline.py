"""The AI-assisted design workflow.

    Designer spec
      -> [1] Input guardrail (safety + prompt injection + IP)
      -> [2] Cache lookup / budget check
      -> [3] Generate (grounded in Game Bible)
      -> [4] Output guardrail (safety + copyright)
      -> [5] Consistency check vs Game Bible
      -> [6] Auto-repair loop (regenerate only broken fields, max N rounds)
      -> [7] Human designer review (approve / edit / reject)
"""
import json
import re
import time
import uuid

from . import consistency, prompts, safety


def _timed(fn, *a, **kw):
    t = time.perf_counter()
    out = fn(*a, **kw)
    return out, time.perf_counter() - t


def run_character_pipeline(spec, bible, engine, ledger, temperature=0.7, seed=1,
                           auto_repair=True, max_repairs=2):
    """Returns a result dict with every intermediate step, for display."""
    steps = []
    result = {"steps": steps, "character": None, "blocked": False, "drafts": []}

    # [1] input guardrail
    input_issues = safety.scan_input(spec)
    steps.append({"step": "Input guardrail", "ok": not safety.is_blocked(input_issues), "issues": input_issues})
    if safety.is_blocked(input_issues):
        result["blocked"] = True
        result["block_reason"] = "Designer input was blocked before reaching the model."
        return result

    # [2] budget + cache
    if ledger.over_budget():
        steps.append({"step": "Budget check", "ok": False,
                      "issues": [{"message": f"Session budget of ${ledger.budget_usd:.2f} reached."}]})
        result["blocked"] = True
        result["block_reason"] = "Budget cap reached. Raise it in the sidebar or reuse cached results."
        return result
    payload = {"spec": spec, "t": temperature, "seed": seed, "engine": engine.model_id,
               "bible": bible["world_name"], "factions": sorted(bible["factions"])}
    key = ledger.cache_key("character", payload)
    cached = ledger.cached(key)
    prompt = prompts.character_prompt(spec, bible)

    # [3] generate
    if cached:
        char, secs = json.loads(cached), 0.0
        ledger.record("character", engine.model_id, prompt, cached, secs, key, cache_hit=True)
        steps.append({"step": "Generate (cache hit - free)", "ok": True, "issues": []})
    else:
        char, secs = _timed(engine.character, spec, bible, temperature, seed)
        out = json.dumps(char)
        ledger.record("character", engine.model_id, prompt, out, secs, key, result=out)
        steps.append({"step": f"Generate with {engine.name}", "ok": True, "issues": [],
                      "ms": round(secs * 1000, 1)})
    char["id"] = spec.get("id") or uuid.uuid4().hex[:8]

    # [4] + [5] checks
    def evaluate(c):
        return safety.scan_output(c), consistency.check_character(c, bible)

    out_issues, rule_issues = evaluate(char)
    result["drafts"].append({"label": "AI draft", "character": dict(char),
                             "safety": out_issues, "issues": rule_issues,
                             "score": consistency.score(rule_issues)})
    steps.append({"step": "Output guardrail", "ok": not safety.is_blocked(out_issues), "issues": out_issues})
    steps.append({"step": "Consistency check", "ok": not consistency.has_errors(rule_issues),
                  "issues": rule_issues, "score": consistency.score(rule_issues)})

    # [6] auto-repair loop
    rounds = 0
    while auto_repair and rounds < max_repairs:
        fixable = list(rule_issues)
        fixable += [{"field": "name", "message": i["message"]} for i in out_issues if i["category"] == "character name"]
        fixable += [{"field": "visual_prompt", "message": i["message"]} for i in out_issues
                    if i["category"] == "artist / studio style"]
        if spec.get("custom_name"):  # respect the designer's chosen name
            fixable = [f for f in fixable if f["field"] != "name"]
        if not fixable:
            break
        rounds += 1
        rprompt = prompts.repair_prompt(char, fixable, bible)
        fixed, secs = _timed(engine.repair, char, fixable, bible, seed + rounds)
        fixed["id"] = char["id"]
        ledger.record("repair", engine.model_id, rprompt, json.dumps(fixed), secs)
        before = consistency.score(rule_issues)
        char = fixed
        out_issues, rule_issues = evaluate(char)
        result["drafts"].append({"label": f"Auto-repair round {rounds}", "character": dict(char),
                                 "safety": out_issues, "issues": rule_issues,
                                 "score": consistency.score(rule_issues), "fixed": fixable})
        steps.append({"step": f"Auto-repair round {rounds}", "ok": not consistency.has_errors(rule_issues),
                      "issues": rule_issues,
                      "note": f"Fixed {len(fixable)} issue(s); score {before} -> {consistency.score(rule_issues)}"})

    if safety.is_blocked(out_issues):
        result["blocked"] = True
        result["block_reason"] = "Generated content failed the safety filter and was withheld."
    result["character"] = char
    result["safety"] = out_issues
    result["issues"] = rule_issues
    result["score"] = consistency.score(rule_issues)
    steps.append({"step": "Ready for designer review", "ok": not result["blocked"], "issues": []})
    return result


def run_dialogue(char, situation, n, bible, engine, ledger, temperature=0.7, seed=1):
    prompt = prompts.dialogue_prompt(char, situation, n, bible)
    key = ledger.cache_key("dialogue", {"c": char, "s": situation, "n": n, "t": temperature,
                                        "seed": seed, "e": engine.model_id})
    cached = ledger.cached(key)
    if cached:
        lines = json.loads(cached)
        ledger.record("dialogue", engine.model_id, prompt, cached, 0, key, cache_hit=True)
    else:
        lines, secs = _timed(engine.dialogue, char, situation, n, bible, temperature, seed)
        out = json.dumps(lines)
        ledger.record("dialogue", engine.model_id, prompt, out, secs, key, result=out)
    text = " ".join(lines)
    return {"lines": lines, "safety": safety.scan_text(text),
            "issues": consistency.check_dialogue(lines, bible), "cached": bool(cached)}


def run_variations(char, arcs, bible, engine, ledger, temperature=0.7, seed=1):
    prompt = prompts.variations_prompt(char, arcs, bible)
    key = ledger.cache_key("variations", {"c": char, "a": arcs, "seed": seed, "e": engine.model_id})
    cached = ledger.cached(key)
    if cached:
        out_arcs = json.loads(cached)
        ledger.record("variations", engine.model_id, prompt, cached, 0, key, cache_hit=True)
    else:
        out_arcs, secs = _timed(engine.variations, char, arcs, bible, temperature, seed)
        out = json.dumps(out_arcs)
        ledger.record("variations", engine.model_id, prompt, out, secs, key, result=out)
    checked = []
    for a in out_arcs:
        text = " ".join([a.get("logline", ""), *a.get("beats", []), a.get("ending", "")])
        issues = []
        for lc in bible.get("lore_contradictions", []):
            m = re.search(lc["pattern"], text, re.IGNORECASE)
            if m:
                issues.append({"rule": "R3", "severity": "error", "field": "story",
                               "message": f"\"{m.group(0)}\" contradicts lore: {lc['fact']}"})
        checked.append({**a, "safety": safety.scan_text(text), "issues": issues})
    return checked
