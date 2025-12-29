"""Authentication utilities (DEMO STUB).

For production:
- Replace this with JWT/OAuth2 validation.
- Load users from DB.
- Never trust a header as identity.
"""

from fastapi import HTTPException, Header
from .marketplace_models import User


async def get_current_user(authorization: str = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Demo user. Replace with real auth + DB lookup.
    return User(
        id="user-demo-123",
        username="demo_user",
        email="demo@nebula.ai",
        wallet_balance=1000.0,
    )
