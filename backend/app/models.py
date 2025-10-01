from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel, Field, validator


class Course(BaseModel):
    """
    A course the student is preparing for.
    Confidence level: 1–5 (1 = very weak, 5 = very confident).
    """
    name: str
    confidence_level: int = Field(ge=1, le=5)
    credit_unit: int = Field(ge=1, description="Credit units for the course")


class GenerateRequest(BaseModel):
    """
    Input from the user for schedule generation.
    """
    student_name: str
    academic_level: str  # e.g., "100L", "200L"
    semester: str        # e.g., "First Semester", "Second Semester"
    avg_hours_per_day: float = Field(gt=0)
    courses: List[Course]


class DailyAllocation(BaseModel):
    """
    A single day’s study plan.
    """
    day: str                  # e.g., "Monday"
    allocations: List[Dict[str, float]]
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
    per_course_hours: Dict[str, float] | None = None
