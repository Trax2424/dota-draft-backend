from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import Hero, get_db

router = APIRouter(prefix="/heroes", tags=["heroes"])


# ---------- SCHEMAS ----------
class HeroOut(dict):
    """Simple serializer so we don't need Pydantic models yet."""

    @classmethod
    def from_model(cls, hero: Hero) -> "HeroOut":
        return cls(
            id=hero.id,
            name=hero.name,
            primary_role=hero.primary_role,
            roles=hero.roles,
            win_rate=hero.win_rate,
            pick_rate=hero.pick_rate,
        )


# ---------- ENDPOINTS ----------
@router.get("/", response_model=List[dict])
def list_heroes(db: Session = Depends(get_db)):
    heroes = db.query(Hero).order_by(Hero.name).all()
    return [HeroOut.from_model(h) for h in heroes]


@router.get("/{hero_id}", response_model=dict)
def get_hero(hero_id: int, db: Session = Depends(get_db)):
    hero = db.query(Hero).filter(Hero.id == hero_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return HeroOut.from_model(hero)


@router.get("/roles/{role}", response_model=List[dict])
def heroes_by_role(role: str, db: Session = Depends(get_db)):
    # simple case-insensitive search inside the comma-separated roles string
    pattern = role.lower()
    heroes = db.query(Hero).all()
    filtered = [
        h for h in heroes if h.roles and pattern in h.roles.lower()
    ]
    return [HeroOut.from_model(h) for h in filtered]
