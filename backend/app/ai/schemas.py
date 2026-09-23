"""Structured transcript and analysis contracts for meeting intelligence."""
from typing import Literal

from pydantic import BaseModel, Field


class StrictModel(BaseModel):
    class Config:
        extra = "forbid"


MeetingLanguage = Literal["ru", "kk", "ru_kk"]


class TranscriptSegment(StrictModel):
    segment_id: str
    speaker_id: str | None = None
    speaker_name: str | None = None
    start_ms: int | None = Field(default=None, ge=0)
    end_ms: int | None = Field(default=None, ge=0)
    text: str


class MeetingInput(StrictModel):
    meeting_id: str
    title: str | None = None
    language: MeetingLanguage
    segments: list[TranscriptSegment]


class AnalysisRequest(StrictModel):
    meeting: MeetingInput


class EvidenceFinding(StrictModel):
    text: str
    evidence_segment_ids: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"


class ActionItem(StrictModel):
    task: str
    responsible_person: str | None = None
    deadline_text: str | None = None
    evidence_segment_ids: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"


class MeetingAnalysis(StrictModel):
    meeting_id: str
    title: str | None = None
    language: MeetingLanguage
    summary: str
    key_points: list[EvidenceFinding]
    decisions: list[EvidenceFinding]
    action_items: list[ActionItem]
    open_questions: list[EvidenceFinding]
