import os
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum


class SlotType(str, Enum):
    PEAK = "peak"
    GROWTH = "growth"


@dataclass(frozen=True)
class SlotTypeConfig:
    name: str
    duration: timedelta

    @property
    def duration_minutes(self) -> int:
        return int(self.duration.total_seconds() // 60)


SLOT_TYPES = {
    SlotType.PEAK: SlotTypeConfig(name="اوج", duration=timedelta(minutes=45)),
    SlotType.GROWTH: SlotTypeConfig(name="رشد", duration=timedelta(minutes=25)),
}

DEFAULT_ADMIN_API_KEY = "change-me"

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", DEFAULT_ADMIN_API_KEY)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./booking.db")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
