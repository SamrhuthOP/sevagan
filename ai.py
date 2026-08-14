
# ============================================================
# SEVAGAN — Gemini AI Layer
# ============================================================

import json
import os

from google import genai
from google.genai import types


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """
You are SevaganAI, the friendly academic AI assistant inside
SEVAGAN — a student academic companion.

Your job is to help students:
- understand school subjects
- clarify doubts
- explain concepts clearly
- summarize study material
- analyze academic performance
- suggest practical ways to improve
- create revision plans
- discuss homework and exam preparation

The student may be studying under the CBSE curriculum.

IMPORTANT:
- Keep explanations appropriate for school students.
- Be encouraging but honest.
- Do not simply give an answer when teaching the student
  would be more useful; explain the reasoning clearly.
- Never pretend that you know information that was not provided.
- When analyzing marks, focus on patterns and improvement.
- Do not shame students for low marks.
- Keep responses organized and easy to read.
"""


# ------------------------------------------------------------
# Gemini client
# ------------------------------------------------------------

def get_api_key():
    """
    Get the Gemini API key.

    Streamlit deployment can provide GEMINI_API_KEY through
    Streamlit secrets or an environment variable.
    """

    try:
        import streamlit as st

        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


def get_client():
    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "Gemini API key is not configured. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


# ------------------------------------------------------------
# Basic AI response
# ------------------------------------------------------------

def ask_gemini(prompt):
    """
    Send a normal text question to Gemini.
    """

    if not prompt or not prompt.strip():
        return "Please enter a question."

    client = get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt.strip(),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=1200,
        ),
    )

    if not response.text:
        return "I couldn't generate a response right now."

    return response.text.strip()


# ------------------------------------------------------------
# AI chat with history
# ------------------------------------------------------------

def chat_with_gemini(
    messages,
    new_message,
    attachment_bytes=None,
    attachment_mime=None,
):
    """
    Send a message to Gemini while including previous chat
    messages.

    messages format:

    [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]

    Optional attachment:
        attachment_bytes = file/image bytes
        attachment_mime = MIME type
    """

    if not new_message and not attachment_bytes:
        return "Please enter a question or attach a file."

    client = get_client()

    contents = []

    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    for item in messages:
        role = item.get("role")
        content = item.get("content", "")

        if not content:
            continue

        # Gemini uses "user" and "model".
        gemini_role = (
            "model"
            if role in ("assistant", "model")
            else "user"
        )

        contents.append(
            types.Content(
                role=gemini_role,
                parts=[
                    types.Part(text=str(content))
                ],
            )
        )

    # --------------------------------------------------------
    # Current message
    # --------------------------------------------------------

    current_parts = []

    if new_message:
        current_parts.append(
            types.Part(
                text=new_message.strip()
            )
        )

    # --------------------------------------------------------
    # Attachment
    # --------------------------------------------------------

    if attachment_bytes and attachment_mime:
        current_parts.append(
            types.Part.from_bytes(
                data=attachment_bytes,
                mime_type=attachment_mime,
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=current_parts,
        )
    )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=1600,
        ),
    )

    if not response.text:
        return "I couldn't generate a response right now."

    return response.text.strip()


# ------------------------------------------------------------
# Performance insights
# ------------------------------------------------------------

def generate_performance_insight(
    marks,
    student_name="Student",
):
    """
    Generate a clear academic-performance summary.

    marks should contain dictionaries/rows with:
        subject
        exam_type
        obtained
        maximum
    """

    if not marks:
        return (
            "There are not enough marks yet to generate "
            "a performance insight."
        )

    lines = []

    for mark in marks:
        try:
            obtained = float(mark["obtained"])
            maximum = float(mark["maximum"])

            if maximum <= 0:
                continue

            percentage = obtained * 100 / maximum

            lines.append(
                f"- {mark['subject']} | "
                f"{mark['exam_type']} | "
                f"{obtained:g}/{maximum:g} | "
                f"{percentage:.1f}%"
            )

        except (KeyError, TypeError, ValueError):
            continue

    if not lines:
        return "There is not enough valid mark data yet."

    prompt = f"""
Analyze the following academic records for {student_name}.

Marks:
{chr(10).join(lines)}

Give a clear student-friendly report with exactly these sections:

### Overall picture
Briefly describe the overall pattern.

### Strong areas
Mention subjects or patterns that are going well.

### Needs attention
Identify subjects or patterns that need more attention.

### What to improve
Give 3 specific and realistic actions.

### Next step
Give one simple priority for the student's next study session.

Do not shame the student.
Do not compare the student with other students.
Focus on useful improvement.
"""

    return ask_gemini(prompt)


# ------------------------------------------------------------
# File / image analysis
# ------------------------------------------------------------

def analyze_attachment(
    question,
    file_bytes,
    mime_type,
):
    """
    Ask Gemini about an uploaded image/document/PDF.

    This will power:
    - doubt clarification
    - image questions
    - study material summaries
    - homework help
    """

    if not file_bytes:
        return "No file was provided."

    if not mime_type:
        return "The file type could not be detected."

    client = get_client()

    prompt = question.strip() if question else (
        "Explain the attached study material clearly "
        "for a school student."
    )

    contents = [
        types.Part(text=prompt),
        types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type,
        ),
    ]

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=1600,
        ),
    )

    if not response.text:
        return "I couldn't analyze this file right now."

    return response.text.strip()


# ------------------------------------------------------------------------------
# Quiz question generation (NCERT Aligned)
# ------------------------------------------------------------------------------

def generate_quiz_questions(
    subject,
    topic,
    number_of_questions=10,
    class_level="Class 9",
):
    """Generate practice questions for a CBSE student based on official NCERT books."""

    number_of_questions = max(
        1,
        min(int(number_of_questions), 10),
    )

    prompt = f"""
Create exactly {number_of_questions} multiple choice practice quiz questions for a CBSE student based strictly on the official NCERT textbook for {class_level}.

Target Class: {class_level}
Subject: {subject}
Topic / Chapter: {topic}

REQUIREMENTS:
- All questions, concepts, and difficulty levels MUST strictly align with official NCERT {class_level} textbooks.
- Return ONLY a valid JSON array of objects.
- Keep questions and options concise.
- Each item MUST contain these exact keys:
  - "question": string text
  - "options": list of 4 strings (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."])
  - "correct": string matching the exact text of one of the items in options
  - "explanation": concise string brief explanation referencing NCERT concepts

Example:
[
  {{
    "question": "What is magma?",
    "options": ["A) Molten rock under Earth", "B) Solid rock", "C) Water vapor", "D) Ash"],
    "correct": "A) Molten rock under Earth",
    "explanation": "According to NCERT, magma is molten rock stored beneath the Earth's surface."
  }}
]
"""

    client = genai.Client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=4096,  # High token limit to handle all 10 full questions!
        ),
    )

    clean_text = response.text.strip()

    try:
        return json.loads(clean_text)
    except Exception as e:
        return []
