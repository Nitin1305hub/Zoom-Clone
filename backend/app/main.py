import os, re, secrets
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import Meeting, Participant, User
from .schemas import (InstantMeetingRequest, JoinMeetingRequest, MeetingOut, ParticipantCreate,
                      ParticipantOut, ScheduleMeetingRequest)
from .seed import seed

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
app = FastAPI(title="Meetly API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_BASE_URL],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db: seed(db, FRONTEND_BASE_URL)


def format_id():
    digits = "".join(str(secrets.randbelow(10)) for _ in range(9))
    return f"{digits[:3]} {digits[3:6]} {digits[6:]}"


def create_meeting(db, title, description, scheduled_at, duration, state="scheduled"):
    host = db.query(User).filter_by(email="alex@meetly.local").first()
    if not host:
        host = User(name="Alex Morgan", email="alex@meetly.local"); db.add(host); db.flush()
    meeting_id = format_id()
    while db.query(Meeting).filter_by(meeting_id=meeting_id).first(): meeting_id = format_id()
    compact = meeting_id.replace(" ", "")
    meeting = Meeting(meeting_id=meeting_id, title=title, description=description, host_user_id=host.id,
                      scheduled_at=scheduled_at, duration_minutes=duration, status=state,
                      invite_link=f"{FRONTEND_BASE_URL}/meeting/{compact}")
    db.add(meeting); db.commit(); db.refresh(meeting)
    return meeting


def serialize(m: Meeting):
    return MeetingOut(meeting_id=m.meeting_id, title=m.title, description=m.description, scheduled_at=m.scheduled_at,
                      duration_minutes=m.duration_minutes, invite_link=m.invite_link, status=m.status,
                      created_at=m.created_at, host_name=m.host.name)


def normalize(value: str):
    match = re.search(r"(?:meeting/)?(\d{3}[\s-]?\d{3}[\s-]?\d{3})", value)
    if not match: return ""
    digits = re.sub(r"\D", "", match.group(1))
    return f"{digits[:3]} {digits[3:6]} {digits[6:]}"


def utc_naive(value: datetime) -> datetime:
    """Store and compare all meeting times as UTC-naive SQLite datetimes."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def lookup(db, meeting_id):
    normalized = normalize(meeting_id) or meeting_id
    meeting = db.query(Meeting).options(joinedload(Meeting.host)).filter_by(meeting_id=normalized).first()
    if not meeting: raise HTTPException(404, "We couldn't find that meeting. Check the ID or invitation link and try again.")
    return meeting


@app.get("/api/health")
def health(): return {"status": "ok"}


@app.get("/health")
def root_health(): return {"status": "ok"}

@app.get("/api/meetings", response_model=list[MeetingOut])
def meetings(db: Session = Depends(get_db)):
    return [serialize(m) for m in db.query(Meeting).options(joinedload(Meeting.host)).order_by(Meeting.scheduled_at.desc()).all()]

@app.get("/api/meetings/upcoming", response_model=list[MeetingOut])
def upcoming(db: Session = Depends(get_db)):
    rows = db.query(Meeting).options(joinedload(Meeting.host)).filter(Meeting.scheduled_at >= datetime.now(), Meeting.status != "completed").order_by(Meeting.scheduled_at).all()
    return [serialize(m) for m in rows]

@app.get("/api/meetings/recent", response_model=list[MeetingOut])
def recent(db: Session = Depends(get_db)):
    rows = db.query(Meeting).options(joinedload(Meeting.host)).filter((Meeting.scheduled_at < datetime.now()) | (Meeting.status == "completed")).order_by(Meeting.scheduled_at.desc()).limit(10).all()
    return [serialize(m) for m in rows]

@app.get("/api/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)): return serialize(lookup(db, meeting_id))

@app.post("/api/meetings/instant", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
def instant(payload: InstantMeetingRequest, db: Session = Depends(get_db)):
    return serialize(create_meeting(db, payload.title.strip(), "Created for an instant conversation.", datetime.now(), 60, "active"))

@app.post("/api/meetings/schedule", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
def schedule(payload: ScheduleMeetingRequest, db: Session = Depends(get_db)):
    scheduled_at = utc_naive(payload.scheduled_at)
    if scheduled_at < datetime.utcnow():
        raise HTTPException(422, "Choose a future date and time for this meeting.")
    return serialize(create_meeting(db, payload.title, payload.description, scheduled_at, payload.duration_minutes))

@app.post("/api/meetings/join", response_model=MeetingOut)
def join(payload: JoinMeetingRequest, db: Session = Depends(get_db)):
    meeting = lookup(db, payload.meeting)
    db.add(Participant(meeting_db_id=meeting.id, display_name=payload.display_name.strip())); db.commit()
    return serialize(meeting)

@app.post("/api/meetings/{meeting_id}/participants", response_model=ParticipantOut, status_code=201)
def add_participant(meeting_id: str, payload: ParticipantCreate, db: Session = Depends(get_db)):
    meeting = lookup(db, meeting_id); p = Participant(meeting_db_id=meeting.id, display_name=payload.display_name.strip(), is_host=payload.is_host)
    db.add(p); db.commit(); db.refresh(p); return p

@app.get("/api/meetings/{meeting_id}/participants", response_model=list[ParticipantOut])
def participants(meeting_id: str, db: Session = Depends(get_db)):
    meeting = lookup(db, meeting_id); return db.query(Participant).filter_by(meeting_db_id=meeting.id).order_by(Participant.joined_at).all()

@app.delete("/api/meetings/{meeting_id}/participants/{participant_id}", status_code=204)
def remove_participant(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = lookup(db, meeting_id); p = db.query(Participant).filter_by(id=participant_id, meeting_db_id=meeting.id).first()
    if not p: raise HTTPException(404, "Participant not found")
    db.delete(p); db.commit()
