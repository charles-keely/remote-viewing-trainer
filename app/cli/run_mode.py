"""
Ultra-Explicit Guided "Run Mode"
• Explains each CRV stage (what + why + how long + example)
• Provides skip / help / cancel at every prompt
• Audible bell 5 s before timer ends
• Detailed debrief table + plain-English tip
"""

import asyncio, os, sys, time, json, httpx
from datetime import datetime
from rich.console   import Console
from rich.panel     import Panel
from rich.prompt    import Prompt
from rich.text      import Text
from rich.progress  import (
    Progress, SpinnerColumn, BarColumn, TimeRemainingColumn
)
from rich.table     import Table

# ── Configuration ───────────────────────────────────────────────────────
API_ROOT   = os.getenv("RV_API", "http://127.0.0.1:8000")
BELL       = "\a"   # terminal bell
console    = Console()
client     = httpx.AsyncClient()
PAD        = "  "

# ── Mini HTTP helpers ───────────────────────────────────────────────────
async def post(path, **kw): return (await client.post(f"{API_ROOT}{path}", **kw)).json()
async def get (path, **kw): return (await client.get (f"{API_ROOT}{path}", **kw)).json()

# ── UI helpers ──────────────────────────────────────────────────────────
def ring(): console.print(BELL, end="", soft_wrap=True)

def show_panel(title:str, body:str, footer:str=""):
    """Pretty wrapper around rich.Panel"""
    console.print(Panel(body + ("\n"+footer if footer else ""),
                         title=title, padding=(1,2)))

async def ask_user(question:str, allow_blank:bool=False) -> str:
    """Prompt → return trimmed input (handles blank & cancel)"""
    while True:
        ans = Prompt.ask(f"[bold cyan]{question}[/]")
        if ans.lower() == "cancel":
            console.print("[red]Session cancelled by user.[/]")
            sys.exit(0)
        if ans.lower() == "help":
            console.print("[yellow]Type your immediate impressions; "
                          "short words are best. 'skip' jumps ahead.[/]")
            continue
        if ans.strip() or allow_blank:
            return ans.strip()

def countdown(seconds:int):
    """Visual timer with 5-sec warning bell"""
    with Progress(
        SpinnerColumn(),
        BarColumn(bar_width=24),
        TimeRemainingColumn(compact=True),
        console=console,
        transient=True,
    ) as prog:
        task = prog.add_task("", total=seconds)
        for remaining in range(seconds, 0, -1):
            prog.update(task, advance=1)
            if remaining == 5: ring()
            time.sleep(1)

# ── Main orchestrator ───────────────────────────────────────────────────
def run_mode():
    asyncio.run(_run_async())

async def _run_async():
    console.clear()

    # Splash
    show_panel(
        "Controlled Remote Viewing – Guided Session",
        f"{PAD}• You will complete **6 short stages** (≈5 min total)\n"
        f"{PAD}• Have pen & paper ready for sketches/notes\n"
        f"{PAD}• During any prompt you may type:\n"
        f"{PAD}   skip   → jump to next stage\n"
        f"{PAD}   help   → brief stage tip\n"
        f"{PAD}   cancel → abort & save progress",
        "Press ↵ Enter to begin")
    input()

    # Resume or create session
    unfinished = await get("/sessions?status=unfinished")
    if unfinished:
        s   = unfinished[0]
        sid = s["session_id"]; trn = s["target_id"]
        console.print(f"[yellow]Resuming paused session {sid} (TRN {trn})[/]\n")
    else:
        trn = (await post("/targets/random"))["trn"]
        sid = (await post("/sessions", json={"trn": trn}))["session_id"]
        console.print(f"New session [bold]{sid}[/] created  •  TRN {trn}\n")

    # Stage definitions
    stages = [
        ("Stage 1 – Ideogram",      15,
         "On PAPER draw a ½-second spontaneous squiggle.\n"
         "Immediately TYPE **1–3 feeling/motion words** (no nouns).",
         "Example →   flowing   sharp"),
        ("Stage 2 – Sensory",       60,
         "List raw sensory adjectives. Think texture / temperature / smell / sound / colour.\n"
         "Separate with commas, no sentences.",
         "Example →   gritty, cold, metallic, humming"),
        ("Stage 3 – Dimensional",   60,
         "Describe MAJOR SHAPES & DIRECTIONS. Avoid object names.",
         "Example →   tall vertical plane, arch-shaped curve"),
        ("Stage 4 – Functional / Ambience", 45,
         "Note generic function or atmosphere (avoid guessing the site).",
         "Example →   gathering place, energy flow"),
    ]

    # Run stages
    for idx,(title,seconds,desc,example) in enumerate(stages, start=1):
        show_panel(title, f"{desc}\n\n[dim]{example}",
                   footer="Type your words, ↵ to submit  •  'skip' to skip")
        answer = await ask_user("Your entry", allow_blank=True)
        await post(f"/sessions/{sid}/note", json={"stage": idx, "text": answer})
        if answer.lower() != "skip": countdown(seconds)

    # Probes (yes/no/unsure)
    show_panel("Stage 5 – Targeted Probes",
               "Answer quickly:  y = yes   n = no   u = unsure")
    probe_qs = [
        "Is the dominant environment INDOORS?",
        "Is WATER a key element?",
        "Is primary movement VERTICAL?"
    ]
    for i,q in enumerate(probe_qs, 1):
        a = Prompt.ask(f"{q}", choices=["y","n","u"], default="u")
        await post(f"/sessions/{sid}/note",
                   json={"stage": 5, "text": f"{q} → {a}"})

    # Summary
    show_panel("Stage 6 – Summary",
               "In ONE or TWO sentences, combine your strongest impressions.\n"
               "Optional: paste sketch file path (or blank to skip).")
    summary = await ask_user("Summary (blank = none)", allow_blank=True)
    await post(f"/sessions/{sid}/note",
               json={"stage": 6, "text": summary})

    # Lock & score
    console.print("\n[bold]Locking notes and contacting GPT-Vision…[/]")
    await post(f"/sessions/{sid}/finish")
    with Progress(SpinnerColumn(),
                  "[progress.description]{task.description}",
                  console=console, transient=True) as prog:
        t = prog.add_task("Scoring", start=False)
        while True:
            ses = await get(f"/sessions/{sid}")
            if ses["total_score"] > 0:
                break
            prog.start_task(t); time.sleep(1)

    # Debrief
    rubric = ses["rubric"]; total = ses["total_score"]
    table  = Table(title="📝  Accuracy Breakdown", show_header=True,
                   header_style="bold magenta")
    table.add_column("Category"); table.add_column("Score /3", justify="right")
    for k,v in rubric.items(): table.add_row(k.capitalize(), f"{v}")
    console.print(table)
    console.print(f"[bold green]Overall Accuracy →  {total:.2f}  /  3[/]\n")

    # Simple advice
    advice = (
        "Great sensory detail!  Next time linger on colours before "
        "moving to functions." if rubric["sensory"]>=2 else
        "Try pausing longer in Stage-2; literal adjectives beat guesses."
    )
    console.print(f"[blue]Coach Tip:[/] {advice}")

    console.print("\nSession complete – press ↵ to exit to shell.")
    input()

# allow `python -m app.cli.run_mode` direct run
if __name__ == "__main__":
    run_mode() 