from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.database import engine
from app.models.score import Score
from app.schemas.user import UserCreate
from app.services.auth import create_user
from app.models.user import User
from app.services.session import set_session, get_session_user, clear_session
from app.services.hashing import pwd_context
from datetime import datetime, timedelta, date
import secrets
from app.services.email_sender import send_validation_email
from jinja2 import Template
from xhtml2pdf import pisa
from io import BytesIO
from pydantic import ValidationError
from app.services.email_sender import send_reset_email
from fastapi.staticfiles import StaticFiles



router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


"""@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return templates.TemplateResponse("landing.html", {"request": request})
    return templates.TemplateResponse("landing.html", {"request": request})"""

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        user_data = UserCreate(email=email, username=username, password=password)
        create_user(user_data)
        return RedirectResponse(url="/validate", status_code=303)
    except ValidationError as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": e.errors()[0]["msg"]  # affiche la première erreur proprement
        })
    except ValueError as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        })

@router.get("/validate", response_class=HTMLResponse)
async def validate_form(request: Request):
    return templates.TemplateResponse("validate.html", {"request": request})

@router.post("/validate")
async def validate_user(request: Request, email: str = Form(...), code: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        now = datetime.utcnow()

        if not user:
            error = "Adresse email inconnue."
        elif user.is_validated:
            error = "Ce compte est déjà activé."
        elif user.lockout_until and now < user.lockout_until:
            error = "Trop de tentatives. Réessayez plus tard."
        elif now - user.code_created_at > timedelta(minutes=15):
            error = "Ce code de validation a expiré."
        elif user.validation_code != code:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.lockout_until = now + timedelta(minutes=1)
            session.add(user)
            session.commit()
            error = "Code incorrect. Tentatives restantes : {}".format(
                max(0, 5 - user.failed_attempts)
            )
        else:
            user.is_validated = True
            user.failed_attempts = 0
            user.lockout_until = None
            session.add(user)
            session.commit()
            return RedirectResponse(url="/login", status_code=303)

        return templates.TemplateResponse("validate.html", {
            "request": request,
            "error": error
        })

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        valid_perm = pwd_context.verify(password, user.password_hash)
        valid_temp = (
                user.temp_password_hash and
                user.temp_password_expiration and
                datetime.utcnow() < user.temp_password_expiration and
                pwd_context.verify(password, user.temp_password_hash)
        )

        if not user or (not valid_perm and not valid_temp):
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Identifiants incorrects"
            })

        if valid_temp:
            response = RedirectResponse(url="/reset-password", status_code=303)
            set_session(response, user.id)
            return response

        if not user.is_validated:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Compte non validé par email"
            })
        response = RedirectResponse(url="/profil", status_code=303)
        set_session(response, user.id)
        return response

@router.get("/logout")
def logout_user():
    response = RedirectResponse(url="/", status_code=303)
    clear_session(response)
    return response

@router.get("/profil", response_class=HTMLResponse)
async def user_profil(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    with Session(engine) as session:
        user = session.get(User, user_id)
        best_score = session.exec(select(Score).where(Score.user_id == user_id)).first()
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "user": user,
            "email": user.email,
            "best_score": best_score.wpm if best_score else None
        })

@router.get("/resend-code", response_class=HTMLResponse)
async def resend_form(request: Request):
    return templates.TemplateResponse("resend_code.html", {"request": request})

@router.post("/resend-code")
async def resend_code(request: Request, email: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            error = "Aucun compte associé à cet email."
        elif user.is_validated:
            error = "Ce compte est déjà validé."
        else:
            new_code = secrets.token_hex(3)
            user.validation_code = new_code
            user.code_created_at = datetime.utcnow()
            user.failed_attempts = 0
            user.lockout_until = None
            session.add(user)
            session.commit()
            send_validation_email(user.email, new_code)
            return RedirectResponse(url="/validate", status_code=303)

        return templates.TemplateResponse("resend_code.html", {
            "request": request,
            "error": error
        })

@router.get("/certificat", response_class=HTMLResponse)
async def certificat_frontend(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    with Session(engine) as session:
        user = session.get(User, user_id)
        score = session.exec(select(Score).where(Score.user_id == user_id)).first()

    if not score:
        return HTMLResponse("<h3>Aucun score enregistré.</h3>")

    return templates.TemplateResponse("generator.html", {
        "request": request,
        "username": user.username,
        "email": user.email,
        "wpm": score.wpm,
        "date": datetime.today().strftime("%d/%m/%Y")
    })



@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_password(request: Request, email: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            return templates.TemplateResponse("forgot_password.html", {
                "request": request,
                "error": "Aucun compte associé à cet email."
            })

        # Génération du mot de passe temporaire
        temp_password = secrets.token_urlsafe(6)
        user.temp_password_hash = pwd_context.hash(temp_password)
        user.temp_password_expiration = datetime.utcnow() + timedelta(minutes=5)
        user.force_password_reset = True
        session.add(user)
        session.commit()

        send_reset_email(user.email, temp_password)
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": "Un mot de passe temporaire a été envoyé."
        })


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_form(request: Request):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user.force_password_reset:
            return RedirectResponse("/profil", status_code=303)

    return templates.TemplateResponse("reset_password.html", {"request": request})


@router.post("/reset-password")
async def reset_password(request: Request, password: str = Form(...), confirm: str = Form(...)):
    user_id = get_session_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    if password != confirm or len(password) < 6:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Les mots de passe ne correspondent pas ou sont trop courts."
        })

    with Session(engine) as session:
        user = session.get(User, user_id)
        user.password_hash = pwd_context.hash(password)
        user.temp_password_hash = None
        user.temp_password_expiration = None
        user.force_password_reset = False
        session.add(user)
        session.commit()

    return RedirectResponse("/profil", status_code=303)
