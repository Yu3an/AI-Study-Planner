from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd


DIFFICULTY_MULTIPLIER = {
    "Easy": 0.85,
    "Medium": 1.0,
    "Hard": 1.3,
}


def clean_tasks(raw_tasks: str) -> List[str]:
    """Convert a multiline text input into a clean list of study tasks."""
    tasks = []
    for line in raw_tasks.splitlines():
        task = line.strip("- ").strip()
        if task:
            tasks.append(task)
    return tasks


def count_days_until_exam(exam_date: date, today: Optional[date] = None) -> int:
    """Return the number of calendar days from today until the exam date."""
    today = today or date.today()
    return (exam_date - today).days


def build_study_dates(
    exam_date: date,
    study_days_per_week: int,
    include_weekends: bool = False,
    today: Optional[date] = None,
) -> List[date]:
    """
    Build a list of planned study dates before the exam.

    The function spreads study days across the week by using the selected
    weekly study-day limit. It keeps the exam day free for rest and final review.
    """
    today = today or date.today()
    if exam_date <= today:
        return []

    all_dates = []
    current_day = today

    while current_day < exam_date:
        if is_planned_study_day(current_day, study_days_per_week, include_weekends):
            all_dates.append(current_day)
        current_day += timedelta(days=1)

    return all_dates


def is_planned_study_day(
    study_date: date,
    study_days_per_week: int,
    include_weekends: bool,
) -> bool:
    """Decide if a date should be included in the study plan."""
    weekday = study_date.weekday()

    if include_weekends and weekday >= 5:
        return True

    # weekday() returns 0 for Monday and 6 for Sunday.
    # Without weekend mode, this keeps the first N weekdays as study days.
    weekday_limit = study_days_per_week if not include_weekends else min(study_days_per_week, 5)
    return weekday < weekday_limit


def estimate_task_hours(
    tasks: List[str],
    daily_hours: float,
    difficulty: str,
) -> List[Tuple[str, float]]:
    """
    Estimate how many hours each task needs.

    This beginner-friendly version uses equal distribution plus a difficulty
    multiplier. A real product could replace this with historical learning data.
    """
    if not tasks:
        return []

    multiplier = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)
    base_hours = max(daily_hours * multiplier, 0.5)
    return [(task, round(base_hours, 1)) for task in tasks]


def generate_plan(
    course_name: str,
    exam_date: date,
    daily_hours: float,
    study_days_per_week: int,
    raw_tasks: str,
    difficulty: str,
    include_weekends: bool = False,
    weekend_hours: float = 0,
    today: Optional[date] = None,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Generate a rule-based study plan and summary statistics."""
    today = today or date.today()
    tasks = clean_tasks(raw_tasks)
    study_dates = build_study_dates(
        exam_date,
        study_days_per_week,
        include_weekends,
        today,
    )
    days_until_exam = count_days_until_exam(exam_date, today)

    if not tasks or not study_dates:
        summary = {
            "course_name": course_name,
            "days_until_exam": days_until_exam,
            "available_study_days": len(study_dates),
            "total_tasks": len(tasks),
            "total_available_hours": 0,
            "estimated_needed_hours": 0,
            "status": "Not enough data",
            "has_weekend_plan": include_weekends,
        }
        return pd.DataFrame(), summary

    estimated_tasks = estimate_task_hours(tasks, daily_hours, difficulty)
    total_available_hours = round(
        sum(get_planned_hours(study_date, daily_hours, weekend_hours) for study_date in study_dates),
        1,
    )
    estimated_needed_hours = round(sum(hours for _, hours in estimated_tasks), 1)

    plan_rows = []
    task_index = 0

    for study_date in study_dates:
        day_planned_hours = get_planned_hours(study_date, daily_hours, weekend_hours)
        remaining_hours = day_planned_hours
        daily_tasks = []

        # Assign at least one task per study day while there are open tasks.
        while task_index < len(estimated_tasks) and remaining_hours > 0:
            task, estimated_hours = estimated_tasks[task_index]
            task_planned_hours = min(estimated_hours, remaining_hours)
            daily_tasks.append(f"{task} ({task_planned_hours:g}h)")
            remaining_hours = round(remaining_hours - task_planned_hours, 2)

            # Move to the next task when the current task fits into this day.
            if estimated_hours <= task_planned_hours:
                task_index += 1
            else:
                estimated_tasks[task_index] = (
                    task,
                    round(estimated_hours - task_planned_hours, 1),
                )
                break

        if not daily_tasks:
            daily_tasks.append("Review notes and practice weak topics")

        plan_rows.append(
            {
                "Date": study_date.strftime("%Y-%m-%d"),
                "Day Type": choose_day_type(study_date),
                "Course": course_name,
                "Planned Hours": day_planned_hours,
                "Tasks": "; ".join(daily_tasks),
                "Focus": choose_daily_focus(study_date, exam_date),
            }
        )

    status = "Realistic"
    if estimated_needed_hours > total_available_hours:
        status = "Tight schedule"

    summary = {
        "course_name": course_name,
        "days_until_exam": days_until_exam,
        "available_study_days": len(study_dates),
        "total_tasks": len(tasks),
        "total_available_hours": total_available_hours,
        "estimated_needed_hours": estimated_needed_hours,
        "status": status,
        "has_weekend_plan": include_weekends,
    }

    return pd.DataFrame(plan_rows), summary


def choose_daily_focus(study_date: date, exam_date: date) -> str:
    """Give a short learning focus depending on how close the exam is."""
    days_left = (exam_date - study_date).days

    if days_left <= 2:
        return "Final review, mistakes, formulas"
    if days_left <= 7:
        return "Practice exercises and old exam questions"
    if study_date.weekday() >= 5:
        return "Weekend deep work and weekly review"
    return "Understand concepts and create summaries"


def get_planned_hours(study_date: date, daily_hours: float, weekend_hours: float) -> float:
    """Use a separate study duration for Saturday and Sunday if configured."""
    if study_date.weekday() >= 5 and weekend_hours > 0:
        return weekend_hours
    return daily_hours


def choose_day_type(study_date: date) -> str:
    """Return a stable day type label for localization in the UI."""
    if study_date.weekday() >= 5:
        return "Weekend Study"
    return "Weekday Study"


def build_rule_based_advice(summary: Dict[str, object], difficulty: str) -> List[str]:
    """Create simple study advice without using any external API."""
    advice = [
        "Start with the most important topics and mark unclear points early.",
        "Use short active-recall sessions instead of only rereading notes.",
        "Reserve the last two days for mistakes, summaries, and exam-style questions.",
    ]

    if summary.get("status") == "Tight schedule":
        advice.append(
            "Your schedule is tight. Reduce low-priority topics or increase daily study time."
        )

    if difficulty == "Hard":
        advice.append(
            "For a hard course, add extra practice blocks for problem solving and examples."
        )

    return advice
