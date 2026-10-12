# 🎮 GenAI Character Design Studio — Case Study 65

An AI-assisted game-design workflow that generates **character concepts, dialogue and story variations**
while staying consistent with the game's rules and narrative. It also handles **copyright, inappropriate
content, computational cost and human creative control**.

Runs fully **offline with no API key**. If [Ollama](https://ollama.com) is installed with `llama3.2`, it switches
to a free local LLM automatically.

## Run it

Double-click **`run.bat`**, or run:

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

The app opens at http://localhost:8501.

## What's inside

| Tab | Shows |
|---|---|
| 🏗️ How it works | Pipeline diagram and a requirement → solution map |
| 📖 Game Bible | World rules, lore, factions; editable JSON |
| 🧙 Generate | Brief → guardrails → generate → check → auto-repair, with demo scenarios |
| 💬 Dialogue & Story | In-voice dialogue per situation, 5 story-arc types |
| ✅ Designer Review | Approve / reject / edit / regenerate, version history with diffs |
| 💰 Cost | Tokens, cache hits, model routing savings, budget |
| 📦 Export | JSON + PDF character sheet (approved characters only) |

```
app.py                 Streamlit UI
studio/game_bible.py   Game Bible (rules, lore, factions)
studio/engines.py      Offline engine + Ollama engine
studio/prompts.py      Bible-grounded prompts
studio/safety.py       Content, prompt-injection and copyright guardrails
studio/consistency.py  Rules R1–R7 and scoring
studio/pipeline.py     Orchestration and auto-repair loop
studio/cost.py         Tokens, cache, routing, budget
studio/review.py       Versioned human review
studio/export.py       JSON / PDF export
tests/                 8 automated tests (incl. headless UI test)
docs/                  Report PDF, slides PPTX, demo script, evaluation
```

## Tests and docs

```bash
python -m pytest -q
```

```bash
python docs/build_docs.py
```

The second command re-runs the evaluation and rebuilds the report and slides.
