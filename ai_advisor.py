from __future__ import annotations

from typing import Dict, List


def generate_ai_advice(
    api_key: str,
    course_name: str,
    difficulty: str,
    tasks: List[str],
    summary: Dict[str, object],
) -> str:
    """
    Generate optional AI advice with the OpenAI API.

    The project works without this function. It is only called when the user
    enters an API key in the Streamlit sidebar.
    """
    if not api_key:
        return ""

    try:
        from openai import OpenAI
    except ImportError:
        return (
            "OpenAI package is not installed. Run `pip install openai` "
            "or use the rule-based mode."
        )

    client = OpenAI(api_key=api_key)

    prompt = f"""
Create concise study advice for a beginner university student.

Course: {course_name}
Difficulty: {difficulty}
Days until exam: {summary.get("days_until_exam")}
Available study days: {summary.get("available_study_days")}
Daily tasks: {", ".join(tasks[:12])}

Return 4 to 6 practical bullet points. Keep the language simple.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.4,
            max_output_tokens=300,
        )
        return response.output_text.strip()
    except Exception as exc:
        return f"AI advice could not be generated: {exc}"
