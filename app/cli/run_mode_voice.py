import asyncio, os, time, json, httpx
from rich.console import Console
from app.services.voice import speak, listen
from app.cli.run_mode import countdown     # reuse timer helper
API = os.getenv("RV_API", "http://127.0.0.1:8000")
console = Console()
client  = httpx.AsyncClient()

async def post(path, **k): return (await client.post(f"{API}{path}", **k)).json()
async def get (path, **k): return (await client.get (f"{API}{path}", **k)).json()

async def voice_run():
    # Introduction with detailed explanation
    await speak(
        "Welcome to the Controlled Remote Viewing guided session. "
        "Controlled Remote Viewing is a structured protocol developed to perceive and describe distant or unseen targets. "
        "I'll guide you through six distinct stages, each designed to access different types of information about the target. "
        "The entire session will take about fifteen minutes. "
        "Have pen and paper ready for sketches and notes. "
        "You can say 'skip' to move to the next stage, 'help' for guidance, or 'cancel' to end the session. "
        "Let's begin when you're ready and settled. Take a deep breath."
    )
    
    # Pause to allow user to prepare
    await asyncio.sleep(3)
    
    # Generate new target and create session
    trn = (await post("/targets/random"))["trn"]
    sid = (await post("/sessions", json={"trn": trn}))["session_id"]
    console.print(f"Voice session {sid} • TRN {trn}")
    
    await speak(
        "A random target has been selected. "
        "Remember, your task is to perceive information about this target without knowing what it is. "
        "Trust your initial impressions and avoid analytical thinking during the process."
    )
    
    # Stage definitions with detailed instructions
    stages = [
        # Stage 1: Ideogram
        (
            "Stage One: Ideogram. "
            "The ideogram is your hand's spontaneous reaction to the target's signal. "
            "Take your pen and make a quick, half-second mark on paper—a spontaneous squiggle without thinking. "
            "This is not a drawing but a reflexive response. "
            "Now, describe the feeling or motion qualities of your ideogram using one to three simple words. "
            "Focus on how it felt to make the mark—was it flowing, jagged, smooth, sharp, or heavy? "
            "Avoid naming objects. Simply describe the motion or feeling. "
            "Please speak your response now.",
            15, 1
        ),
        
        # Stage 2: Sensory
        (
            "Stage Two: Sensory impressions. "
            "Now move to pure sensory data about the target. "
            "What basic sensations are you perceiving? "
            "Focus on textures, temperatures, sounds, smells, colors, or tastes. "
            "List these as simple adjectives separated by pauses—cold, rough, blue, humming. "
            "Stay with raw sensory data only—no objects or interpretations. "
            "These impressions may seem random but are important building blocks. "
            "Take a moment to perceive, then speak the sensory impressions as they come to you.",
            60, 2
        ),
        
        # Stage 3: Dimensional
        (
            "Stage Three: Dimensional aspects. "
            "In this stage, focus on the dimensions, shapes, and spatial relationships at the target. "
            "Describe the major forms, angles, and how they're arranged. "
            "Is the target primarily vertical, horizontal, or curved? "
            "Are there tall structures, flat surfaces, or rounded elements? "
            "Avoid naming specific objects—instead say 'tall vertical structure' rather than 'building'. "
            "Dimensional data tells us about the physical structure and layout. "
            "Speak these dimensional aspects as they come to mind.",
            60, 3
        ),
        
        # Stage 4: Functional/Ambience
        (
            "Stage Four: Functional or ambience impressions. "
            "Now consider what happens at this target—its purpose or feeling. "
            "What is this place or thing for? What energy or atmosphere exists there? "
            "Use general descriptions like 'gathering place', 'storage', 'movement', or 'transition'. "
            "Note emotional impressions—does it feel sacred, industrial, natural, or human-made? "
            "Again, avoid specific naming or guessing what the target is. "
            "The function and ambience give context to your earlier impressions. "
            "Please describe these functional aspects now.",
            45, 4
        ),
    ]

    # Run through each stage with improved interaction
    for prompt, secs, num in stages:
        await speak(prompt)
        
        # Listen for response with commands handling
        txt = (await listen(seconds=secs+10)).lower()
        
        # Handle commands
        if "cancel" in txt:
            await speak("Session cancelled. Your progress has been saved. Thank you for participating.")
            return
        elif "help" in txt:
            if num == 1:
                help_text = "For the ideogram, just make a quick mark and describe how it felt to make it—flowing, sharp, curved, etc."
            elif num == 2:
                help_text = "Focus on pure sensations like colors, textures, sounds, temperatures. Avoid naming things."
            elif num == 3:
                help_text = "Describe shapes and their arrangements without naming what they are—vertical structures, horizontal planes, etc."
            elif num == 4:
                help_text = "Focus on what happens here or how it feels—a place of movement, storage, connection, etc."
            
            await speak(help_text)
            txt = (await listen(seconds=secs)).lower()
            if "cancel" in txt:
                await speak("Session cancelled. Your progress has been saved. Thank you for participating.")
                return
        
        # Save the response
        await post(f"/sessions/{sid}/note", json={"stage":num, "text":txt})
        
        # Countdown timer if not skipped
        if "skip" not in txt: 
            await speak(f"Taking time to deepen your impressions. {secs} seconds remaining in this stage.")
            countdown(secs)
        else:
            await speak("Moving to the next stage.")

    # Stage 5: Probes with better explanation
    await speak(
        "Stage Five: Targeted probes. "
        "I'll ask you three specific questions about the target. "
        "Answer quickly with 'yes', 'no', or 'unsure'. "
        "These probes help focus on specific aspects of the target. "
        "Trust your intuitive response without analyzing."
    )
    
    probes = [
        "Is the dominant environment indoors?",
        "Is water a key element at this target?",
        "Is vertical movement or structure significant at this target?"
    ]
    
    for q in probes:
        await speak(q)
        ans = (await listen(seconds=8)).lower()
        
        # Simplify response to yes/no/unsure
        if "yes" in ans or "yeah" in ans:
            simplified = "yes"
        elif "no" in ans or "nope" in ans:
            simplified = "no"
        else:
            simplified = "unsure"
            
        await post(f"/sessions/{sid}/note", json={"stage":5, "text":f"{q} → {simplified}"})
        await speak(f"Recorded: {simplified}")

    # Stage 6: Summary with better guidance
    await speak(
        "Stage Six: Summary. "
        "This is your opportunity to bring together all your impressions. "
        "What stands out most strongly from your session? "
        "Synthesize your key impressions from all stages into one or two sentences. "
        "This summary helps consolidate your perceptions of the target. "
        "Take a moment to review your notes if needed, then provide your summary."
    )
    
    summary = await listen(seconds=90)
    await post(f"/sessions/{sid}/note", json={"stage":6, "text":summary})

    # Scoring process with explanation
    await speak(
        "Thank you for completing your remote viewing session. "
        "I'm now sending your impressions for analysis and scoring against the actual target. "
        "This process uses advanced AI to evaluate the accuracy of your perceptions. "
        "Please wait a moment while this analysis is completed."
    )
    
    await post(f"/sessions/{sid}/finish")
    while True:
        ses = await get(f"/sessions/{sid}")
        if ses["total_score"]>0: break
        time.sleep(1)

    # Detailed feedback
    total_score = ses["total_score"]
    score_percentage = min(round(total_score * 33.3, 1), 100)
    
    # Feedback based on score range
    if score_percentage > 70:
        assessment = "excellent"
    elif score_percentage > 50:
        assessment = "good"
    elif score_percentage > 30:
        assessment = "promising"
    else:
        assessment = "developing"
    
    await speak(
        f"Your session scoring is complete. Your overall accuracy was {score_percentage:.1f} percent, "
        f"which is {assessment} for remote viewing. "
        f"The detailed breakdown of your score in different categories "
        f"is displayed in the terminal. "
        f"Remember, remote viewing is a skill that improves with practice. "
        f"Each session builds your abilities, regardless of the score. "
        f"Thank you for completing this remote viewing exercise."
    )
    
    # Print detailed results to terminal
    console.print("\n")
    console.print("=" * 50)
    console.print(f"SESSION RESULTS: #{sid} - Target {trn}")
    console.print("=" * 50)
    console.print(f"Overall Accuracy: {score_percentage:.1f}%")
    console.print("\nCategory Scores:")
    for category, score in ses["rubric"].items():
        cat_percent = min(round(score * 33.3, 1), 100)
        console.print(f"- {category.capitalize()}: {cat_percent:.1f}%")
    console.print("\nYour Notes:")
    console.print(ses["user_notes"])
    console.print("=" * 50)

if __name__ == "__main__":
    asyncio.run(voice_run()) 