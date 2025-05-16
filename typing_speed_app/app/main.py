from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import auth, game, home
from app.database import init_db

app = FastAPI()

# ⚠️ Monter les fichiers statiques AVANT le reste
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Import des routes
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(game.router)



@app.on_event("startup")
def on_startup():
    init_db()
