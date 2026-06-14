from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Load .env before anything else
_load_dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_load_dotenv_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.deps import get_config
from app.models.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    get_config()
    yield


app = FastAPI(
    title="CazzKB",
    description="Personal knowledge base chat assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
