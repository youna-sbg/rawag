import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config, models  # noqa: F401  (models must be imported before create_all)
from app.database import Base, engine
from app.routers import bookings, slots

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    if config.ADMIN_API_KEY == config.DEFAULT_ADMIN_API_KEY:
        logger.warning("ADMIN_API_KEY is not set, falling back to the insecure default key")
    yield


app = FastAPI(title="Consultation Booking API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(slots.router)
app.include_router(bookings.router)
