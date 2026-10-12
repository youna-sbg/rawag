import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.config import SlotType


class SlotCreate(BaseModel):
    type: SlotType
    date: dt.date
    start_time: dt.time


class SlotBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: SlotType
    type_name: str
    start_at: dt.datetime
    end_at: dt.datetime
    duration_minutes: int


class SlotOut(SlotBase):
    is_booked: bool


class BookingCreate(BaseModel):
    slot_id: int
    client_name: str = Field(min_length=2, max_length=100)
    client_phone: str = Field(min_length=7, max_length=20)
    note: str | None = Field(default=None, max_length=500)


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    client_phone: str
    note: str | None
    created_at: dt.datetime
    slot: SlotBase
