import typer
from rich import print
import httpx
import time
from typing import Optional

app = typer.Typer()
API = "http://localhost:8000"

@app.command()
def new():
    try:
        # Create a new random target
        response = httpx.post(f"{API}/targets/random")
        response.raise_for_status()  # Raise exception for 4xx/5xx responses
        trn = response.json()["trn"]
        
        # Create a new session
        response = httpx.post(f"{API}/sessions", json={"trn": trn})
        response.raise_for_status()
        sid = response.json()["session_id"]
        
        print(f"[green]Session {sid} – TRN {trn}[/]")
        
        # Collect impressions
        stage = 1
        while True:
            txt = typer.prompt("note (blank = finish)")
            if not txt:
                break
            
            # Add note to session
            response = httpx.post(f"{API}/sessions/{sid}/note", json={"text": txt, "stage": stage})
            response.raise_for_status()
            stage += 1
        
        # Finish session
        print("[yellow]Finishing session and scoring... (this may take a moment)[/]")
        response = httpx.post(f"{API}/sessions/{sid}/finish")
        response.raise_for_status()
        
        # Wait for scoring to complete (could add polling here)
        time.sleep(5)
        show(sid)
    except httpx.HTTPStatusError as e:
        print(f"[red]Error: API returned status code {e.response.status_code}[/]")
        if e.response.content:
            try:
                error_data = e.response.json()
                print(f"[red]Message: {error_data.get('detail', 'Unknown error')}[/]")
            except:
                print(f"[red]Response: {e.response.text}[/]")
    except httpx.RequestError as e:
        print(f"[red]Error: Could not connect to API server. Make sure the server is running at {API}[/]")
        print(f"[red]Detail: {str(e)}[/]")
    except Exception as e:
        print(f"[red]Unexpected error: {str(e)}[/]")

@app.command()
def show(session_id: int = typer.Argument(None)):
    sid = session_id
    if sid is None:
        sid = typer.prompt("Session ID", type=int)
    
    try:
        response = httpx.get(f"{API}/sessions/{sid}")
        response.raise_for_status()
        session = response.json()
        
        print(f"\n[bold green]Session {sid}[/]")
        
        if session.get("total_score"):
            print(f"[bold]Score: {session['total_score']:.1f}%[/]")
            print("\n[bold]Rubric:[/]")
            for k, v in session["rubric"].items():
                print(f"- {k}: {v:.1f}%")
        else:
            print("[yellow]This session has not been scored yet.[/]")
        
        print("\n[bold]Notes:[/]")
        print(session.get("user_notes", "No notes recorded"))
    except httpx.HTTPStatusError as e:
        print(f"[red]Error: API returned status code {e.response.status_code}[/]")
        if e.response.status_code == 404:
            print(f"[red]Session {sid} not found[/]")
        else:
            print(f"[red]Detail: {e.response.text}[/]")
    except httpx.RequestError as e:
        print(f"[red]Error: Could not connect to API server. Make sure the server is running at {API}[/]")
    except Exception as e:
        print(f"[red]Unexpected error: {str(e)}[/]")

if __name__ == "__main__":
    app() 