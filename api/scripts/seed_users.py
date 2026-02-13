"""Seed initial users into the database.

Usage:
    python -m api.scripts.seed_users
"""

import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.db.models import User
from api.services.auth_service import hash_password
from api.settings import settings

SEED_USERS = [
    {"username": "admin", "password": "admin", "role": "admin"},
    {"username": "staff", "password": "staff", "role": "staff"},
]


def seed(db: Session) -> None:
    for u in SEED_USERS:
        exists = db.query(User).filter(User.username == u["username"]).first()
        if exists:
            print(f"  skip {u['username']} (already exists)")
            continue
        user = User(
            id=uuid.uuid4(),
            username=u["username"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        print(f"  created {u['username']} ({u['role']})")
    db.commit()


def main() -> None:
    engine = create_engine(settings.database_url)
    with Session(engine) as db:
        print("Seeding users...")
        seed(db)
        print("Done.")


if __name__ == "__main__":
    main()
