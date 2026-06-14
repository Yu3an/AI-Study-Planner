# AI Study Planner / Lernplan-Assistent

A beginner-friendly Python and Streamlit web app that creates a clear study plan for university exam preparation.

Users enter a course name, exam date, available study time, weekly study days, task list, and difficulty level. The app calculates the remaining days before the exam and distributes tasks across available study dates. It works without an API key, but also includes an optional OpenAI mode for more natural study advice.

## Features

- Course and exam setup
- Automatic calculation of days until exam
- Rule-based task distribution across study dates
- Daily study plan with focus recommendations
- Interactive task checklist with completion tracking
- Study playlist module with built-in and custom playlist links
- Optional weekend study plan with separate weekend study hours
- Pomodoro focus timer with focus-session logging
- Dark focus screen that only shows the timer and task checklist
- Focus log CSV export
- Difficulty-aware time estimation
- Practical revision advice
- CSV export
- English, Chinese, and German interface language pack
- Optional OpenAI API mode for AI-generated suggestions
- Simple Streamlit interface suitable for GitHub screenshots

## Project Structure

```text
ai-study-planner/
├── app.py
├── planner.py
├── ai_advisor.py
├── locales.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── .gitkeep
└── screenshots/
    └── .gitkeep
```

## Installation

```bash
cd ai-study-planner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
cd ai-study-planner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Optional AI Mode

The app works without an API key. If you want AI-generated study advice, enter an OpenAI API key in the sidebar.

The default rule-based mode still creates:

- the full study plan
- the schedule
- the CSV export
- revision recommendations

## Language Support

The app includes a small language pack in `locales.py` and supports:

- English
- Chinese
- German

The sidebar language selector changes the main interface labels, table headers, status text, focus text, default tasks, and rule-based study advice.

## Screenshot

Create a screenshot after running the app and save it here:

```text
screenshots/app-preview.png
```

You can then add it to this README:

```markdown
![App Screenshot](screenshots/app-preview.png)
```

## Example GitHub Commit Messages

```text
Initial commit: add Streamlit study planner app
Add rule-based task scheduling logic
Add optional OpenAI study advice mode
Add English Chinese German language pack
Add weekend study planning option
Add Pomodoro focus timer and focus log
Add task checklist with completion tracking
Add dark focus screen for Pomodoro sessions
Add study playlist module
Improve README with setup and resume description
```

## Resume Description

English:

```text
AI Study Planner: Built a Python and Streamlit web application that generates personalized exam study plans based on course tasks, available study time, difficulty level, exam date, and optional weekend availability. Implemented rule-based scheduling, interactive task checklists, a study playlist module, Pomodoro focus tracking with a dark focus screen, CSV export, multilingual UI, and optional OpenAI-powered study advice.
```

German:

```text
AI Study Planner / Lernplan-Assistent: Entwicklung einer Python- und Streamlit-Webanwendung zur automatischen Erstellung personalisierter Lernplaene fuer Pruefungen. Die Anwendung verteilt Lernaufgaben anhand von Pruefungsdatum, verfuegbarer Lernzeit, Wochenendverfuegbarkeit und Schwierigkeitsgrad, bietet interaktive Aufgaben-Checklisten, ein Lern-Playlist-Modul, Pomodoro-Fokustracking mit dunkler Fokusansicht, CSV-Export, mehrsprachige Benutzeroberflaeche sowie optional KI-gestuetzte Lernempfehlungen ueber die OpenAI API.
```

## Why This Project Is Good for a Beginner Portfolio

This project shows practical skills that are useful for an Informatik bachelor's student:

- Python programming
- simple web app development with Streamlit
- data handling with pandas
- basic scheduling logic
- clean project structure
- optional API integration
- user-focused feature design
