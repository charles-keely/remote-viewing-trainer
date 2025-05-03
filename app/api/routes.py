from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update, text
from app.db.session import get_db_session
from app.services.targets import create_target
from app.services.ai import describe_image
from app.services.score import score
from app.models.session import Session as SessionModel
from app.models.target import Target
import threading
import time

router = APIRouter()

@router.get("/health") 
def health(): 
    return {"status":"ok"}

@router.post("/targets/random") 
def new_target(): 
    return {"trn": create_target()}

@router.post("/sessions")
def new_session(p: dict, db: Session = Depends(get_db_session)):
    trn = p["trn"]
    result = db.execute(text(
         "INSERT INTO sessions(target_id,user_notes,stage_durations,rubric,total_score,aols)"
         f" VALUES('{trn}','','{{}}','{{}}',0,'[]') RETURNING session_id"))
    sid = result.scalar_one()
    return {"session_id": sid}

@router.get("/sessions")
def list_sessions(status: str = None, db: Session = Depends(get_db_session)):
    """List sessions, optionally filtering by status"""
    query = select(SessionModel)
    if status == "unfinished":
        # Return sessions with a score of 0 (not yet scored/finished)
        query = query.where(SessionModel.total_score == 0)
    sessions = db.execute(query).scalars().all()
    return [s.__dict__ for s in sessions]

@router.post("/sessions/{sid}/note")
def add_note(sid: int, p: dict, db: Session = Depends(get_db_session)):
    db.execute(update(SessionModel).where(SessionModel.session_id==sid)
        .values(user_notes=SessionModel.user_notes+f"\n[Stage {p['stage']}] {p['text']}"))
    return {"ok": True}

@router.post("/sessions/{sid}/finish")
def finish(sid: int, bg: BackgroundTasks, db: Session = Depends(get_db_session)):
    def _work():
        from app.db.session import SessionLocal
        db_session = SessionLocal()
        try:
            ses = db_session.execute(select(SessionModel).where(SessionModel.session_id==sid)).scalar_one()
            tgt = db_session.execute(select(Target).where(Target.target_id==ses.target_id)).scalar_one()
            desc = describe_image(tgt.image_url)
            res = score(ses.user_notes, desc)
            db_session.execute(update(Target).where(Target.target_id==tgt.target_id).values(caption=desc))
            db_session.execute(update(SessionModel).where(SessionModel.session_id==sid)
                        .values(rubric=res["rubric"], total_score=res["total"]))
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error in background task: {e}")
        finally:
            db_session.close()
    
    bg.add_task(_work)
    return {"status": "scoring"}

@router.get("/sessions/{sid}")
def get_session(sid: int, db: Session = Depends(get_db_session)):
    ses = db.execute(select(SessionModel).where(SessionModel.session_id==sid)).scalar_one_or_none()
    if not ses: 
        raise HTTPException(404)
    return ses.__dict__ 