"""Drives the real Streamlit UI headlessly.  Run:  python tests/test_app_ui.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

from studio import review

APP = str(ROOT / "app.py")


def fresh_app():
    # keep tests from touching the real history file
    review.HISTORY_PATH = ROOT / "data" / "_test_history.json"
    review.HISTORY_PATH.unlink(missing_ok=True)
    review.ReviewStore.__init__.__defaults__ = (review.HISTORY_PATH, False)
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def generate(at, scenario):
    at.selectbox(key="scenario").set_value(scenario).run()
    at.button[[b.label for b in at.button].index("Generate character")].click().run()
    assert not at.exception, at.exception
    return " ".join(m.value for m in at.markdown) + " ".join(e.value for e in at.error)


def test_full_ui_flow():
    at = run_scenarios()
    dialogue_review_export(at)
    review.HISTORY_PATH.unlink(missing_ok=True)


def run_scenarios():
    at = fresh_app()
    out = generate(at, "Unsafe brief (graphic violence)")
    assert "Blocked" in out and "graphic violence" in out
    out = generate(at, "Prompt injection attempt")
    assert "prompt-injection" in out
    out = generate(at, "Copycat name: Pikachoo")
    assert "Pikachu" in out
    out = generate(at, "Franchise reference (Jedi)")
    assert "jedi" in out
    out = generate(at, "High creativity (AI breaks rules)")
    res = at.session_state.last_result
    assert res["temperature"] == 1.0 and res["spec"]["custom_name"] == ""
    assert "Fully consistent" in out or res["score"] >= 90
    at.selectbox(key="scenario").set_value("Normal brief").run()
    assert len(at.session_state.store.items) == 3  # 2 copyright-flagged + 1 creative
    print("PASS scenarios")
    return at


def dialogue_review_export(at):
    at.button[[b.label for b in at.button].index("Generate dialogue")].click().run()
    at.button[[b.label for b in at.button].index("Generate story variations")].click().run()
    assert not at.exception, at.exception
    cid = at.session_state.current_id
    extras = at.session_state.store.items[cid]["extras"]
    assert len(extras["dialogue"]) == 2 and len(extras["arcs"]) == 3
    at.button[[b.label for b in at.button].index("Approve")].click().run()
    assert not at.exception, at.exception
    assert at.session_state.store.items[cid]["status"] == "approved"
    labels = [b.label for b in at.get("download_button")] if hasattr(at, "get") else []
    print("PASS dialogue + review + export", labels[:3])


if __name__ == "__main__":
    test_full_ui_flow()
