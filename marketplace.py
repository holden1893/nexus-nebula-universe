"""NEXUS NEBULA MARKETPLACE API (minimal).

Endpoints:
- GET  /api/marketplace/listings
- GET  /api/marketplace/listings/{id}
- POST /api/marketplace/listings
- PATCH /api/marketplace/listings/{id}/publish
- GET  /api/marketplace/stats
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .marketplace_models import User, Listing, Transaction, ListingStatus
from .database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])
PLATFORM_FEE_PERCENT = 0.20


def clean_sa(obj):
    """Convert a SQLAlchemy model into a JSON-safe dict."""
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


class ListingCreate(BaseModel):
    project_id: str
    title: str = Field(..., min_length=10, max_length=100)
    description: str = Field(..., min_length=50)
    price: float = Field(..., ge=0.99)
    license_type: str
    tags: List[str] = []
    category: str


@router.get("/listings")
async def browse_listings(
    category: Optional[str] = None,
    sort_by: str = "popular",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Listing).where(Listing.status == ListingStatus.ACTIVE.value)

    if category:
        query = query.where(Listing.category == category)

    if sort_by == "popular":
        query = query.order_by(Listing.current_sales.desc())
    elif sort_by == "recent":
        query = query.order_by(Listing.published_at.desc())
    elif sort_by == "rating":
        query = query.order_by(Listing.rating.desc())

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    listings = result.scalars().all()

    return {"listings": [clean_sa(l) for l in listings], "page": page}


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Not found")

    listing.views += 1
    await db.commit()

    return clean_sa(listing)


@router.post("/listings")
async def create_listing(
    data: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    listing = Listing(
        id=f"lst-{uuid.uuid4().hex[:12]}",
        project_id=data.project_id,
        seller_id=current_user.id,
        title=data.title,
        description=data.description,
        price=data.price,
        license_type=data.license_type,
        tags=data.tags,
        category=data.category,
        status=ListingStatus.DRAFT.value,
    )

    db.add(listing)
    await db.commit()
    return {"listing_id": listing.id, "status": "created"}


@router.patch("/listings/{listing_id}/publish")
async def publish_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Not found")

    if listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    listing.status = ListingStatus.ACTIVE.value
    listing.published_at = datetime.utcnow()
    await db.commit()

    return {"status": "published", "listing_id": listing_id}


@router.get("/stats")
async def marketplace_stats(db: AsyncSession = Depends(get_db)):
    total_listings = await db.scalar(
        select(func.count(Listing.id)).where(Listing.status == ListingStatus.ACTIVE.value)
    )
    total_sales = await db.scalar(select(func.count(Transaction.id)))
    total_volume = await db.scalar(select(func.sum(Transaction.amount))) or 0.0

    return {
        "total_listings": int(total_listings or 0),
        "total_sales": int(total_sales or 0),
        "total_volume": float(total_volume),
    }
