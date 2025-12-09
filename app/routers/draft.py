from typing import Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import Hero, get_db

router = APIRouter(prefix="/draft", tags=["draft"])

Team = Literal["radiant", "dire"]


class DraftState:
    def __init__(self, draft_id: str):
        self.id = draft_id
        self.radiant: List[int] = []
        self.dire: List[int] = []
        self.completed: bool = False


# In-memory storage for now. Later we can move to DB/Redis if needed.
DRAFTS: Dict[str, DraftState] = {}


def _get_draft_or_404(draft_id: str) -> DraftState:
    draft = DRAFTS.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


# ---------- ENDPOINTS ----------
@router.post("/start")
def start_draft():
    draft_id = str(uuid4())
    DRAFTS[draft_id] = DraftState(draft_id)
    return {"draft_id": draft_id, "radiant": [], "dire": [], "completed": False}


@router.post("/pick")
def pick_hero(
    draft_id: str,
    team: Team,
    hero_id: int,
    db: Session = Depends(get_db),
):
    draft = _get_draft_or_404(draft_id)

    # Ensure hero exists
    hero = db.query(Hero).filter(Hero.id == hero_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    # Ensure not already picked
    if hero_id in draft.radiant or hero_id in draft.dire:
        raise HTTPException(status_code=400, detail="Hero already picked")

    target_list = draft.radiant if team == "radiant" else draft.dire
    target_list.append(hero_id)

    # For now we mark draft complete when each team has 5 heroes
    if len(draft.radiant) >= 5 and len(draft.dire) >= 5:
        draft.completed = True

    return {
        "draft_id": draft.id,
        "radiant": draft.radiant,
        "dire": draft.dire,
        "completed": draft.completed,
    }


@router.get("/state")
def get_state(draft_id: str):
    draft = _get_draft_or_404(draft_id)
    return {
        "draft_id": draft.id,
        "radiant": draft.radiant,
        "dire": draft.dire,
        "completed": draft.completed,
    }


@router.get("/suggest")
def suggest_pick(
    draft_id: str,
    team: Team,
    db: Session = Depends(get_db),
):
    """
    SUPER SIMPLE META-AWARE SUGGESTION:
    - Look at all heroes not yet picked.
    - Sort by win_rate (meta strength).
    - Return the best available hero for that team.
    Later we plug in our full formula with OpenDota data.
    """
    draft = _get_draft_or_404(draft_id)

    picked_ids = set(draft.radiant + draft.dire)
    all_heroes = db.query(Hero).all()
    available = [h for h in all_heroes if h.id not in picked_ids]

    if not available:
        raise HTTPException(status_code=400, detail="No heroes left to suggest")

    best = max(available, key=lambda h: (h.win_rate or 0.0))

    return {
        "draft_id": draft.id,
        "team": team,
        "suggested_hero": {
            "id": best.id,
            "name": best.name,
            "primary_role": best.primary_role,
            "roles": best.roles,
            "win_rate": best.win_rate,
            "pick_rate": best.pick_rate,
        },
    }
