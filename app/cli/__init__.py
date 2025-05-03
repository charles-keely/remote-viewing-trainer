"""
rv – top-level CLI launcher
--------------------------------------------------
• `rv` or `rv run`  →  guided CRV session
• `rv help`         →  one-page quick help
• `rv voice`        →  voice-guided CRV session
(advanced users can still call hidden FastAPI or Typer
 commands; we expose only the friendly entry here.)
"""
import typer, importlib
from .run_mode import run_mode
from .run_mode_voice import voice_run

app = typer.Typer(add_completion=False, rich_help_panel="Main Commands")

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """
    Called when user types bare `rv` (no sub-command).
    We immediately start the guided run mode.
    """
    if ctx.invoked_subcommand is None:
        run_mode()

@app.command()
def run():
    """Start a brand-new or resume a paused CRV session."""
    run_mode()

@app.command()
def voice():
    """Start a voice-guided CRV session using OpenAI TTS and Whisper."""
    import asyncio
    asyncio.run(voice_run())

@app.command()
def help():
    """Print a concise cheat-sheet without opening docs."""
    print(
        "─────────  RV CLI Cheat-Sheet  ─────────\n"
        "rv           : start / resume session (same as rv run)\n"
        "rv voice     : start voice-guided session\n"
        "make run     : alias for rv (convenience)\n"
        "make vrun    : alias for rv voice\n"
        "make dev     : start FastAPI backend\n"
        "Commands during prompts:\n"
        "  skip   → jump to next stage\n"
        "  help   → show stage tip\n"
        "  cancel → abort & save progress\n"
        "Keys: ↵ = continue   •   y/n/u = yes/no/unsure\n"
        "────────────────────────────────────────"
    ) 