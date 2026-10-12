# Demo script (about 4 minutes)

**Before class:** double-click `run.bat`. In the sidebar, click **Reset session** so you start clean.

---

### 1. The problem and the architecture (30 s), tab **Overview**
> "Studios want GenAI for character design, but raw AI output breaks game rules, can copy famous characters,
> can be inappropriate, costs money, and can take control away from designers. So I built a pipeline that puts
> guardrails around the model."

Point at the diagram: brief → input guardrail → cache/budget → generator → output guardrail → consistency
check → auto-repair → **human review** → export. Then point at the requirements table.

### 2. The Game Bible (20 s), tab **Game Bible**
> "Everything is grounded in this Game Bible: 4 factions, each with its own magic, colours and names, plus lore
> like *dragons are extinct* and a medieval tech level. The same rules go into the prompt and into the checker."

### 3. A clean generation (30 s), tab **Generate**
Scenario **Normal brief**, then **Generate**.
> "Every stage of the pipeline runs and is shown here. The character is consistent and safe, and it's saved as *pending*."

### 4. The AI breaks rules, and the system repairs it (45 s) ⭐
Scenario **High creativity (AI breaks rules)**, then **Generate**. Scroll to *"What the AI got wrong"*.
> "At high creativity the AI makes the same mistakes real LLMs make: fire magic for an ice faction, a pistol in
> a medieval world, a living dragon, 'in the style of Studio Ghibli'. The checker caught every one, and auto-repair
> regenerated only the broken fields. The score went from about 20 to 100." Open the diff.

### 5. Guardrails (40 s)
- **Unsafe brief (graphic violence)**: blocked before it reaches the model.
- **Prompt injection attempt** ("ignore previous instructions..."): blocked.
- **Copycat name: Pikachoo**: flagged as 80% similar to Pikachu. The designer decides what to do.

### 6. Dialogue and story (30 s), tab **Dialogue & Story**
Generate dialogue for 2 situations and 3 story arcs.
> "Same character, different voices and branching arcs, all checked against lore."

### 7. Human control (40 s), tab **Designer Review**
Scroll to **Concept art** and pick a different variation.
> "The portrait is drawn from the character's validated data: faction scene, palette, class weapon, element
> aura. So the art can't contradict the Game Bible. The designer chooses, or uploads their own artwork."

Edit the catchphrase and **Save edit**. Show the version history (AI, AI repair, Designer) and the diff. Then **Approve**.
> "AI never has the final say. Every version is attributed and can be compared."

### 8. Cost (20 s), tab **Cost**
> "Every call is metered. Cheap models handle repairs and dialogue, repeats are cached for free, and there's a
> budget cap. That's about 10x cheaper than using the biggest model for everything."

### 9. Export (10 s), tab **Export**
Download the **PDF sheet**. It includes the provenance history.

---

**Likely questions**
- *Is it a real AI?* The default engine is a procedural generator, so it runs offline with no API key, and it
  deliberately makes LLM-style mistakes so the guardrails can be demonstrated reliably. The same pipeline runs
  on a real local LLM through Ollama with no code changes.
- *Can filters be bypassed?* Keyword filters can miss paraphrases. That's why there's a human review step,
  and the report proposes trained moderation models and embedding similarity as future work.
- *How do you know it works?* There are 8 automated tests, plus an evaluation over 240 generations (see the report).
