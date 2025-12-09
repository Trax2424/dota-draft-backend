from fastapi import APIRouter

router = APIRouter()

@router.get("/suggest-picks")
def suggest_picks_placeholder():
    # We'll replace this with the real draft engine later
    return {"message": "Draft engine coming soon"}
