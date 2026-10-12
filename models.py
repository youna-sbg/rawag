from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import SLOT_TYPES, SlotType
from app.database import Base


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[SlotType] = mapped_column(Enum(SlotType))
    start_at: Mapped[datetime] = mapped_column(index=True)
    end_at: Mapped[datetime]

    booking: Mapped["Booking | None"] = relationship(
        back_populates="slot", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def type_name(self) -> str:
        return SLOT_TYPES[self.type].name

    @property
    def duration_minutes(self) -> int:
        return SLOT_TYPES[self.type].duration_minutes

    @property
    def is_booked(self) -> bool:
        return self.booking is not None


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique: a slot can only ever have one booking
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"), unique=True)
    client_name: Mapped[str] = mapped_column(String(100))
    client_phone: Mapped[str] = mapped_column(String(20))
    note: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    slot: Mapped[Slot] = relationship(back_populates="booking")
