from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserCreate
from app.database import engine
from app.services.email_sender import send_validation_email
from app.services.hashing import hash_password
import secrets

from datetime import datetime, timedelta


def create_user(user_data: UserCreate):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()

        if existing_user:
            # Cas 1 : compte déjà validé → refuse
            if existing_user.is_validated:
                raise ValueError("Cet email est déjà utilisé.")

            # Cas 2 : compte pas encore validé + code expiré → supprime et remplace
            if datetime.utcnow() - existing_user.code_created_at > timedelta(minutes=1):
                session.delete(existing_user)
                session.commit()
            else:
                raise ValueError("Un code d’activation a déjà été envoyé. Patientez ou validez-le.")

        # Nouveau compte
        validation_code = secrets.token_hex(3)
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            validation_code=validation_code,
            code_created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        send_validation_email(user.email, validation_code)
        return user
