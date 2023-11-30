from pydantic import BaseModel, Field
from typing import Literal, Any, Union, Optional

class Annotation(BaseModel):
    path: str
    start_line: int
    end_line: int
    annotation_level: Literal["notice", "warning", "failure"]
    message: str
    title: str
    raw_details: str

class CheckRun(BaseModel):
    name: str
    head_sha: str
    status: Literal["queued", "in_progress", "completed"]
    conclusion: Literal["success", "failure", "neutral", "cancelled", "timed_out", "action_required"]
    output: dict[str, Any] = Field(default_factory=dict)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    check_suite: dict[str, Any] = Field(default_factory=dict)
    external_id: str
    started_at: str
    completed_at: str
    output: dict[str, Any] = Field(default_factory=dict)
    annotations: list[Annotation] = Field(default_factory=list)
    pull_requests: list[dict[str, Any]] = Field(default_factory=list)
