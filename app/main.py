from fastapi import FastAPI

from .db import init_db, seed_heroes
from .routers import draft, heroes

app = FastAPI(title="Dota Draft Backend")


@app.on_event("startup")
def on_startup():
    # Make sure DB is ready and has heroes
    init_db()
    seed_heroes()


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers
app.include_router(heroes.router)
app.include_router(draft.router)
