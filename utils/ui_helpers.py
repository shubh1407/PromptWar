import os
import streamlit as st
from models.user_profile import UserProfile

def init_session_state() -> None:
    """
    Initializes all global Streamlit session state properties.
    Ensures they are present before pages are loaded.
    """
    # Load defaults from environment variables where applicable
    if "groq_api_key" not in st.session_state:
        st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
    if "groq_model" not in st.session_state:
        st.session_state.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if "user_role" not in st.session_state:
        st.session_state.user_role = "guest"  # "guest" or "authenticated"

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = UserProfile(
            name="Emergency Guest",
            city="Mumbai",
            family_members=1,
            children=0,
            senior_citizens=0,
            pets=False,
            medical_conditions=""
        )

    if "weather" not in st.session_state:
        st.session_state.weather = None

    if "checklist" not in st.session_state:
        st.session_state.checklist = None

    if "plan" not in st.session_state:
        st.session_state.plan = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def logout() -> None:
    """
    Handles logging out the user, clearing relevant session states,
    and triggering a navigation reset.
    """
    st.session_state.logged_in = False
    st.session_state.user_role = "guest"
    st.session_state.user_profile = UserProfile(
        name="Emergency Guest",
        city="Mumbai",
        family_members=1,
        children=0,
        senior_citizens=0,
        pets=False,
        medical_conditions=""
    )
    st.session_state.weather = None
    st.session_state.checklist = None
    st.session_state.plan = None
    st.session_state.chat_history = []
    st.rerun()

def apply_custom_css() -> None:
    """
    Applies custom CSS to modify Streamlit's default components,
    giving a modern glassmorphic look with custom fonts, subtle shadows, and premium layout tokens.
    """
    st.markdown(
        """
        <style>
        /* Import premium font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
        }

        /* Glassmorphic card design template */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }

        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.2);
        }

        /* Alerts Styling */
        .alert-red {
            border-left: 6px solid #ff4b4b;
            background: rgba(255, 75, 75, 0.08);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
        }
        
        .alert-orange {
            border-left: 6px solid #ffa500;
            background: rgba(255, 165, 0, 0.08);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
        }

        .alert-yellow {
            border-left: 6px solid #ffd700;
            background: rgba(255, 215, 0, 0.08);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
        }

        .alert-normal {
            border-left: 6px solid #00c853;
            background: rgba(0, 200, 83, 0.08);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 15px;
        }

        /* Custom style buttons */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 10px 24px;
            transition: all 0.2s ease-in-out;
        }

        /* Weather stats container styling */
        .metric-cell {
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .metric-val {
            font-size: 2rem;
            font-weight: 700;
            color: #00e5ff;
            line-height: 1.2;
        }

        .metric-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #8892b0;
            margin-top: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
