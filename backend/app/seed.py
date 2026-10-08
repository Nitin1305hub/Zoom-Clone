from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Meeting, User


def seed(db: Session, frontend_url: str):
    if db.query(User).filter_by(email="alex@meetly.local").first():
        return
    host = User(name="Alex Morgan", email="alex@meetly.local")
    db.add(host); db.flush()
    now = datetime.now().replace(second=0, microsecond=0)
    samples = [
        ("Product design sync", "Review the Q4 design system and next milestones.", now + timedelta(days=1, hours=2), 45, "scheduled"),
        ("Team standup", "Daily priorities, blockers, and hand-offs.", now + timedelta(days=2, hours=1), 30, "scheduled"),
        ("Client discovery workshop", "Initial working session with the Northstar team.", now + timedelta(days=4, hours=4), 60, "scheduled"),
        ("Weekly planning", "Sprint planning and capacity review.", now - timedelta(days=1, hours=2), 45, "completed"),
        ("Research review", "Share user interview insights and decisions.", now - timedelta(days=3, hours=3), 30, "completed"),
    ]
    ids = ["482 391 726", "809 164 537", "674 205 918", "371 824 605", "956 410 283"]
    for item, meeting_id in zip(samples, ids):
        title, description, scheduled_at, duration, status = item
        db.add(Meeting(meeting_id=meeting_id, title=title, description=description, host_user_id=host.id,
                       scheduled_at=scheduled_at, duration_minutes=duration,
                       invite_link=f"{frontend_url}/meeting/{meeting_id.replace(' ', '')}", status=status))
    db.commit()
