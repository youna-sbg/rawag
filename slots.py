import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import SLOT_TYPES, SlotType
from app.deps import get_db, require_admin
from app.models import Slot
from app.schemas import SlotCreate, SlotOut

router = APIRouter()


@router.get("/slot-types")
def list_slot_types():
    return [
        {"key": key.value, "name": cfg.name, "duration_minutes": cfg.duration_minutes}
        for key, cfg in SLOT_TYPES.items()
    ]


@router.get("/slots", response_model=list[SlotOut])
def list_slots(
    day: dt.date | None = None,
    slot_type: SlotType | None = Query(None, alias="type"),
    only_available: bool = True,
    db: Session = Depends(get_db),
):
    query = select(Slot).options(selectinload(Slot.booking)).order_by(Slot.start_at)

    if day:
        day_start = dt.datetime.combine(day, dt.time.min)
        query = query.where(Slot.start_at >= day_start, Slot.start_at < day_start + dt.timedelta(days=1))
    else:
        query = query.where(Slot.start_at >= dt.datetime.now())

    if slot_type:
        query = query.where(Slot.type == slot_type)
    if only_available:
        query = query.where(~Slot.booking.has())

    return db.scalars(query).all()


@router.post("/slots", response_model=SlotOut, status_code=201, dependencies=[Depends(require_admin)])
def create_slot(payload: SlotCreate, db: Session = Depends(get_db)):
    # clients may send a timezone or seconds (e.g. "10:00:00Z"); slots are stored as naive local times
    start_time = payload.start_time.replace(tzinfo=None, second=0, microsecond=0)
    start = dt.datetime.combine(payload.date, start_time)
    end = start + SLOT_TYPES[payload.type].duration

    if start < dt.datetime.now():
        raise HTTPException(400, "نمی‌توان برای زمان گذشته وقت ثبت کرد")

    overlaps = db.scalar(select(Slot.id).where(Slot.start_at < end, Slot.end_at > start).limit(1))
    if overlaps:
        raise HTTPException(409, "این بازه با یک وقت دیگر هم‌پوشانی دارد")

    slot = Slot(type=payload.type, start_at=start, end_at=end)
    db.add(slot)
    db.commit()
    return slot


@router.delete("/slots/{slot_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = db.get(Slot, slot_id)
    if slot is None:
        raise HTTPException(404, "وقت پیدا نشد")
    db.delete(slot)  # also removes its booking, if any
    db.commit()
