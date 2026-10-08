from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MeetingOut(BaseModel):
    meeting_id: str
    title: str
    description: str
    scheduled_at: datetime
    duration_minutes: int
    invite_link: str
    status: str
    created_at: datetime
    host_name: str


class InstantMeetingRequest(BaseModel):
    title: str = Field(default="Instant meeting", min_length=1, max_length=180)


class ScheduleMeetingRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=2000)
    scheduled_at: datetime
    duration_minutes: int = Field(ge=1, le=1440)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str):
        if not value.strip():
            raise ValueError("A meeting title is required")
        return value.strip()


class JoinMeetingRequest(BaseModel):
    meeting: str = Field(min_length=1)
    display_name: str = Field(min_length=1, max_length=120)


class ParticipantCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    is_host: bool = False


class ParticipantOut(BaseModel):
    id: int
    display_name: str
    joined_at: datetime
    left_at: datetime | None
    is_host: bool
