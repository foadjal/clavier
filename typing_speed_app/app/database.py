from sqlmodel import SQLModel, create_engine
from app.models.score import Score

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from app.models.user import User
    SQLModel.metadata.create_all(engine)
