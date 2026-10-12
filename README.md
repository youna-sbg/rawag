# Booking API

Backend for a consultation booking system, built with FastAPI and SQLAlchemy.
An admin publishes free time slots, and clients book them.

There are two session types, defined in `app/config.py`:

| Type     | Name | Duration   |
|----------|------|------------|
| `peak`   | اوج  | 45 minutes |
| `growth` | رشد  | 25 minutes |

## Getting started

```bash
pip install -r requirements.txt
export ADMIN_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
uvicorn app.main:app
```

Interactive docs are served at `http://localhost:8000/docs`.

## Configuration

Environment variables:

| Variable        | Description                                      | Default                  |
|-----------------|--------------------------------------------------|--------------------------|
| `ADMIN_API_KEY` | Key for admin endpoints, sent as `X-API-Key`     | `change-me`              |
| `CORS_ORIGINS`  | Comma-separated list of allowed frontend origins | `*`                      |
| `DATABASE_URL`  | SQLAlchemy database URL                          | `sqlite:///./booking.db` |

Set `ADMIN_API_KEY` and `CORS_ORIGINS` before deploying. The defaults are for local development only.

## Endpoints

| Endpoint                | Auth  | Description                                                   |
|-------------------------|-------|---------------------------------------------------------------|
| `GET /slot-types`       |       | Session types and durations                                   |
| `GET /slots`            |       | List slots. Query: `day`, `type`, `only_available` (default true) |
| `POST /bookings`        |       | Book a slot: `slot_id`, `client_name`, `client_phone`, `note` |
| `POST /slots`           | admin | Create a slot: `type`, `date`, `start_time`                   |
| `DELETE /slots/{id}`    | admin | Delete a slot and its booking                                 |
| `GET /bookings`         | admin | List bookings with slot details, ordered by time              |
| `DELETE /bookings/{id}` | admin | Cancel a booking and free the slot                            |

## Notes

- Times are stored as naive local datetimes. Any timezone or seconds in `start_time` are ignored.
- Slots cannot overlap, and a slot can only be booked once. Both cases return `409`.
- Tables are created on startup. There are no migrations yet; consider Alembic and PostgreSQL for production.
