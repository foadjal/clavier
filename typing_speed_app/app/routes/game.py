from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.session import get_session_user
from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.models.score import Score
from datetime import datetime


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/test", response_class=HTMLResponse)
async def typing_test(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("test.html", {"request": request})



from fastapi import HTTPException
from app.services.words import get_random_words  # ← à ajouter en haut avec les imports

@router.get("/api/words")
async def get_words():
    try:
        words = await get_random_words()
        return {"words": words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def submit_test(request: Request, typed: str = Form(...), original: str = Form(...), time: float = Form(...)):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    typed = typed.strip()
    original = original.strip()

    # Comparaison caractère par caractère
    correct_chars = 0
    total_chars = len(typed)
    for i in range(min(len(typed), len(original))):
        if typed[i] == original[i]:
            correct_chars += 1

    mistakes = total_chars - correct_chars
    effective_chars = max(0, correct_chars - mistakes)
    minutes = time / 60
    wpm = round((effective_chars / 5) / minutes, 2)
    accuracy = round((correct_chars / total_chars) * 100, 2) if total_chars > 0 else 0.0

    with Session(engine) as session:
        existing = session.exec(select(Score).where(Score.user_id == user_id)).first()
        if not existing or wpm > existing.wpm:
            if existing:
                session.delete(existing)
                session.commit()
            session.add(Score(user_id=user_id, wpm=wpm))
            session.commit()

    return templates.TemplateResponse("result.html", {"request": request, "wpm": wpm, "accuracy": accuracy})


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse("/profil", status_code=303)
