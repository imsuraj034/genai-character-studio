"""Human-in-the-loop review: every AI output and designer action is versioned.

The designer always has final creative control: nothing is "approved" without
an explicit human action, and every change is attributed (AI vs Designer).
"""
import copy
import difflib
import json
import time

from .game_bible import DATA_DIR

HISTORY_PATH = DATA_DIR / "history.json"


class ReviewStore:
    def __init__(self, path=HISTORY_PATH, persist=True):
        self.path = path
        self.persist = persist
        self.items = {}
        if persist and path.exists():
            try:
                self.items = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.items = {}

    def _save(self):
        if self.persist:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_version(self, char, author, action, score=None, note="", extras=None):
        cid = char["id"]
        item = self.items.setdefault(cid, {"status": "pending", "versions": [], "extras": {}})
        item["versions"].append({
            "v": len(item["versions"]) + 1,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "author": author, "action": action, "score": score, "note": note,
            "character": copy.deepcopy(char),
        })
        if extras:
            item["extras"].update(extras)
        if action not in ("approved", "rejected"):
            item["status"] = "pending"
        self._save()
        return item["versions"][-1]

    def set_extras(self, cid, **extras):
        self.items[cid]["extras"].update(extras)
        self._save()

    def log(self, cid, action, note="", author="Designer"):
        """Record a designer action (no content change) in the version history."""
        item = self.items[cid]
        latest = item["versions"][-1]
        item["versions"].append({**copy.deepcopy(latest), "v": latest["v"] + 1,
                                 "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                                 "author": author, "action": action, "note": note})
        self._save()

    def set_status(self, cid, status, note=""):
        self.items[cid]["status"] = status
        self.log(cid, status, note)

    def latest(self, cid):
        return self.items[cid]["versions"][-1]["character"]

    def approved(self):
        return {cid: it for cid, it in self.items.items() if it["status"] == "approved"}

    def delete(self, cid):
        self.items.pop(cid, None)
        self._save()

    @staticmethod
    def diff(a, b):
        fa = json.dumps(a, indent=1, ensure_ascii=False).splitlines()
        fb = json.dumps(b, indent=1, ensure_ascii=False).splitlines()
        return "\n".join(difflib.unified_diff(fa, fb, "before", "after", lineterm="", n=0))
