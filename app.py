from datetime import date, datetime, time as datetime_time, timedelta
import random
import time
from uuid import uuid4

import pandas as pd
import streamlit as st

from ai_advisor import generate_ai_advice
from locales import get_text
from planner import clean_tasks, generate_plan


st.set_page_config(
    page_title="AI Study Planner",
    layout="wide",
)


def main() -> None:
    init_focus_state()
    init_checklist_state()

    if st.session_state.focus_screen_active:
        language = st.session_state.get("language", "English")
        text = get_text(language)
        show_focus_screen(text)
        return

    with st.sidebar:
        language = st.selectbox("Language / 语言 / Sprache", ["English", "中文", "Deutsch"])
        st.session_state.language = language
        text = get_text(language)

        st.header(text["optional_ai_mode"])
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help=text["api_key_help"],
        )
        st.info(text["api_info"])

    apply_typography_style()
    show_companion_banner(text)
    st.title(text["title"])
    st.caption(text["caption"])
    show_quick_nav(text)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        add_anchor("course-settings")
        st.subheader(text["course_settings"])
        course_name = st.text_input(text["course_name"], value=text["default_course"])
        exam_date = st.date_input(
            text["exam_date"],
            value=date.today() + timedelta(days=21),
            min_value=date.today(),
        )
        daily_hours = st.slider(text["daily_hours"], 0.5, 8.0, 2.0, 0.5)
        study_days_per_week = st.slider(text["study_days_per_week"], 1, 7, 5)
        include_weekends = st.checkbox(text["include_weekends"], value=True)
        weekend_hours = 0.0
        if include_weekends:
            weekend_hours = st.slider(text["weekend_hours"], 0.5, 10.0, 3.0, 0.5)

        difficulty_labels = text["difficulty_options"]
        selected_difficulty_label = st.selectbox(
            text["difficulty"],
            list(difficulty_labels.values()),
            index=1,
        )
        difficulty = reverse_lookup(difficulty_labels, selected_difficulty_label)

    with col_right:
        add_anchor("study-tasks")
        raw_tasks = build_task_input(text)

    st.session_state.last_course_name = course_name
    st.session_state.last_raw_tasks = raw_tasks

    show_task_checklist(text, raw_tasks)
    show_playlist(text)
    show_focus_timer(text, course_name)

    add_anchor("generate-plan")
    generate_from_main_button = st.button(
        text["generate"],
        type="primary",
        key="main_generate_plan",
    )

    if generate_from_main_button:
        render_generated_plan(
            api_key=api_key,
            course_name=course_name,
            exam_date=exam_date,
            daily_hours=daily_hours,
            study_days_per_week=study_days_per_week,
            raw_tasks=raw_tasks,
            difficulty=difficulty,
            include_weekends=include_weekends,
            weekend_hours=weekend_hours,
            text=text,
        )


def reverse_lookup(options: dict, selected_label: str) -> str:
    """Find the internal option key for a translated label."""
    for key, label in options.items():
        if label == selected_label:
            return key
    return "Medium"


def render_generated_plan(
    api_key: str,
    course_name: str,
    exam_date: date,
    daily_hours: float,
    study_days_per_week: int,
    raw_tasks: str,
    difficulty: str,
    include_weekends: bool,
    weekend_hours: float,
    text: dict,
) -> None:
    """Generate and render the study plan from any page action button."""
    plan_df, summary = generate_plan(
        course_name=course_name,
        exam_date=exam_date,
        daily_hours=daily_hours,
        study_days_per_week=study_days_per_week,
        raw_tasks=raw_tasks,
        difficulty=difficulty,
        include_weekends=include_weekends,
        weekend_hours=weekend_hours,
    )

    if plan_df.empty:
        st.error(text["input_error"])
        return

    show_summary(summary, text)
    show_plan(plan_df, text)
    show_advice(api_key, course_name, difficulty, raw_tasks, summary, text)


def build_task_input(text: dict) -> str:
    """Build the final task list from selected reference tasks and custom tasks."""
    st.subheader(text["study_tasks"])
    st.caption(
        text.get(
            "study_tasks_caption",
            "Select useful reference tasks and add your own tasks if needed.",
        )
    )

    reference_tasks = text.get("reference_tasks", clean_tasks(text.get("default_tasks", "")))
    selected_reference_tasks = st.multiselect(
        text.get("reference_tasks_label", "Reference tasks"),
        reference_tasks,
        default=reference_tasks[:4],
    )
    custom_tasks = st.text_area(
        text.get("custom_tasks_label", "Custom tasks"),
        value="",
        height=150,
        placeholder=text.get("custom_tasks_placeholder", "Enter one custom task per line"),
    )

    final_tasks = selected_reference_tasks + clean_tasks(custom_tasks)
    if final_tasks:
        st.caption(text.get("selected_tasks_preview", "Selected task list"))
        st.write(", ".join(final_tasks))
    else:
        st.info(
            text.get(
                "empty_task_selection",
                "Select at least one reference task or enter a custom task.",
            )
        )

    return "\n".join(final_tasks)


def apply_typography_style() -> None:
    """Apply a softer decorative style to headings without changing body text."""
    st.markdown(
        """
        <style>
        h1, h2, h3, h4,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            font-family: "Palatino Linotype", "Book Antiqua", Georgia, "Times New Roman", serif;
            letter-spacing: 0;
            color: #111827;
        }
        h1, [data-testid="stMarkdownContainer"] h1 {
            font-size: 2.65rem;
            font-weight: 700;
            font-style: normal;
        }
        h2, [data-testid="stMarkdownContainer"] h2 {
            font-size: 1.75rem;
            font-weight: 700;
            font-style: normal;
        }
        h3, h4,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            font-weight: 650;
            font-style: normal;
        }
        .module-anchor {
            display: block;
            position: relative;
            top: -5rem;
            visibility: hidden;
        }
        .quick-nav {
            display: flex;
            flex-direction: column;
            flex-wrap: wrap;
            gap: 0.55rem;
            position: fixed;
            top: 7rem;
            right: 0.9rem;
            width: 7.4rem;
            min-height: 2.8rem;
            margin: 0;
            padding: 0.55rem;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: rgba(250, 250, 250, 0.96);
            box-shadow: 0 8px 20px rgba(17, 24, 39, 0.08);
            z-index: 1000;
            overflow: hidden;
            transition: width 160ms ease, padding 160ms ease;
        }
        .quick-nav:hover,
        .quick-nav:focus-within {
            width: 9.8rem;
            padding: 0.75rem 0.7rem 0.85rem 0.7rem;
        }
        .quick-nav strong {
            align-self: center;
            white-space: nowrap;
            font-size: 0.85rem;
            letter-spacing: 0;
        }
        .quick-nav:hover strong,
        .quick-nav:focus-within strong {
            align-self: flex-start;
        }
        .quick-nav a {
            display: none;
            align-items: center;
            padding: 0.35rem 0.65rem;
            border: 1px solid #d1d5db;
            border-radius: 999px;
            color: #111827 !important;
            text-decoration: none;
            font-size: 0.9rem;
            background: #ffffff;
        }
        .quick-nav:hover a,
        .quick-nav:focus-within a {
            display: inline-flex;
        }
        .quick-nav a:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        .quick-nav-art {
            display: none;
            justify-content: center;
            gap: 0.45rem;
            padding-top: 0.25rem;
            margin-top: 0.25rem;
            border-top: 1px solid #e5e7eb;
        }
        .quick-nav:hover .quick-nav-art,
        .quick-nav:focus-within .quick-nav-art {
            display: flex;
        }
        .quick-friend {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.9rem;
            height: 1.9rem;
            border: 1.8px solid #111827;
            border-radius: 48% 48% 54% 54%;
            background: #ffffff;
            color: #111827;
            font-family: "Courier New", monospace;
            font-size: 0.58rem;
            font-weight: 700;
            line-height: 1;
            position: relative;
        }
        .quick-friend::after {
            content: "";
            position: absolute;
            width: 0.43rem;
            height: 0.43rem;
            top: -0.08rem;
            right: 0.12rem;
            border-top: 1.8px solid #111827;
            border-right: 1.8px solid #111827;
            background: #ffffff;
            transform: rotate(45deg);
        }
        .quick-friend.rabbit::after {
            width: 0.28rem;
            height: 0.8rem;
            top: -0.35rem;
            right: 0.32rem;
            border-radius: 0.45rem 0.45rem 0 0;
            transform: rotate(18deg);
        }
        .quick-friend.panda {
            box-shadow: inset 0.28rem 0 0 #111827, inset -0.28rem 0 0 #111827;
        }
        .module-spacer {
            height: 1.5rem;
        }
        .playlist-box {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.85rem 1rem;
            margin-top: 0.65rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: #fafafa;
        }
        .playlist-title {
            color: #111827;
            font-weight: 650;
        }
        .playlist-box a {
            color: #111827 !important;
            text-decoration: none;
            border: 1px solid #111827;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            background: #ffffff;
        }
        .playlist-box a:hover {
            background: #f3f4f6;
        }
        @media (max-width: 900px) {
            .quick-nav {
                display: flex;
                position: static;
                width: auto;
                min-height: 0;
                margin: 1rem 0 1.25rem 0;
                overflow: visible;
            }
            .quick-nav strong {
                align-self: flex-start;
            }
            .quick-nav a,
            .quick-nav-art {
                display: flex;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def add_anchor(anchor_id: str) -> None:
    """Add a jump target for the quick navigation."""
    st.markdown(f"<span id='{anchor_id}' class='module-anchor'></span>", unsafe_allow_html=True)


def add_module_spacer() -> None:
    """Add consistent vertical space between major modules."""
    st.markdown("<div class='module-spacer'></div>", unsafe_allow_html=True)


def show_quick_nav(text: dict) -> None:
    """Render a compact jump navigation for the main page modules."""
    links = [
        ("course-settings", text.get("nav_course", "Course")),
        ("study-tasks", text.get("nav_tasks", "Tasks")),
        ("task-checklist", text.get("nav_checklist", "Checklist")),
        ("playlist", text.get("nav_playlist", "Playlist")),
        ("focus-mode", text.get("nav_focus", "Focus")),
        ("generate-plan", text.get("generate", "Generate Study Plan")),
        ("study-plan", text.get("nav_plan", "Plan")),
    ]
    link_html = "".join(f"<a href='#{anchor}'>{label}</a>" for anchor, label in links)
    art_html = """
        <div class='quick-nav-art'>
            <span class='quick-friend'>=^</span>
            <span class='quick-friend rabbit'>o.</span>
            <span class='quick-friend panda'>•.</span>
        </div>
    """
    st.markdown(
        f"<nav class='quick-nav'><strong>{text.get('quick_actions', 'Quick Actions')}</strong>{link_html}{art_html}</nav>",
        unsafe_allow_html=True,
    )


def show_companion_banner(text: dict) -> None:
    """Render a minimal black-and-white companion strip at the top."""
    companion_message = random.choice(
        text.get("companion_messages", [text["companion_message"]])
    )

    st.markdown(
        f"""
        <style>
        .companion-banner {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1.25rem;
            min-height: 5.2rem;
            padding: 0 0.15rem 0.8rem 0.15rem;
            margin: -0.5rem 0 0.35rem 0;
            border-bottom: 1px solid #e5e7eb;
            background: #ffffff;
        }}
        .companion-group {{
            display: flex;
            align-items: flex-start;
            gap: 0.95rem;
            flex-wrap: wrap;
            min-height: 5rem;
        }}
        .hanging-friend {{
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 3.1rem;
            height: 3.1rem;
            margin-top: 1.15rem;
            border: 2px solid #111827;
            border-radius: 48% 48% 54% 54%;
            background: #ffffff;
            color: #111827;
            font-family: "Courier New", monospace;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1;
            transform: rotate(180deg);
        }}
        .hanging-friend::before {{
            content: "";
            position: absolute;
            width: 1px;
            height: 1.2rem;
            top: -1.35rem;
            left: 50%;
            background: #111827;
        }}
        .hanging-friend::after {{
            content: "";
            position: absolute;
            width: 0.7rem;
            height: 0.7rem;
            top: -0.2rem;
            right: 0.2rem;
            border-top: 2px solid #111827;
            border-right: 2px solid #111827;
            background: #ffffff;
            transform: rotate(45deg);
        }}
        .hanging-friend span {{
            display: block;
            transform: rotate(180deg);
            letter-spacing: 0;
        }}
        .hanging-friend.friend-cat {{
            border-radius: 44% 44% 55% 55%;
        }}
        .hanging-friend.friend-dog {{
            border-radius: 42% 42% 50% 50%;
        }}
        .hanging-friend.friend-dog::after {{
            width: 0.55rem;
            height: 0.95rem;
            right: -0.05rem;
            top: 0.15rem;
            border-radius: 0 0.5rem 0.5rem 0;
            transform: rotate(12deg);
        }}
        .hanging-friend.friend-rabbit::after {{
            width: 0.45rem;
            height: 1.25rem;
            top: -0.55rem;
            right: 0.45rem;
            border-radius: 0.5rem 0.5rem 0 0;
            transform: rotate(20deg);
        }}
        .hanging-friend.friend-panda {{
            box-shadow: inset 0.45rem 0 0 #111827, inset -0.45rem 0 0 #111827;
        }}
        .hanging-friend.friend-bear {{
            border-radius: 50%;
        }}
        .companion-bubble {{
            max-width: 26rem;
            padding-top: 1.15rem;
            background: transparent;
            color: #111827;
            font-size: 0.92rem;
            font-weight: 500;
            line-height: 1.45;
        }}
        @media (max-width: 700px) {{
            .companion-banner {{
                flex-direction: column;
                min-height: auto;
            }}
            .companion-bubble {{
                max-width: 100%;
                padding-top: 0;
            }}
        }}
        </style>
        <div class="companion-banner">
            <div class="companion-group">
                <span class="hanging-friend friend-cat" title="{text['companion_cat']}"><span>=^.^=</span></span>
                <span class="hanging-friend friend-dog" title="{text['companion_dog']}"><span>u.u</span></span>
                <span class="hanging-friend friend-rabbit" title="{text['companion_rabbit']}"><span>o.o</span></span>
                <span class="hanging-friend friend-panda" title="{text['companion_panda']}"><span>•.•</span></span>
                <span class="hanging-friend friend-bear" title="{text['companion_bear']}"><span>-.-</span></span>
            </div>
            <div class="companion-bubble">{companion_message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_task_checklist(text: dict, raw_tasks: str, compact: bool = False) -> None:
    """Show a checkbox list for study tasks and track completion progress."""
    add_module_spacer()
    add_anchor("task-checklist")
    st.divider()
    st.subheader(text["task_checklist"])

    tasks = clean_tasks(raw_tasks)
    if not tasks:
        st.info(text["empty_checklist"])
        return

    completed_count = 0
    for index, task in enumerate(tasks):
        task_key = f"task_done_{index}_{task}"
        default_value = st.session_state.task_checklist.get(task, False)
        is_done = st.checkbox(task, value=default_value, key=task_key)
        st.session_state.task_checklist[task] = is_done
        if is_done:
            completed_count += 1

    progress = completed_count / len(tasks)
    st.progress(progress)
    st.caption(
        text["checklist_progress"].format(
            completed=completed_count,
            total=len(tasks),
        )
    )

    if compact:
        return

    reset_col, export_col = st.columns([1, 1])
    if reset_col.button(text["reset_checklist"]):
        for task in tasks:
            st.session_state.task_checklist[task] = False
        st.rerun()

    checklist_df = pd.DataFrame(
        [
            {
                "Task": task,
                "Completed": text["completed_yes"] if st.session_state.task_checklist.get(task) else text["completed_no"],
            }
            for task in tasks
        ]
    )
    checklist_df = checklist_df.rename(columns=text["checklist_columns"])
    csv_data = checklist_df.to_csv(index=False).encode("utf-8-sig")
    export_col.download_button(
        label=text["download_checklist"],
        data=csv_data,
        file_name="task_checklist.csv",
        mime="text/csv",
    )


def show_playlist(text: dict) -> None:
    """Show study playlist links and optional custom playlist input."""
    add_module_spacer()
    add_anchor("playlist")
    st.divider()
    st.subheader(text.get("playlist", "Study Playlist"))
    st.caption(
        text.get(
            "playlist_caption",
            "Choose a background playlist for reading, coding, or deep work.",
        )
    )

    playlist_options = text.get(
        "playlist_options",
        {
            "Lo-fi focus": "https://www.youtube.com/results?search_query=lofi+study+music",
            "Classical study": "https://www.youtube.com/results?search_query=classical+music+for+studying",
            "Rain ambience": "https://www.youtube.com/results?search_query=rain+sounds+for+studying",
            "Deep work": "https://www.youtube.com/results?search_query=deep+work+music",
        },
    )
    selected_playlist = st.selectbox(
        text.get("playlist_select", "Playlist type"),
        list(playlist_options.keys()),
    )
    selected_url = playlist_options[selected_playlist]

    custom_url = st.text_input(
        text.get("custom_playlist", "Custom playlist link"),
        placeholder="https://...",
    )
    active_url = custom_url.strip() or selected_url

    link_label = text.get("open_playlist", "Open playlist")
    st.markdown(
        f"""
        <div class="playlist-box">
            <div class="playlist-title">{selected_playlist}</div>
            <a href="{active_url}" target="_blank" rel="noopener noreferrer">{link_label}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_checklist_state() -> None:
    """Initialize task checklist state."""
    if "task_checklist" not in st.session_state:
        st.session_state.task_checklist = {}


def show_focus_screen(text: dict) -> None:
    """Render a distraction-free dark focus page."""
    apply_focus_screen_style()

    course_name = st.session_state.get("last_course_name", text["default_course"])
    raw_tasks = st.session_state.get("last_raw_tasks", text["default_tasks"])

    st.markdown(f"<h1 class='focus-title'>{text['focus_screen_title']}</h1>", unsafe_allow_html=True)
    if st.button(text["exit_focus_screen"]):
        st.session_state.focus_screen_active = False
        st.rerun()

    timer_col, checklist_col = st.columns([1, 1])
    with timer_col:
        show_minimal_focus_timer(text, course_name)
    with checklist_col:
        show_task_checklist(text, raw_tasks, compact=True)


def apply_focus_screen_style() -> None:
    """Apply dark CSS for the dedicated focus screen."""
    st.markdown(
        """
        <style>
        .stApp {
            background: #050505 !important;
            color: #f4f4f5 !important;
        }
        header, [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: #050505 !important;
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="block-container"] {
            background: #050505 !important;
            color: #f4f4f5 !important;
        }
        h1, h2, h3, h4, p, label,
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"],
        [data-testid="stMetric"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            color: #f4f4f5 !important;
        }
        .focus-title {
            text-align: center;
            font-size: 2.4rem;
            margin: 1rem 0 2rem 0;
        }
        [data-testid="stMetricValue"] {
            font-size: 5rem;
            text-align: center;
        }
        [data-testid="stMetricLabel"] {
            text-align: center;
        }
        .stButton > button,
        .stDownloadButton > button {
            background: #18181b !important;
            color: #f4f4f5 !important;
            border: 1px solid #3f3f46 !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #27272a !important;
            border-color: #71717a !important;
            color: #ffffff !important;
        }
        input, textarea,
        [data-baseweb="input"],
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"],
        [data-baseweb="select"] span {
            background: #111113 !important;
            color: #f4f4f5 !important;
            border-color: #3f3f46 !important;
        }
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {
            background: #111113 !important;
            color: #f4f4f5 !important;
        }
        [role="option"] {
            background: #111113 !important;
            color: #f4f4f5 !important;
        }
        [role="option"]:hover {
            background: #27272a !important;
        }
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] span,
        [data-testid="stCheckbox"] p {
            color: #f4f4f5 !important;
        }
        [data-testid="stProgress"] > div > div {
            background-color: #27272a !important;
        }
        [data-testid="stAlert"] {
            background: #111827 !important;
            color: #f4f4f5 !important;
            border: 1px solid #374151 !important;
        }
        [data-testid="stDataFrame"],
        [data-testid="stDataFrame"] div {
            background: #111111 !important;
            color: #f4f4f5 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_minimal_focus_timer(text: dict, course_name: str) -> None:
    """Show only the active timer controls for the dark focus screen."""
    st.subheader(text["focus_mode"])

    if st.session_state.focus_duration_seconds == 0:
        mode_labels = text["pomodoro_modes"]
        selected_mode_label = st.selectbox(
            text["timer_mode"],
            list(mode_labels.values()),
            index=0,
        )
        selected_mode = reverse_lookup(mode_labels, selected_mode_label)
        default_minutes = {
            "Focus": 25,
            "Short Break": 5,
            "Long Break": 15,
        }[selected_mode]
        minutes = st.number_input(
            text["timer_minutes"],
            min_value=1,
            max_value=120,
            value=default_minutes,
            step=1,
        )
        if st.button(text["start_timer"], type="primary"):
            start_timer(selected_mode, int(minutes))
            st.rerun()
    else:
        remaining_seconds, elapsed_seconds = calculate_timer_seconds()
        st.metric(text["time_remaining"], format_seconds(remaining_seconds))
        st.progress(calculate_progress(elapsed_seconds, st.session_state.focus_duration_seconds))

        pause_col, reset_col, refresh_col = st.columns(3)
        if pause_col.button(text["pause_timer"]):
            pause_timer()
            st.rerun()
        if reset_col.button(text["reset_timer"]):
            reset_timer()
            st.rerun()
        if refresh_col.button(text["refresh_timer"]):
            st.rerun()

        if (
            st.session_state.focus_duration_seconds > 0
            and remaining_seconds == 0
            and st.session_state.focus_running
        ):
            save_focus_session(
                course_name=course_name,
                mode=st.session_state.focus_mode,
                minutes=round(st.session_state.focus_duration_seconds / 60),
                note=course_name,
            )
            reset_timer()
            st.success(text["focus_completed"])
            st.rerun()


def show_focus_timer(text: dict, course_name: str) -> None:
    """Display a simple Pomodoro timer and session log."""
    add_module_spacer()
    add_anchor("focus-mode")
    st.divider()

    timer_col, log_col = st.columns([1, 1])

    with timer_col:
        st.markdown(f"#### {text['focus_mode']}")
        mode_labels = text["pomodoro_modes"]
        selected_mode_label = st.selectbox(
            text["timer_mode"],
            list(mode_labels.values()),
            index=0,
        )
        selected_mode = reverse_lookup(mode_labels, selected_mode_label)

        default_minutes = {
            "Focus": 25,
            "Short Break": 5,
            "Long Break": 15,
        }[selected_mode]
        minutes = st.number_input(
            text["timer_minutes"],
            min_value=1,
            max_value=120,
            value=default_minutes,
            step=1,
        )
        note = st.text_input(text["focus_note"], value=course_name)

        remaining_seconds, elapsed_seconds = calculate_timer_seconds()
        if st.session_state.focus_duration_seconds == 0:
            remaining_seconds = int(minutes * 60)

        st.metric(text["time_remaining"], format_seconds(remaining_seconds))
        progress = calculate_progress(elapsed_seconds, st.session_state.focus_duration_seconds)
        st.progress(progress)

        if st.button(text["open_focus_screen"], type="secondary"):
            st.session_state.focus_screen_active = True
            st.rerun()

        start_col, pause_col, reset_col, save_col = st.columns(4)
        if start_col.button(text["start_timer"]):
            start_timer(selected_mode, int(minutes))
            st.rerun()

        if pause_col.button(text["pause_timer"]):
            pause_timer()
            st.rerun()

        if reset_col.button(text["reset_timer"]):
            reset_timer()
            st.rerun()

        if save_col.button(text["save_focus"]):
            save_focus_session(
                course_name=course_name,
                mode=st.session_state.focus_mode or selected_mode,
                minutes=max(1, round(elapsed_seconds / 60)),
                note=note,
            )
            reset_timer()
            st.rerun()

        if st.session_state.focus_running:
            st.caption(text["timer_running_hint"])
            if st.button(text["refresh_timer"]):
                st.rerun()

        if (
            st.session_state.focus_duration_seconds > 0
            and remaining_seconds == 0
            and st.session_state.focus_running
        ):
            save_focus_session(
                course_name=course_name,
                mode=st.session_state.focus_mode,
                minutes=round(st.session_state.focus_duration_seconds / 60),
                note=note,
            )
            reset_timer()
            st.success(text["focus_completed"])
            st.rerun()

    with log_col:
        st.markdown(f"#### {text['focus_log']}")
        if st.session_state.focus_log:
            log_df = pd.DataFrame(st.session_state.focus_log)
            localized_log_df = localize_focus_log(log_df, text)
            st.dataframe(localized_log_df, use_container_width=True, hide_index=True)
            st.metric(text["total_focus_minutes"], int(log_df["Minutes"].sum()))
            csv_data = localized_log_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label=text["download_focus_log"],
                data=csv_data,
                file_name="focus_log.csv",
                mime="text/csv",
            )
        else:
            st.info(text["empty_focus_log"])


def init_focus_state() -> None:
    """Initialize Pomodoro session state values."""
    defaults = {
        "focus_running": False,
        "focus_started_at": 0.0,
        "focus_elapsed_before_pause": 0.0,
        "focus_duration_seconds": 0,
        "focus_mode": "",
        "focus_log": [],
        "focus_screen_active": False,
        "language": "English",
        "last_course_name": "",
        "last_raw_tasks": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_timer(mode: str, minutes: int) -> None:
    """Start a new timer or resume the current timer."""
    if st.session_state.focus_duration_seconds == 0:
        st.session_state.focus_duration_seconds = minutes * 60
        st.session_state.focus_elapsed_before_pause = 0.0
        st.session_state.focus_mode = mode

    st.session_state.focus_started_at = time.time()
    st.session_state.focus_running = True


def pause_timer() -> None:
    """Pause the running timer and keep elapsed time."""
    if not st.session_state.focus_running:
        return

    elapsed_since_start = time.time() - st.session_state.focus_started_at
    st.session_state.focus_elapsed_before_pause += elapsed_since_start
    st.session_state.focus_running = False


def reset_timer() -> None:
    """Reset the current timer without clearing the focus log."""
    st.session_state.focus_running = False
    st.session_state.focus_started_at = 0.0
    st.session_state.focus_elapsed_before_pause = 0.0
    st.session_state.focus_duration_seconds = 0
    st.session_state.focus_mode = ""


def calculate_timer_seconds() -> tuple:
    """Return remaining and elapsed seconds for the current timer."""
    elapsed_seconds = st.session_state.focus_elapsed_before_pause
    if st.session_state.focus_running:
        elapsed_seconds += time.time() - st.session_state.focus_started_at

    duration_seconds = st.session_state.focus_duration_seconds
    remaining_seconds = max(0, int(duration_seconds - elapsed_seconds))
    return remaining_seconds, elapsed_seconds


def calculate_progress(elapsed_seconds: float, duration_seconds: int) -> float:
    """Return a value between 0 and 1 for the Streamlit progress bar."""
    if duration_seconds <= 0:
        return 0.0
    return min(1.0, elapsed_seconds / duration_seconds)


def save_focus_session(course_name: str, mode: str, minutes: int, note: str) -> None:
    """Save one focus session to the in-memory session log."""
    st.session_state.focus_log.append(
        {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Course": course_name,
            "Mode": mode,
            "Minutes": minutes,
            "Note": note,
        }
    )


def format_seconds(total_seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes, seconds = divmod(max(0, int(total_seconds)), 60)
    return f"{minutes:02d}:{seconds:02d}"


def localize_focus_log(log_df, text: dict):
    """Translate focus log values and column names."""
    localized_df = log_df.copy()
    localized_df["Mode"] = localized_df["Mode"].map(
        lambda value: translate_value(text, "pomodoro_modes", value)
    )
    return localized_df.rename(columns=text["focus_log_columns"])


def show_summary(summary: dict, text: dict) -> None:
    """Display the most important calculated values as metrics."""
    add_module_spacer()
    add_anchor("study-plan")
    st.subheader(text["summary"])
    metric_cols = st.columns(5)
    metric_cols[0].metric(text["days_until_exam"], summary["days_until_exam"])
    metric_cols[1].metric(text["study_days"], summary["available_study_days"])
    metric_cols[2].metric(text["tasks"], summary["total_tasks"])
    metric_cols[3].metric(text["available_hours"], summary["total_available_hours"])
    metric_cols[4].metric(text["status"], translate_value(text, "status_values", summary["status"]))


def show_plan(plan_df, text: dict) -> None:
    """Render the generated plan and offer a CSV download."""
    localized_df = localize_plan(plan_df, text)

    st.subheader(text["daily_plan"])
    st.dataframe(localized_df, use_container_width=True, hide_index=True)

    csv_data = localized_df.to_csv(index=False).encode("utf-8-sig")
    ics_data = build_icalendar(plan_df).encode("utf-8")

    download_col_csv, download_col_calendar = st.columns([1, 1])
    download_col_csv.download_button(
        label=text["download_csv"],
        data=csv_data,
        file_name="study_plan.csv",
        mime="text/csv",
    )
    download_col_calendar.download_button(
        label=text.get("download_ics", "Download iCalendar"),
        data=ics_data,
        file_name="study_plan.ics",
        mime="text/calendar",
    )


def show_advice(
    api_key: str,
    course_name: str,
    difficulty: str,
    raw_tasks: str,
    summary: dict,
    text: dict,
) -> None:
    """Show rule-based advice and optional AI-generated advice."""
    st.subheader(text["study_advice"])

    for item in build_localized_advice(summary, difficulty, text):
        st.write(f"- {item}")

    if api_key:
        with st.spinner(text["ai_spinner"]):
            ai_advice = generate_ai_advice(
                api_key=api_key,
                course_name=course_name,
                difficulty=difficulty,
                tasks=clean_tasks(raw_tasks),
                summary=summary,
            )
        st.markdown(f"#### {text['ai_suggestions']}")
        st.write(ai_advice)


def translate_value(text: dict, group: str, value: str) -> str:
    """Translate a planner value while keeping the original as fallback."""
    return text[group].get(value, value)


def build_icalendar(plan_df) -> str:
    """Create an iCalendar file from the generated study plan."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Study Planner//Study Plan//EN",
        "CALSCALE:GREGORIAN",
    ]
    created_at = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    for _, row in plan_df.iterrows():
        start_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
        start_dt = datetime.combine(start_date, datetime_time(hour=9))
        duration_hours = float(row["Planned Hours"])
        end_dt = start_dt + timedelta(minutes=int(duration_hours * 60))

        summary = f"{row['Course']} study session"
        description = f"Tasks: {row['Tasks']}\\nFocus: {row['Focus']}"

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid4()}@ai-study-planner",
                f"DTSTAMP:{created_at}",
                f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{escape_ical_text(summary)}",
                f"DESCRIPTION:{escape_ical_text(description)}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def escape_ical_text(value: str) -> str:
    """Escape text values for a simple iCalendar file."""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def localize_plan(plan_df, text: dict):
    """Translate plan table values and column names for display and CSV export."""
    localized_df = plan_df.copy()
    localized_df["Focus"] = localized_df["Focus"].map(
        lambda value: translate_value(text, "focus_values", value)
    )
    localized_df["Day Type"] = localized_df["Day Type"].map(
        lambda value: translate_value(text, "day_type_values", value)
    )
    return localized_df.rename(columns=text["columns"])


def build_localized_advice(summary: dict, difficulty: str, text: dict) -> list:
    """Create localized rule-based advice without using an external API."""
    advice_text = text["advice"]
    advice = [
        advice_text["start_important"],
        advice_text["active_recall"],
        advice_text["last_two_days"],
    ]

    if summary.get("status") == "Tight schedule":
        advice.append(advice_text["tight"])

    if difficulty == "Hard":
        advice.append(advice_text["hard"])

    if summary.get("has_weekend_plan"):
        advice.append(advice_text["weekend"])

    return advice


if __name__ == "__main__":
    main()
