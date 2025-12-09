from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .config import settings

# --- DB URL (works for Railway & local) ---
DATABASE_URL = getattr(settings, "DATABASE_URL", None) or getattr(
    settings, "database_url", None
)

if not DATABASE_URL:
    # Fallback for local dev if nothing is set yet
    DATABASE_URL = "sqlite:///./dev.db"

# SQLite needs this extra arg, Postgres does not
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---------- MODELS ----------
class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    primary_role = Column(String, index=True, nullable=True)
    roles = Column(String, nullable=True)  # comma-separated roles
    win_rate = Column(Float, nullable=True)
    pick_rate = Column(Float, nullable=True)


# ---------- HELPERS ----------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def seed_heroes() -> None:
    """Insert a small set of heroes if the table is empty."""
    db = SessionLocal()
    try:
        count = db.query(Hero).count()
        if count > 0:
            return  # already seeded

        heroes_seed = [
            Hero(
                id=1,
                name="Anti-Mage",
                primary_role="Carry",
                roles="Carry,Escape,Nuker",
                win_rate=0.51,
                pick_rate=0.18,
            ),
            Hero(
                id=2,
                name="Axe",
                primary_role="Initiator",
                roles="Initiator,Durable,Disabler",
                win_rate=0.50,
                pick_rate=0.22,
            ),
            Hero(
                id=3,
                name="Juggernaut",
                primary_role="Carry",
                roles="Carry,Pusher,Escape",
                win_rate=0.56,  # meta strong
                pick_rate=0.24,
            ),
            Hero(
                id=4,
                name="Slark",
                primary_role="Carry",
                roles="Carry,Escape,Disabler",
                win_rate=0.44,  # meta weak
                pick_rate=0.15,
            ),
        ]

        db.add_all(heroes_seed)
        db.commit()
    finally:
        db.close()
