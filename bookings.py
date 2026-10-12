import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager

from app.deps import get_db, require_admin
from app.models import Booking, Slot
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings")


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    slot = db.get(Slot, payload.slot_id)
    if slot is None:
        raise HTTPException(404, "وقت پیدا نشد")
    if slot.start_at < dt.datetime.now():
        raise HTTPException(400, "زمان این وقت گذشته است")

    booking = Booking(**payload.model_dump())
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        # the unique constraint on slot_id caught a concurrent booking
        db.rollback()
        raise HTTPException(409, "این وقت قبلاً رزرو شده است")
    return booking


@router.get("", response_model=list[BookingOut], dependencies=[Depends(require_admin)])
def list_bookings(db: Session = Depends(get_db)):
    query = (
        select(Booking)
        .join(Booking.slot)
        .options(contains_eager(Booking.slot))
        .order_by(Slot.start_at)
    )
    return db.scalars(query).all()


@router.delete("/{booking_id}", status_code=204, dependencies=[Depends(require_admin)])
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(404, "رزرو پیدا نشد")
    db.delete(booking)
    db.commit()
