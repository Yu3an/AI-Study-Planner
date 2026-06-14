# AI Study Planner / Lernplan-Assistent

A beginner-friendly Python and Streamlit web app that creates a clear study plan for university exam preparation.

Users enter a course name, exam date, available study time, weekly study days, task list, and difficulty level. The app calculates the remaining days before the exam and distributes tasks across available study dates. It works without an API key, but also includes an optional OpenAI mode for more natural study advice.

## Live Demo
Try the app here:
https://your-app-name.streamlit.app
  
## Features

- Course and exam setup
- Reference tasks plus custom task input
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

