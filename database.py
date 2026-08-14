# ============================================================
# SEVAGAN — Database Layer
# ============================================================

import sqlite3
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------
# Database location
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "sevagan.db"


# ------------------------------------------------------------
# Connection
# ------------------------------------------------------------

def get_connection():
    connection = sqlite3.connect(
        DB_FILE,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ------------------------------------------------------------
# Initialize database
# ------------------------------------------------------------

def init_database():
    db = get_connection()

    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            board TEXT DEFAULT 'CBSE',
            class_name TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            exam_date TEXT,
            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER,
            exam_id INTEGER,

            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,

            obtained REAL NOT NULL,
            maximum REAL NOT NULL,

            assessment_date TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY (subject_id)
                REFERENCES subjects(id)
                ON DELETE SET NULL,

            FOREIGN KEY (exam_id)
                REFERENCES exams(id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            homework_date TEXT NOT NULL,
            subject TEXT NOT NULL,
            task TEXT NOT NULL,

            due_time TEXT,
            priority TEXT DEFAULT 'Normal',

            completed INTEGER DEFAULT 0,

            attachment_name TEXT,
            attachment_data BLOB,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            role TEXT NOT NULL,
            message TEXT NOT NULL,

            attachment_name TEXT,
            attachment_data BLOB,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,
            message TEXT NOT NULL,

            notification_type TEXT DEFAULT 'general',

            scheduled_for TEXT,
            is_read INTEGER DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            subject TEXT NOT NULL,
            topic TEXT,

            score REAL NOT NULL,
            total REAL NOT NULL,

            source TEXT DEFAULT 'NCERT',

            attempted_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ai_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            insight_type TEXT NOT NULL,
            content TEXT NOT NULL,

            generated_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );
        """
    )

    db.commit()
    db.close()


# ------------------------------------------------------------
# User functions
# ------------------------------------------------------------

def create_user(
    username,
    password_hash,
    display_name="",
    board="CBSE",
    class_name="",
):
    db = get_connection()

    try:
        cursor = db.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                display_name,
                board,
                class_name,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                display_name,
                board,
                class_name,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        db.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        db.close()


def get_user_by_username(username):
    db = get_connection()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    db.close()

    return user


def get_user_by_id(user_id):
    db = get_connection()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    db.close()

    return user


# ------------------------------------------------------------
# Subjects
# ------------------------------------------------------------

def add_subject(user_id, name):
    db = get_connection()

    try:
        db.execute(
            """
            INSERT OR IGNORE INTO subjects
            (user_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                name.strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        db.commit()

    finally:
        db.close()


def get_subjects(user_id):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM subjects
        WHERE user_id = ?
        ORDER BY name
        """,
        (user_id,),
    ).fetchall()

    db.close()

    return rows


# ------------------------------------------------------------
# Marks
# ------------------------------------------------------------

def add_mark(
    user_id,
    subject,
    exam_type,
    obtained,
    maximum,
    assessment_date,
):
    if maximum <= 0:
        raise ValueError("Maximum marks must be greater than zero.")

    if obtained < 0:
        raise ValueError("Obtained marks cannot be negative.")

    if obtained > maximum:
        raise ValueError(
            "Obtained marks cannot exceed maximum marks."
        )

    add_subject(user_id, subject)

    db = get_connection()

    db.execute(
        """
        INSERT INTO marks (
            user_id,
            subject,
            exam_type,
            obtained,
            maximum,
            assessment_date,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            subject.strip(),
            exam_type.strip(),
            obtained,
            maximum,
            assessment_date,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_marks(user_id):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM marks
        WHERE user_id = ?
        ORDER BY assessment_date DESC, id DESC
        """,
        (user_id,),
    ).fetchall()

    db.close()

    return rows


def delete_mark(user_id, mark_id):
    db = get_connection()

    db.execute(
        """
        DELETE FROM marks
        WHERE id = ?
        AND user_id = ?
        """,
        (mark_id, user_id),
    )

    db.commit()
    db.close()


# ------------------------------------------------------------
# Homework
# ------------------------------------------------------------

def add_homework(
    user_id,
    homework_date,
    subject,
    task,
    due_time=None,
    priority="Normal",
    attachment_name=None,
    attachment_data=None,
):
    add_subject(user_id, subject)

    db = get_connection()

    db.execute(
        """
        INSERT INTO homework (
            user_id,
            homework_date,
            subject,
            task,
            due_time,
            priority,
            completed,
            attachment_name,
            attachment_data,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        """,
        (
            user_id,
            homework_date,
            subject.strip(),
            task.strip(),
            due_time,
            priority,
            attachment_name,
            attachment_data,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_homework_for_date(user_id, homework_date):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM homework
        WHERE user_id = ?
        AND homework_date = ?
        ORDER BY id DESC
        """,
        (
            user_id,
            homework_date,
        ),
    ).fetchall()

    db.close()

    return rows


def get_all_homework(user_id):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM homework
        WHERE user_id = ?
        ORDER BY homework_date DESC, id DESC
        """,
        (user_id,),
    ).fetchall()

    db.close()

    return rows


def complete_homework(user_id, homework_id):
    db = get_connection()

    db.execute(
        """
        UPDATE homework
        SET completed = 1
        WHERE id = ?
        AND user_id = ?
        """,
        (
            homework_id,
            user_id,
        ),
    )

    db.commit()
    db.close()


def delete_homework(user_id, homework_id):
    db = get_connection()

    db.execute(
        """
        DELETE FROM homework
        WHERE id = ?
        AND user_id = ?
        """,
        (
            homework_id,
            user_id,
        ),
    )

    db.commit()
    db.close()


# ------------------------------------------------------------
# AI chat history
# ------------------------------------------------------------

def save_chat_message(
    user_id,
    role,
    message,
    attachment_name=None,
    attachment_data=None,
):
    db = get_connection()

    db.execute(
        """
        INSERT INTO chat_messages (
            user_id,
            role,
            message,
            attachment_name,
            attachment_data,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            role,
            message,
            attachment_name,
            attachment_data,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_chat_history(user_id, limit=50):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM chat_messages
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_id,
            limit,
        ),
    ).fetchall()

    db.close()

    return list(reversed(rows))


def clear_chat_history(user_id):
    db = get_connection()

    db.execute(
        """
        DELETE FROM chat_messages
        WHERE user_id = ?
        """,
        (user_id,),
    )

    db.commit()
    db.close()


# ------------------------------------------------------------
# Notifications
# ------------------------------------------------------------

def add_notification(
    user_id,
    title,
    message,
    notification_type="general",
    scheduled_for=None,
):
    db = get_connection()

    db.execute(
        """
        INSERT INTO notifications (
            user_id,
            title,
            message,
            notification_type,
            scheduled_for,
            is_read,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, 0, ?)
        """,
        (
            user_id,
            title,
            message,
            notification_type,
            scheduled_for,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_notifications(user_id):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()

    db.close()

    return rows


def mark_notification_read(user_id, notification_id):
    db = get_connection()

    db.execute(
        """
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
        AND user_id = ?
        """,
        (
            notification_id,
            user_id,
        ),
    )

    db.commit()
    db.close()


# ------------------------------------------------------------
# Quiz history
# ------------------------------------------------------------

def save_quiz_attempt(
    user_id,
    subject,
    topic,
    score,
    total,
    source="NCERT",
):
    db = get_connection()

    db.execute(
        """
        INSERT INTO quiz_attempts (
            user_id,
            subject,
            topic,
            score,
            total,
            source,
            attempted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            subject,
            topic,
            score,
            total,
            source,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_quiz_attempts(user_id):
    db = get_connection()

    rows = db.execute(
        """
        SELECT *
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY attempted_at DESC
        """,
        (user_id,),
    ).fetchall()

    db.close()
    return rows

def clear_quiz_attempts(user_id):
    db = get_connection()
    db.execute(
        """
        DELETE FROM quiz_attempts
        WHERE user_id = ?
        """,
        (user_id,),
    )
    db.commit()
    db.close()


# ------------------------------------------------------------
# AI insights
# ------------------------------------------------------------

def save_ai_insight(
    user_id,
    insight_type,
    content,
):
    db = get_connection()

    db.execute(
        """
        INSERT INTO ai_insights (
            user_id,
            insight_type,
            content,
            generated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            insight_type,
            content,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    db.commit()
    db.close()


def get_latest_ai_insight(user_id, insight_type=None):
    db = get_connection()

    if insight_type:
        row = db.execute(
            """
            SELECT *
            FROM ai_insights
            WHERE user_id = ?
            AND insight_type = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                insight_type,
            ),
        ).fetchone()
    else:
        row = db.execute(
            """
            SELECT *
            FROM ai_insights
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    db.close()

    return row


# ------------------------------------------------------------
# Start database automatically
# ------------------------------------------------------------

init_database()
