from __future__ import annotations
from typing import List, Dict
from .models import (
    GenerateRequest,
    GenerateResponse,
    DailyAllocation,
)


def generate_schedule(req: GenerateRequest) -> GenerateResponse:
    """
    Generate a weekly study schedule based on:
    - average daily study hours
    - courses, their confidence levels, and credit units
    Lower confidence and higher credit units receive more time.
    """

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Step 1: Calculate total weight. Confidence dominates; credit unit is a secondary factor
    weights: Dict[str, float] = {}
    for course in req.courses:
        # Inverse confidence (1-5) -> 5 strongest influence
        inv_conf = float(max(1, 6 - int(course.confidence_level)))
        # Credit unit modulation (each extra unit adds 30% more weight)
        credit = max(1, int(getattr(course, "credit_unit", 1)))
        credit_factor = 1.0 + 0.30 * float(credit - 1)
        weights[course.name] = inv_conf * credit_factor

    total_weight = sum(weights.values()) or 1.0

    # Step 2: Calculate weekly total hours
    weekly_hours = float(req.avg_hours_per_day) * len(days)

    # Step 3: Hours per course per week
    course_hours: Dict[str, float] = {}
    for course_name, w in weights.items():
        course_hours[course_name] = (w / total_weight) * weekly_hours

    # Step 4: Build daily allocations (spread evenly across days)
    schedule: List[DailyAllocation] = []
    for day in days:
        allocations = []
        for course_name, hours in course_hours.items():
            per_day = max(1.0, hours / len(days))
            allocations.append({
                "course": course_name,
                "hours": round(per_day, 2)
            })
        schedule.append(DailyAllocation(day=day, allocations=allocations))

    return GenerateResponse(
        student_name=req.student_name,
        academic_level=req.academic_level,
        semester=req.semester,
        total_weekly_hours=round(weekly_hours, 2),
        per_course_hours={k: round(v, 2) for k, v in course_hours.items()},
        schedule=schedule,
        notes=[
            "Lower confidence and higher credit-unit courses are allocated more study time.",
            "Hours are distributed evenly across the week."
        ]
    )
