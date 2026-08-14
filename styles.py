# ============================================================
# SEVAGAN — Styles
# ============================================================

import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:'
            'wght@400;500;600;700;800&display=swap'
        );

        .stApp {
            background:
                radial-gradient(
                    circle at 5% 0%,
                    rgba(36, 180, 120, .14),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 95% 0%,
                    rgba(80, 90, 180, .10),
                    transparent 28%
                ),
                #070b0d;
        }

        html,
        body,
        [class*="css"] {
            font-family: "Inter", sans-serif;
        }

        /* ==================================================
           SIDEBAR
           ================================================== */

        section[data-testid="stSidebar"] {
            background: #090e10;
            border-right: 1px solid rgba(255,255,255,.07);
        }

        /* ==================================================
           HEADINGS
           ================================================== */

        .sevagan-hero {
            font-size: 42px;
            line-height: 1.1;
            font-weight: 800;
            color: #f2f7f4;
        }

        .sevagan-subtitle {
            color: #7d8985;
            font-size: 13px;
            margin: 8px 0 26px;
        }

        .section-title {
            color: #edf4f1;
            font-size: 22px;
            font-weight: 800;
            margin: 28px 0 14px;
        }

        /* ==================================================
           CARDS
           ================================================== */

        .sevagan-card {
            background:
                linear-gradient(
                    145deg,
                    #162122,
                    #0c1415
                );

            border: 1px solid rgba(255,255,255,.07);
            border-radius: 19px;
            padding: 19px;
            margin-bottom: 10px;

            box-shadow:
                0 15px 35px rgba(0,0,0,.15);
        }

        .sevagan-item {
            background: rgba(16,25,26,.96);
            border: 1px solid rgba(255,255,255,.065);
            border-radius: 17px;
            padding: 17px;
            margin-bottom: 10px;
        }

        /* ==================================================
           TEXT
           ================================================== */

        .label {
            color: #7e8b86;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.3px;
        }

        .big-number {
            color: #f3f7f5;
            font-size: 31px;
            font-weight: 800;
            margin: 6px 0;
        }

        .muted {
            color: #75817d;
            font-size: 12px;
        }

        .green {
            color: #61d99d;
            font-weight: 800;
        }

        .gold {
            color: #f0c674;
            font-weight: 700;
        }

        /* ==================================================
           AI CHAT
           ================================================== */

        .ai-card {
            background:
                linear-gradient(
                    145deg,
                    #172526,
                    #0b1315
                );

            border: 1px solid rgba(97,217,157,.18);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 14px;
        }

        .ai-title {
            font-size: 24px;
            font-weight: 800;
            color: #f2f7f4;
        }

        .ai-subtitle {
            color: #7d8985;
            font-size: 12px;
            margin-top: 4px;
        }

        .chat-user {
            background: #172526;
            border-radius: 17px;
            padding: 14px 16px;
            margin: 8px 0 8px 12%;
        }

        .chat-ai {
            background: #10191a;
            border: 1px solid rgba(255,255,255,.06);
            border-radius: 17px;
            padding: 14px 16px;
            margin: 8px 12% 8px 0;
        }

        /* ==================================================
           AUTHENTICATION
           ================================================== */

        .auth-box {
            max-width: 520px;
            margin: 9vh auto 0;
        }

        .auth-title {
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            color: #f2f7f4;
        }

        .auth-subtitle {
            text-align: center;
            color: #77837e;
            margin-bottom: 25px;
        }

        /* ==================================================
           BUTTONS
           ================================================== */

        div.stButton > button {
            border-radius: 11px;
            font-weight: 650;
        }

        /* ==================================================
           FOOTER
           ================================================== */

        .footer {
            text-align: center;
            color: #64706c;
            font-size: 11px;
            padding: 42px 0 18px;
        }

        /* ==================================================
           PROGRESS
           ================================================== */

        .progress-background {
            height: 8px;
            background: #192322;
            border-radius: 20px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress-fill {
            height: 8px;
            background: #61d99d;
            border-radius: 20px;
        }

        /* ==================================================
           NOTIFICATION
           ================================================== */

        .notification-card {
            background: #111b1c;
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 16px;
            padding: 15px;
            margin-bottom: 9px;
        }

        .notification-title {
            color: #f0f6f3;
            font-weight: 700;
        }

        .notification-message {
            color: #7d8985;
            font-size: 12px;
            margin-top: 5px;
        }

        /* ==================================================
           MOBILE
           ================================================== */

        @media (max-width: 768px) {

            .sevagan-hero {
                font-size: 32px;
            }

            .section-title {
                font-size: 19px;
            }

            .auth-title {
                font-size: 38px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )
