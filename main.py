import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import init_db
from .marketplace import router as marketplace_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus.nebula")

app = FastAPI(title="Nexus Nebula Universe API", version="1.0.0")

# CORS:
# - In production, set CORS_ALLOW_ORIGINS="https://your-frontend.example,https://another.example"
# - In dev, the default keeps local Next.js happy.
allowed = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed if o.strip()],
    # We don't use cookie-based auth in this starter, so credentials can stay off.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(marketplace_router)


@app.get("/health")
async def health():
    return {"ok": True, "service": "nexus-nebula-universe"}


@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Marketplace DB initialized")
