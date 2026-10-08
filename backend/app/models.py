from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="host")


class Meeting(Base):
    __tablename__ = "meetings"
    __table_args__ = (Index("ix_meetings_scheduled_at", "scheduled_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    host_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    invite_link: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    host: Mapped[User] = relationship(back_populates="meetings")
    participants: Mapped[list["Participant"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"
    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_db_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    left_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_host: Mapped[bool] = mapped_column(Boolean, default=False)
    meeting: Mapped[Meeting] = relationship(back_populates="participants")
