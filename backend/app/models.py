from __future__ import annotations
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator, root_validator


class Course(BaseModel):
    """
    A course the student is preparing for.
    Confidence level: 1–5 (1 = very weak, 5 = very confident).
    """
    name: str
    confidence_level: int = Field(ge=1, le=5)
    credit_unit: int = Field(ge=1, description="Credit units for the course")

    @root_validator(pre=True)
    def _map_legacy_fields(cls, values):  # type: ignore[override]
        # accept legacy keys from older frontend payloads
        if "confidence_level" not in values and "confidence" in values:
            values["confidence_level"] = values.pop("confidence")
        if "credit_unit" not in values and "creditUnit" in values:
            values["credit_unit"] = values.pop("creditUnit")
        # coerce to int safely
        try:
            values["confidence_level"] = int(values.get("confidence_level", 3))
        except Exception:
            values["confidence_level"] = 3
        try:
            values["credit_unit"] = int(values.get("credit_unit", 1))
        except Exception:
            values["credit_unit"] = 1
        return values


class GenerateRequest(BaseModel):
    """
    Input from the user for schedule generation.
    """
    student_name: str
    academic_level: str  # e.g., "100L", "200L"
    semester: str        # e.g., "First Semester", "Second Semester"
    avg_hours_per_day: float = Field(gt=0, le=24)
    courses: List[Course]


class DailyAllocation(BaseModel):
    """
    A single day’s study plan.
    """
    day: str                  # e.g., "Monday"
    
    class Allocation(BaseModel):
        course: str
        hours: float

    allocations: List[Allocation]
    # Example: [{"course": "Mathematics", "hours": 3.0}, {"course": "Physics", "hours": 2.0}]


class GenerateResponse(BaseModel):
    """
    Output schedule returned by the backend.
    """
    student_name: str
    academic_level: str
    semester: str
    total_weekly_hours: float
    schedule: List[DailyAllocation]
    notes: List[str] = []
    # Optional extra breakdown used by the frontend for summaries
    per_course_hours: Optional[Dict[str, float]] = None
