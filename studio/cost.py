"""Computational cost tracking: tokens, latency, estimated money, caching, budget.

Prices are ILLUSTRATIVE tiers (USD per 1M tokens) so students can reason about
trade-offs; edit them in the sidebar to match a real provider's price list.
"""
import hashlib
import json
import math
import time

DEFAULT_TIERS = {
    "Offline / local model": {"input": 0.0, "output": 0.0},
    "Small cloud model": {"input": 0.25, "output": 1.25},
    "Medium cloud model": {"input": 3.0, "output": 15.0},
    "Large cloud model": {"input": 15.0, "output": 75.0},
}

# Model routing: cheap tier for short/simple tasks, bigger tier for creative ones.
ROUTING = {
    "character": "Medium cloud model",
    "repair": "Small cloud model",
    "dialogue": "Small cloud model",
    "variations": "Medium cloud model",
}


def estimate_tokens(text):
    """~4 characters per token for English (standard rule of thumb)."""
    return max(1, math.ceil(len(text) / 4))


class CostLedger:
    def __init__(self, tiers=None, budget_usd=0.50):
        self.tiers = tiers or {k: dict(v) for k, v in DEFAULT_TIERS.items()}
        self.budget_usd = budget_usd
        self.entries = []
        self._cache = {}

    def cache_key(self, task, payload):
        return hashlib.sha256(f"{task}|{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()[:16]

    def cached(self, key):
        return self._cache.get(key)

    def price(self, tier, tin, tout):
        t = self.tiers[tier]
        return (tin * t["input"] + tout * t["output"]) / 1_000_000

    def record(self, task, engine, prompt, output, seconds, cache_key=None, cache_hit=False, result=None):
        tin, tout = estimate_tokens(prompt), estimate_tokens(output)
        tier = ROUTING.get(task, "Medium cloud model")
        cost = 0.0 if cache_hit else self.price(tier, tin, tout)
        entry = {
            "time": time.strftime("%H:%M:%S"), "task": task, "engine": engine,
            "routed_tier": tier, "input_tokens": tin, "output_tokens": tout,
            "latency_ms": round(seconds * 1000, 1), "est_cost_usd": round(cost, 6),
            "cache_hit": cache_hit,
            "if_large_model_usd": round(self.price("Large cloud model", tin, tout), 6),
        }
        self.entries.append(entry)
        if cache_key and result is not None and not cache_hit:
            self._cache[cache_key] = result
        return entry

    @property
    def spent(self):
        return sum(e["est_cost_usd"] for e in self.entries)

    @property
    def saved_by_cache(self):
        return sum(self.price(e["routed_tier"], e["input_tokens"], e["output_tokens"])
                   for e in self.entries if e["cache_hit"])

    @property
    def saved_by_routing(self):
        return sum(e["if_large_model_usd"] - e["est_cost_usd"] for e in self.entries if not e["cache_hit"])

    def over_budget(self):
        return self.spent >= self.budget_usd

    def totals(self):
        return {
            "calls": len(self.entries),
            "cache_hits": sum(e["cache_hit"] for e in self.entries),
            "input_tokens": sum(e["input_tokens"] for e in self.entries),
            "output_tokens": sum(e["output_tokens"] for e in self.entries),
            "spent_usd": self.spent,
            "saved_cache_usd": self.saved_by_cache,
            "saved_routing_usd": self.saved_by_routing,
        }
