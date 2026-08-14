import json
import streamlit as st
from datetime import date, datetime

from database import (
    get_user_by_id,
    get_marks,
    add_mark,
    get_subjects,
    get_homework_for_date,
    add_homework,
    complete_homework,
    delete_homework,
    save_chat_message,
    get_chat_history,
    clear_chat_history,
    save_ai_insight,
    get_latest_ai_insight,
    save_quiz_attempt,
    get_quiz_attempts,
    clear_quiz_attempts,
    add_notification,
    get_notifications,
    mark_notification_read,
)

from auth import register_user, login_user

from ai import (
    chat_with_gemini,
    generate_performance_insight,
    generate_quiz_questions,
)
from push_component import render_push_subscription_ui


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SEVAGAN — Your Academic Companion",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ============================================================
# PWA / SERVICE WORKER
# ============================================================

st.markdown(
    """
    <link rel="manifest" href="/static/manifest.json">

    <script>
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", function () {
            navigator.serviceWorker.register("/static/service-worker.js")
                .then(function (registration) {
                    console.log("SEVAGAN service worker registered.");
                })
                .catch(function (error) {
                    console.error(
                        "SEVAGAN service worker registration failed:",
                        error
                    );
                });
        });
    }
    </script>
    """,
    unsafe_allow_html=True,
)

# Deep Navy + Soft Blue theme.
# This CSS is only for styling; all visible content below uses
# Streamlit's native rendering so HTML/code cannot leak onto the page.
st.markdown(
    """
    <style>
        :root {
            --navy-1: #07111f;
            --navy-2: #0b1728;
            --navy-3: #10233b;
            --blue: #6ea8ff;
            --blue-2: #8bbcff;
            --text: #f3f7ff;
            --muted: #9aaac0;
            --border: rgba(139, 188, 255, 0.16);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(76, 132, 220, 0.18), transparent 28%),
                radial-gradient(circle at 95% 5%, rgba(61, 105, 177, 0.14), transparent 30%),
                var(--navy-1);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 17, 31, 0.82);
        }

        [data-testid="stSidebar"] {
            background: var(--navy-2);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: var(--text) !important;
        }

        p, label, .stCaption, [data-testid="stMarkdownContainer"] {
            color: var(--text);
        }

        .hero-title {
            font-size: clamp(30px, 5vw, 46px);
            font-weight: 800;
            letter-spacing: -0.8px;
            margin-bottom: 0.15rem;
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 0.92rem;
            margin-bottom: 1.4rem;
        }

        .brand-title {
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 0.76rem;
        }

        .metric-card {
            background: linear-gradient(145deg, var(--navy-3), var(--navy-2));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
            min-height: 125px;
            box-shadow: 0 14px 32px rgba(0, 0, 0, 0.18);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.70rem;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .metric-value {
            color: var(--text);
            font-size: 1.9rem;
            font-weight: 800;
            margin: 5px 0;
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.76rem;
        }

        .soft-card {
            background: rgba(16, 35, 59, 0.72);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
            margin: 7px 0;
        }

        .soft-card strong {
            color: var(--text);
        }

        .section-heading {
            color: var(--text);
            font-size: 1.25rem;
            font-weight: 800;
            margin: 1.35rem 0 0.65rem;
        }

        .blue-text {
            color: var(--blue-2);
            font-weight: 800;
        }

        .ai-box {
            background: linear-gradient(145deg, #102744, #0c1b2f);
            border: 1px solid rgba(110, 168, 255, 0.25);
            border-radius: 18px;
            padding: 18px;
        }

        .auth-wrap {
            max-width: 560px;
            margin: 7vh auto 0;
        }

        .footer-text {
            color: #71829a;
            text-align: center;
            font-size: 0.72rem;
            padding: 2.5rem 0 1rem;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 11px;
            min-height: 44px;
            font-weight: 700;
            border: 1px solid rgba(139, 188, 255, 0.20);
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: rgba(139, 188, 255, 0.55);
        }

        input, textarea, [data-baseweb="select"] > div {
            border-radius: 10px !important;
        }

        [data-testid="stFileUploader"] {
            border-radius: 12px;
        }

        @media (max-width: 700px) {
            .block-container {
                padding: 0.75rem 0.85rem 1.5rem;
            }

            .hero-title {
                font-size: 31px;
            }

            .metric-card {
                min-height: 105px;
                padding: 14px;
            }

            .metric-value {
                font-size: 1.55rem;
            }

            .section-heading {
                font-size: 1.12rem;
            }

            .stButton > button,
            .stFormSubmitButton > button {
                min-height: 46px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"


# ============================================================
# HELPERS
# ============================================================

def logout():
    st.session_state.user_id = None
    st.session_state.page = "🏠 Dashboard"
    st.rerun()


def percentage(obtained, maximum):
    if float(maximum) <= 0:
        return 0.0
    return float(obtained) * 100 / float(maximum)


def overall_percentage(rows):
    if not rows:
        return 0.0
    obtained = sum(float(row["obtained"]) for row in rows)
    maximum = sum(float(row["maximum"]) for row in rows)
    return percentage(obtained, maximum)


def today_string():
    return date.today().isoformat()


def get_user_marks():
    return get_marks(st.session_state.user_id)


def get_today_homework():
    return get_homework_for_date(
        st.session_state.user_id,
        today_string(),
    )


def show_page_header(title, subtitle):
    st.markdown(f"# {title}")
    st.caption(subtitle)


def show_metric(label, value, note):
    st.markdown(
        f"**{label}**\n\n### {value}\n\n{note}"
    )


def safe_text(value, fallback=""):
    if value is None:
        return fallback
    return str(value)


# ============================================================
# AUTHENTICATION
# ============================================================

if st.session_state.user_id is None:
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown("# 🔱 SEVAGAN")
    st.caption("Your Academic Companion · மாணவர்களின் கல்வித் துணையாளர்")

    login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="e.g. samrhuth",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="e.g. Enter your password",
            )

            submitted = st.form_submit_button(
                "Login to SEVAGAN",
                use_container_width=True,
            )

            if submitted:
                success, message, user = login_user(
                    username.strip(),
                    password,
                )

                if success:
                    st.session_state.user_id = user["id"]
                    st.session_state.page = "🏠 Dashboard"
                    st.rerun()
                else:
                    st.error(message)

    with signup_tab:
        with st.form("signup_form"):
            display_name = st.text_input(
                "Your Name",
                placeholder="e.g. Samrhuth",
            )
            username = st.text_input(
                "Choose Username",
                placeholder="e.g. samrhuth",
            )
            class_name = st.text_input(
                "Class",
                placeholder="e.g. IX-B",
            )
            board = st.selectbox("Board", ["CBSE"])
            password = st.text_input(
                "Create Password",
                type="password",
                placeholder="e.g. Create a secure password",
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="e.g. Re-enter your password",
            )

            submitted = st.form_submit_button(
                "Create My Account",
                use_container_width=True,
            )

            if submitted:
                if not display_name.strip():
                    st.warning("Please enter your name.")
                elif not username.strip():
                    st.warning("Please enter a username.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message, _ = register_user(
                        username=username.strip(),
                        password=password,
                        display_name=display_name.strip(),
                        board=board,
                        class_name=class_name.strip(),
                    )

                    if success:
                        st.success(
                            "Account created successfully! Open the Login tab."
                        )
                    else:
                        st.error(message)

    st.markdown("---")
    st.caption("🔱 SEVAGAN · Your Academic Companion")
    st.caption("Crafted by **Samrhuth S.P · IX-B**")
    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

user_id = st.session_state.user_id
user = get_user_by_id(user_id)

if user is None:
    st.session_state.user_id = None
    st.rerun()

display_name = user["display_name"] or user["username"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 🔱 SEVAGAN")
    st.caption("Your Academic Companion")
    st.caption(f"Signed in as **@{user['username']}**")
    st.divider()

    pages = [
        "🏠 Dashboard",
        "📝 Homework",
        "📊 Marks & Performance",
        "💡 SevaganAI",
        "🧠 Quizzes",
        "🔔 Notifications",
        "⚙️ Account",
    ]

    selected_page = st.radio(
        "NAVIGATION",
        pages,
        index=pages.index(st.session_state.page)
        if st.session_state.page in pages
        else 0,
    )
    st.session_state.page = selected_page

    st.divider()

    if st.button("🚪 Log out", use_container_width=True):
        logout()


# ============================================================
# DASHBOARD
# ============================================================

if selected_page == "🏠 Dashboard":
    marks = get_user_marks()
    homework = get_today_homework()
    subjects = get_subjects(user_id)
    notifications = get_notifications(user_id)

    overall = overall_percentage(marks)
    completed = sum(1 for row in homework if row["completed"])
    unread = sum(1 for n in notifications if not n["is_read"])

    show_page_header(
        f"Good day, {display_name}. 👋",
        f"{date.today().strftime('%A, %d %B %Y')} · Your academic overview",
    )

    # ✅ PASTE THIS TABLE CARD INSTEAD:
    table_html = f"""
    <div style="background-color: #0e1b2e; border-radius: 12px; padding: 18px; border: 1px solid #1e2d42; margin: 15px 0 25px 0;">
        <table style="width: 100%; text-align: center; border-collapse: collapse; font-family: sans-serif;">
            <thead>
                <tr style="border-bottom: 1px solid #1e2d42; color: #8a99ad; font-size: 12px; letter-spacing: 0.8px; text-transform: uppercase;">
                    <th style="padding: 10px;">Overall Performance</th>
                    <th style="padding: 10px;">Today's Homework</th>
                    <th style="padding: 10px;">Subjects</th>
                    <th style="padding: 10px;">Notifications</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding-top: 14px; font-size: 28px; font-weight: bold; color: #ffffff;">{overall:.1f}%</td>
                    <td style="padding-top: 14px; font-size: 28px; font-weight: bold; color: #ffffff;">{completed}/{len(homework)}</td>
                    <td style="padding-top: 14px; font-size: 28px; font-weight: bold; color: #ffffff;">{len(subjects)}</td>
                    <td style="padding-top: 14px; font-size: 28px; font-weight: bold; color: #ffffff;">{unread}</td>
                </tr>
                <tr style="color: #6b7a90; font-size: 11px;">
                    <td style="padding-bottom: 10px;">Recorded assessments</td>
                    <td style="padding-bottom: 10px;">Tasks completed</td>
                    <td style="padding-bottom: 10px;">Your subjects</td>
                    <td style="padding-bottom: 10px;">Unread</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown("## 📚 My Subjects")
    if subjects:
        cols = st.columns(min(max(len(subjects), 1), 4))
        for index, subject in enumerate(subjects):
            subject_name = safe_text(subject["name"], "Subject")
            with cols[index % len(cols)]:
                st.info(f"📘 **{subject_name}**")
    else:
        st.info("Your subjects will appear here after you add marks or homework.")

    st.markdown("## 📝 Today's Homework")
    if not homework:
        st.success("Your homework list is clear. 🎉")
    else:
        for row in homework:
            left, right = st.columns([6, 1])
            with left:
                status = "✅ Completed" if row["completed"] else "⏳ Pending"
                st.info(
                    f"**{row['subject']}**\n\n"
                    f"{row['task']}\n\n"
                    f"{status} · {row['due_time'] or 'No time'}"
                )
            with right:
                if not row["completed"] and st.button(
                    "✓ Done", key=f"dash_done_{row['id']}", use_container_width=True
                ):
                    complete_homework(user_id, row["id"])
                    st.rerun()

    st.markdown("## 📈 SevaganAI Insight")
    latest = get_latest_ai_insight(user_id, "performance")

    if latest:
        st.success(latest["content"])
    elif marks:
        if st.button("💡 SevaganAI Generate My AI Insight", use_container_width=True):
            with st.spinner("SevaganAI is analyzing your performance..."):
                insight = generate_performance_insight(marks, display_name)
            save_ai_insight(user_id, "performance", insight)
            st.rerun()
    else:
        st.info(
            "Add your marks and SevaganAI will identify your strengths "
            "and what you can improve."
        )


# ============================================================
# HOMEWORK
# ============================================================

elif selected_page == "📝 Homework":
    show_page_header(
        "Homework 📝",
        "Keep today's tasks organized and attach study material when needed.",
    )

    st.markdown("## ➕ Add Today's Homework")

    with st.form("homework_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            subject = st.text_input("Subject", placeholder="e.g. Mathematics")
            task = st.text_area(
                "Homework",
                placeholder="e.g. Complete Exercise 5.2, Questions 1–10",
            )

        with c2:
            due_time = st.time_input(
                "Reminder time",
                value=datetime.strptime("18:00", "%H:%M").time(),
            )
            priority = st.selectbox(
                "Priority",
                ["Normal", "Important", "High"],
            )

        attachment = st.file_uploader(
            "📎 Attach an image or file (optional)",
            type=["png", "jpg", "jpeg", "pdf", "txt", "docx"],
        )

        submit = st.form_submit_button(
            "➕ Add Homework",
            use_container_width=True,
        )

        if submit:
            if not subject.strip() or not task.strip():
                st.warning("Please enter both the subject and homework.")
            else:
                attachment_name = attachment.name if attachment else None
                attachment_data = attachment.getvalue() if attachment else None

                add_homework(
                    user_id=user_id,
                    homework_date=today_string(),
                    subject=subject.strip(),
                    task=task.strip(),
                    due_time=due_time.strftime("%H:%M"),
                    priority=priority,
                    attachment_name=attachment_name,
                    attachment_data=attachment_data,
                )

                add_notification(
                    user_id=user_id,
                    title="Homework reminder",
                    message=f"{subject.strip()}: {task.strip()}",
                    notification_type="homework",
                    scheduled_for=(
                        f"{today_string()} {due_time.strftime('%H:%M')}"
                    ),
                )

                st.success("Homework added successfully. 🔱")
                st.rerun()

    st.markdown("## 📋 Today")
    homework = get_today_homework()

    if not homework:
        st.info("No homework for today.")

    for row in homework:
        left, right = st.columns([6, 1])
        with left:
            status = "✅ Completed" if row["completed"] else "⏳ Pending"
            attachment_text = (
                f" · 📎 {row['attachment_name']}"
                if row["attachment_name"]
                else ""
            )
            st.info(
                f"**{row['subject']}**\n\n"
                f"{row['task']}\n\n"
                f"{status} · Due {row['due_time'] or 'not set'}{attachment_text}"
            )
        with right:
            if not row["completed"] and st.button(
                "✓ Done", key=f"hw_done_{row['id']}", use_container_width=True
            ):
                complete_homework(user_id, row["id"])
                st.rerun()

            if st.button(
                "🗑️ Delete", key=f"hw_delete_{row['id']}", use_container_width=True
            ):
                delete_homework(user_id, row["id"])
                st.rerun()


# ============================================================
# MARKS & PERFORMANCE
# ============================================================

elif selected_page == "📊 Marks & Performance":
    show_page_header(
        "Marks & Performance 📊",
        "Record assessments and let SevaganAI identify strengths and areas to improve.",
    )

    st.markdown("## ➕ Add Marks")

    with st.form("mark_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            subject = st.text_input("Subject", placeholder="e.g. Science")
            exam_type = st.text_input(
                "Exam / Assessment Type",
                placeholder="e.g. Unit Test 1",
            )
        with c2:
            obtained = st.number_input(
                "Marks Obtained", min_value=0.0, step=1.0
            )
            maximum = st.number_input(
                "Maximum Marks", min_value=1.0, value=100.0, step=1.0
            )

        assessment_date = st.date_input(
            "Assessment Date", value=date.today()
        )

        save = st.form_submit_button("💾 Save Marks", use_container_width=True)

        if save:
            if not subject.strip():
                st.warning("Please enter a subject.")
            elif not exam_type.strip():
                st.warning("Please enter the exam type.")
            elif obtained > maximum:
                st.error("Marks obtained cannot exceed maximum marks.")
            else:
                add_mark(
                    user_id=user_id,
                    subject=subject.strip(),
                    exam_type=exam_type.strip(),
                    obtained=obtained,
                    maximum=maximum,
                    assessment_date=assessment_date.isoformat(),
                )
                st.success(f"Saved: {percentage(obtained, maximum):.1f}%")
                st.rerun()

    marks = get_user_marks()
    overall = overall_percentage(marks)
    unique_subjects = {row["subject"] for row in marks}

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Overall", f"{overall:.1f}%")
    with c2:
        st.metric("Assessments", len(marks))
    with c3:
        st.metric("Subjects", len(unique_subjects))

    st.markdown("## 📚 Subject Breakdown")
    if not unique_subjects:
        st.info("Add your first assessment to see subject performance.")

    for subject in sorted(unique_subjects):
        subject_marks = [row for row in marks if row["subject"] == subject]
        score = overall_percentage(subject_marks)
        st.progress(min(score, 100.0) / 100.0)
        st.caption(f"**{subject}** · {score:.1f}%")

    if marks:
        st.markdown("## 🤖 SevaganAI Analysis")
        if st.button("📈 Analyze My Performance", use_container_width=True):
            with st.spinner("SevaganAI is analyzing your marks..."):
                insight = generate_performance_insight(marks, display_name)
            save_ai_insight(user_id, "performance", insight)
            st.success("Analysis generated.")
            st.write(insight)

    st.markdown("## 📋 Assessment History")
    if not marks:
        st.info("No assessments recorded yet.")

    for row in marks:
        score = percentage(float(row["obtained"]), float(row["maximum"]))
        st.info(
            f"**{row['subject']} — {row['exam_type']}**\n\n"
            f"{row['obtained']:g}/{row['maximum']:g} · {score:.1f}%\n\n"
            f"{row['assessment_date']}"
        )


# ============================================================
# SEVAGANAI
# ============================================================

elif selected_page == "💡 SevaganAI":
    show_page_header(
        "💡 SevaganAI",
        "Clarify doubts, explain concepts, and analyze attached study material.",
    )

    st.info(
        "💬 **Your AI Academic Companion**\n\n"
        "Ask a doubt or attach an image, PDF, or study file for analysis."
    )

    history = get_chat_history(user_id, limit=50)

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    for message in history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["message"])

                if (
                    "attachment_name" in message.keys()
                    and message["attachment_name"]
                ):
                    st.caption(f"📎 {message['attachment_name']}")

        else:
            with st.chat_message("assistant"):
                st.write(message["message"])

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    clear_col1, clear_col2 = st.columns([5, 1])

    with clear_col2:
        if st.button(
            "🗑️ Clear",
            use_container_width=True,
            help="Clear your SevaganAI chat history",
        ):
            clear_chat_history(user_id)
            st.rerun()

    # --------------------------------------------------------
    # CHAT INPUT + ATTACHMENT
    # --------------------------------------------------------

    submission = st.chat_input(
        "Ask SevaganAI a doubt...",
        accept_file=True,
        file_type=["png", "jpg", "jpeg", "pdf", "txt", "docx"],
    )

    if submission:
        prompt = submission.text.strip()

        attachment = None
        attachment_bytes = None
        attachment_mime = None
        attachment_name = None

        # Get attached file if one was selected
        if submission.files:
            attachment = submission.files[0]

            attachment_bytes = attachment.getvalue()
            attachment_mime = attachment.type
            attachment_name = attachment.name

        # If neither text nor file was provided, do nothing
        if not prompt and not attachment:
            st.warning("Please type a question or attach a file.")
            st.stop()

        # ----------------------------------------------------
        # SAVE USER MESSAGE
        # ----------------------------------------------------

        save_chat_message(
            user_id=user_id,
            role="user",
            message=prompt or "Please analyze my attachment.",
            attachment_name=attachment_name,
            attachment_data=attachment_bytes,
        )

        # ----------------------------------------------------
        # SEND TO GEMINI
        # ----------------------------------------------------

        with st.spinner("SevaganAI is thinking..."):
            try:
                previous_messages = [
                    {
                        "role": row["role"],
                        "content": row["message"],
                    }
                    for row in history
                ]

                answer = chat_with_gemini(
                    messages=previous_messages,
                    new_message=prompt or "Analyze the attached file.",
                    attachment_bytes=attachment_bytes,
                    attachment_mime=attachment_mime,
                )

            except Exception:
                answer = (
                    "I couldn't connect to the AI service right now. "
                    "Please check your AI API configuration."
                )

        # ----------------------------------------------------
        # SAVE AI RESPONSE
        # ----------------------------------------------------

        save_chat_message(
            user_id=user_id,
            role="assistant",
            message=answer,
        )

        st.rerun()
        
# ==============================================================================
# QUIZZES
# ==============================================================================

elif selected_page == "🧠 Quizzes":
    show_page_header(
        "NCERT Class-Wise Quizzes 🧠",
        "Practice NCERT concepts class-wise and keep a record of your quiz attempts.",
    )

    # --- 1. QUIZ GENERATION INPUTS ---
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        class_level = st.selectbox(
            "Class",
            [f"Class {i}" for i in range(6, 13)],
            index=3,  # Default: Class 9
        )
    with c2:
        subject = st.text_input("Subject", placeholder="e.g. Science")
    with c3:
        topic = st.text_input("Topic", placeholder="e.g. Matter in Our Surroundings")

    number = st.slider("Number of questions", 1, 10, 5)

    if st.button("🧪 Generate Quiz", use_container_width=True):
        if not subject.strip() or not topic.strip():
            st.warning("Enter both subject and topic.")
        else:
            with st.spinner(f"Creating your {class_level} NCERT quiz..."):
                try:
                    quiz = generate_quiz_questions(
                        subject=subject.strip(),
                        topic=topic.strip(),
                        number_of_questions=number,
                        class_level=class_level,
                    )
                    st.session_state.generated_quiz = quiz
                    st.session_state.quiz_class = class_level
                    st.session_state.quiz_subject = subject.strip()
                    st.session_state.quiz_topic = topic.strip()
                    st.session_state.quiz_number = number

                    # Reset previous quiz state flags
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_saved = False
                    st.session_state.user_answers = {}
                    st.rerun()
                except Exception as e:
                    st.error(
                        "Unable to generate the quiz. "
                        "Please check your AI configuration."
                    )

    # --- 2. ACTIVE QUIZ & EVALUATION SECTION ---
    if "generated_quiz" in st.session_state:
        st.markdown("## 📖 Your Quiz")

        quiz_data = st.session_state.generated_quiz

        # Safely convert JSON string to Python list if needed
        if isinstance(quiz_data, str):
            try:
                clean_json = (
                    quiz_data.replace("```json", "").replace("```", "").strip()
                )
                quiz_data = json.loads(clean_json)
            except Exception:
                pass

        if isinstance(quiz_data, list):
            # STEP A: Render Form with Radio Option Buttons
            if not st.session_state.get("quiz_submitted", False):
                with st.form("interactive_quiz_form"):
                    user_answers = {}

                    for idx, q in enumerate(quiz_data):
                        st.markdown(f"**Q{idx + 1}. {q['question']}**")
                        user_answers[idx] = st.radio(
                            "Choose an option:",
                            q["options"],
                            key=f"quiz_q_{idx}",
                            index=None,  # Unselected by default
                        )
                        st.write("---")

                    submitted = st.form_submit_button(
                        "Check Answers", use_container_width=True
                    )

                    if submitted:
                        st.session_state.quiz_submitted = True
                        st.session_state.user_answers = user_answers
                        st.rerun()

            # STEP B: Results & Explanations
            else:
                st.markdown("### 📊 Quiz Results")
                calculated_score = 0
                total_questions = len(quiz_data)
                user_answers = st.session_state.get("user_answers", {})

                for idx, q in enumerate(quiz_data):
                    selected = user_answers.get(idx)

                    if selected == q["correct"]:
                        calculated_score += 1
                        st.success(f"**Q{idx + 1}: Correct!** ✅")
                    else:
                        st.error(f"**Q{idx + 1}: Incorrect** ❌")
                        st.write(
                            f"**Your Answer:** {selected if selected else 'None selected'}"
                        )
                        st.write(f"**Correct Answer:** {q['correct']}")
                        st.info(f"💡 **Explanation:** {q['explanation']}")

                    st.write("---")

                # Auto-save once to database
                if not st.session_state.get("quiz_saved", False):
                    quiz_cls = st.session_state.get("quiz_class", "NCERT")
                    save_quiz_attempt(
                        user_id=user_id,
                        subject=st.session_state.quiz_subject,
                        topic=st.session_state.quiz_topic,
                        score=calculated_score,
                        total=total_questions,
                        source=f"NCERT {quiz_cls}",
                    )
                    st.session_state.quiz_saved = True

                st.success(
                    f"Saved to history! Score: {calculated_score}/{total_questions}"
                )

                if st.button(
                    "✅ Done (Move to History)", use_container_width=True
                ):
                    for key in [
                        "generated_quiz",
                        "quiz_class",
                        "quiz_submitted",
                        "quiz_saved",
                        "user_answers",
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

    # --- 3. QUIZ HISTORY & CLEAR HISTORY SECTION ---
    attempts = get_quiz_attempts(user_id)
    if attempts:
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown("## 📜 Quiz History")
        with h_col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                clear_quiz_attempts(user_id)
                st.success("Quiz history cleared!")
                st.rerun()

        for attempt in attempts:
            st.info(
                f"**{attempt['subject']} - {attempt['topic'] or 'Practice'}**\n\n"
                f"{attempt['score']}/{attempt['total']} | {attempt['source']}"
            )

# ==============================================================================
# NOTIFICATIONS
# ==============================================================================

elif selected_page == "🔔 Notifications":
    show_page_header(
        "Notifications 🔔",
        "Your homework and academic reminders.",
    )

    # 👇 Add push notification toggle button here
    render_push_subscription_ui()
    st.write("---")

    notifications = get_notifications(user_id)

    if not notifications:
        st.info("You don't have any notifications yet.")

    for notification in notifications:
        status = "• Unread" if not notification["is_read"] else "Read"
        st.info(
            f"**{notification['title']}**\n\n"
            f"{notification['message']}\n\n"
            f"{notification['scheduled_for'] or ''} · {status}"
        )

        if not notification["is_read"]:
            if st.button(
                "Mark as read",
                key=f"read_{notification['id']}",
                use_container_width=True,
            ):
                mark_notification_read(user_id, notification["id"])
                st.rerun()
                

# ============================================================
# ACCOUNT
# ============================================================

elif selected_page == "⚙️ Account":
    show_page_header(
        "Account ⚙️",
        "Your SEVAGAN student profile.",
    )

    st.markdown("## 👤 Account Information")
    st.metric("Username", f"@{user['username']}")
    st.caption(f"Account created: {user['created_at']}")

    st.markdown("## 📝 Profile Details")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(
            "Name",
            value=user["display_name"] or "",
            disabled=True,
        )
    with c2:
        st.text_input(
            "Username",
            value=user["username"] or "",
            disabled=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        st.text_input(
            "Class",
            value=user["class_name"] or "",
            disabled=True,
        )
    with c2:
        st.text_input(
            "Board",
            value=user["board"] or "CBSE",
            disabled=True,
        )

    st.info("Your profile information is currently read-only.")

    st.markdown("## 🔱 About SEVAGAN")
    st.write(
        "SEVAGAN — Your Academic Companion. A student-focused app for "
        "homework, marks, quizzes, notifications and AI-powered academic assistance."
    )
    st.caption("Board: CBSE")
    st.caption("Version: Final Model")
    st.caption("Crafted by Samrhuth S.P · IX-B")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("🔱 SEVAGAN · Your Academic Companion")
st.caption("Crafted by Samrhuth S.P · IX-B")
