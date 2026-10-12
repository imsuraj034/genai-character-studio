"""Print-friendly figures for the AAI case-study report (white background)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "report_assets"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})

NAVY, RED, GREEN, AMBER, GREY = "#1F3B73", "#B23A3A", "#2E7D4F", "#B7791F", "#555555"


def architecture():
    fig, ax = plt.subplots(figsize=(7.2, 8.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    def node(x, y, w, h, title, sub, col, fill="#FFFFFF"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    linewidth=1.6, edgecolor=col, facecolor=fill))
        ax.text(x, y + (0.14 if sub else 0), title, ha="center", va="center", fontsize=11.5, fontweight="bold",
                color="#111111")
        if sub:
            ax.text(x, y - 0.25, sub, ha="center", va="center", fontsize=9.2, color=GREY)

    def arrow(p1, p2, col="#333333", style="-", rad=0.0, label=None, lpos=None):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=13, color=col, linewidth=1.3,
                                     linestyle=style, connectionstyle=f"arc3,rad={rad}"))
        if label:
            ax.text(*lpos, label, fontsize=9, color=col, ha="center", va="center", style="italic")

    cx, w, h = 5.0, 3.6, 0.82
    steps = [("Designer Brief", "role, faction, class, personality, notes", NAVY, "#EEF2FA"),
             ("Input Guardrail", "content filter, prompt-injection, IP check", RED, "#FBEDED"),
             ("Cache, Budget & Model Routing", "reuse results, cap spend, pick tier", GREEN, "#EAF5EE"),
             ("Generator", "offline engine or local LLM (Ollama)", NAVY, "#EEF2FA"),
             ("Output Guardrail", "safety + copyright similarity", RED, "#FBEDED"),
             ("Consistency Checker", "rules R1-R7, score out of 100", NAVY, "#EEF2FA"),
             ("Human Designer Review", "approve / edit / reject / regenerate", GREEN, "#EAF5EE"),
             ("Export with Provenance", "JSON + PDF character sheet", NAVY, "#EEF2FA")]
    ys = [11.2 - i * 1.38 for i in range(len(steps))]
    for (t, s, c, f), y in zip(steps, ys):
        node(cx, y, w, h, t, s, c, f)
    for y1, y2 in zip(ys, ys[1:]):
        arrow((cx, y1 - h / 2), (cx, y2 + h / 2))

    # Game Bible (left) feeding generator + checker
    node(1.35, (ys[3] + ys[5]) / 2, 2.3, 1.25, "Game Bible", "rules, lore,\nfactions, banned terms", AMBER, "#FBF4E6")
    arrow((2.5, (ys[3] + ys[5]) / 2 + 0.3), (cx - w / 2, ys[3]), AMBER, "--")
    arrow((2.5, (ys[3] + ys[5]) / 2 - 0.3), (cx - w / 2, ys[5]), AMBER, "--")
    # Auto-repair loop (right)
    node(8.65, (ys[4] + ys[5]) / 2, 2.2, 1.1, "Auto-Repair", "regenerate only\nbroken fields", RED, "#FBEDED")
    arrow((cx + w / 2, ys[5]), (7.55, (ys[4] + ys[5]) / 2 - 0.3), RED, label="errors", lpos=(7.25, ys[5] - 0.05))
    arrow((7.55, (ys[4] + ys[5]) / 2 + 0.3), (cx + w / 2, ys[4]), RED, label="re-check", lpos=(7.3, ys[4] + 0.12))
    fig.tight_layout()
    fig.savefig(OUT / "fig_architecture.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def scores(rows):
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    x = range(len(rows))
    draft = [r["avg_draft_score"] for r in rows]
    final = [r["avg_final_score"] for r in rows]
    b1 = ax.bar([i - 0.19 for i in x], draft, 0.36, color="#C9824F", label="Raw AI draft (unguarded)")
    b2 = ax.bar([i + 0.19 for i in x], final, 0.36, color=NAVY, label="After consistency check + auto-repair")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{b.get_height():.0f}", ha="center",
                    fontsize=9.5)
    ax.set_xticks(list(x), [f"{r['temperature']}" for r in rows])
    ax.set_xlabel("Creativity (temperature)")
    ax.set_ylabel("Average consistency score (0-100)")
    ax.set_ylim(0, 112)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig_scores.png", dpi=220)
    plt.close(fig)


def cost(rows):
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    x = range(len(rows))
    big = [r["large_model_cost_per_char_usd"] for r in rows]
    ours = [r["cost_per_char_usd"] for r in rows]
    b1 = ax.bar([i - 0.19 for i in x], big, 0.36, color=RED, label="Largest model for every task")
    b2 = ax.bar([i + 0.19 for i in x], ours, 0.36, color=GREEN, label="Proposed routed pipeline")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.0012, f"${b.get_height():.3f}", ha="center",
                    fontsize=9)
    ax.set_xticks(list(x), [f"{r['temperature']}" for r in rows])
    ax.set_xlabel("Creativity (temperature)")
    ax.set_ylabel("Estimated cost per character (USD)")
    ax.set_ylim(0, max(big) * 1.22)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig_cost.png", dpi=220)
    plt.close(fig)


def build(rows):
    architecture()
    scores(rows)
    cost(rows)
