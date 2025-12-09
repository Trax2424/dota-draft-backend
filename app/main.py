from fastapi import FastAPI
from app.routers import draft

app = FastAPI(
    title="Dota Draft Engine",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(draft.router, prefix="/draft", tags=["draft"])
