"""Capture high-resolution screenshots of the running app (http://localhost:8501) with headless Edge.

Run the app first, then:  python docs/capture_screens.py
"""
import base64
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

import sys

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = Path(__file__).resolve().parent / "screenshots"
PORT = 9333
W, H = 1600, 1000


class Page:
    def __init__(self):
        self.proc = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={PORT}",
                                      f"--user-data-dir={tempfile.mkdtemp()}", f"--window-size={W},{H}",
                                      "--hide-scrollbars", "--force-dark-mode", "about:blank"])
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                ws = next(t for t in tabs if t["type"] == "page")["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.2)
        self.ws = websocket.create_connection(ws, timeout=60, suppress_origin=True)
        self.n = 0
        self.cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1.5, mobile=False)

    def cmd(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                return msg.get("result", {})

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        return r.get("result", {}).get("value")

    def wait(self, s):
        time.sleep(s)

    def shot(self, name):
        self.wait(0.8)
        data = self.cmd("Page.captureScreenshot", format="png")["data"]
        OUT.mkdir(exist_ok=True)
        (OUT / f"{name}.png").write_bytes(base64.b64decode(data))
        print("saved", name)

    def close(self):
        self.ws.close()
        self.proc.kill()


TAB = "[...document.querySelectorAll('[role=tab]')].find(b=>b.innerText.includes('{}')).click()"
BTN = "[...document.querySelectorAll('button')].find(b=>b.innerText.includes('{}'))?.click()"
SCROLL = ("(()=>{{const e=[...document.querySelectorAll('{sel}')].find(x=>x.innerText.includes('{txt}'));"
          "if(e){{e.scrollIntoView({{block:'start'}}); "
          "const m=document.querySelector('[data-testid=stMain]')||document.scrollingElement; "
          "m.scrollBy && m.scrollBy(0,-{off});}} return !!e}})()")
SET_TEXTAREA = """(()=>{const t=[...document.querySelectorAll('textarea')].find(x=>x.placeholder.includes('lighthouse'));
const s=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set; s.call(t, %s);
t.dispatchEvent(new Event('input',{bubbles:true})); t.blur(); return true})()"""


def scroll(p, sel, txt, off=20):
    p.js(SCROLL.format(sel=sel, txt=txt, off=off))


def top(p):
    p.js("(document.querySelector('[data-testid=stMain]')||document.scrollingElement).scrollTo(0,0); window.scrollTo(0,0)")


def main():
    p = Page()
    try:
        p.cmd("Page.navigate", url=URL)
        p.wait(7)
        assert p.js("document.title") == "Character Design Studio", f"{URL} is not the Character Studio"
        # reset to a clean session so screenshots are tidy
        p.js(BTN.format("Reset session"))
        p.wait(3)
        top(p)
        p.shot("01_overview")

        p.js(TAB.format("Game Bible"))
        p.wait(1.5)
        scroll(p, ".sec", "Four factions", 120)
        p.shot("02_game_bible")

        # generate until we get a run that needed repair (good story for the deck)
        p.js(TAB.format("Generate"))
        p.wait(1.5)
        for _ in range(8):
            p.js(BTN.format("Generate character"))
            p.wait(3)
            if p.js("document.body.innerText.includes('What the AI got wrong')"):
                break
        top(p)
        scroll(p, ".sec", "Pipeline output", 60)
        p.shot("03_generate_result")
        scroll(p, ".sec", "What the AI got wrong", 20)
        p.shot("04_self_correction")

        # dialogue + story on this character
        p.js(TAB.format("Dialogue"))
        p.wait(1.5)
        p.js(BTN.format("Generate dialogue"))
        p.wait(2.5)
        p.js(BTN.format("Generate story variations"))
        p.wait(2.5)
        top(p)
        scroll(p, ".sec", "Lines in the character", 120)
        p.shot("05_dialogue_story")

        # review
        p.js(TAB.format("Designer Review"))
        p.wait(2)
        top(p)
        scroll(p, "[data-testid=stSelectbox]", "Character", 10)
        p.shot("06_review")
        scroll(p, ".sec", "Choose the portrait", 20)
        p.shot("07_concept_art")
        p.js(BTN.format("Approve"))
        p.wait(2)

        # guardrail: unsafe brief
        p.js(TAB.format("Generate"))
        p.wait(1.5)
        p.js(SET_TEXTAREA % json.dumps("Their village was a gory bloodbath and they tortured prisoners"))
        p.wait(1)
        p.js(BTN.format("Generate character"))
        p.wait(3)
        top(p)
        scroll(p, ".sec", "Pipeline output", 60)
        p.shot("08_guardrail_block")

        # a few more generations so the cost page has data, including a cache hit
        p.js(SET_TEXTAREA % json.dumps(""))
        p.wait(1)
        for _ in range(3):
            p.js(BTN.format("Generate character"))
            p.wait(2.5)
        p.js(TAB.format("Cost"))
        p.wait(2.5)
        top(p)
        p.shot("09_cost")

        p.js(TAB.format("Export"))
        p.wait(2)
        top(p)
        scroll(p, ".sec", "Approved characters", 40)
        p.shot("10_export")
    finally:
        p.close()


if __name__ == "__main__":
    main()
