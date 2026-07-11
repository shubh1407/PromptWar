import dotenv
import streamlit as st
from utils.ui_helpers import init_session_state, apply_custom_css, logout

# Load environment variables from .env
dotenv.load_dotenv()

# Set up page configurations
st.set_page_config(
    page_title="Monsoon Preparedness & Citizen Assistance",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global session variables
init_session_state()

# Apply page-wide branding, glassmorphism templates, and modern fonts
apply_custom_css()

# Configure Multi-Page Routing
# We define St.Page objects mapping to our pages folder.
login_page = st.Page("pages/login.py", title="Get Started", icon="🔒")
home_page = st.Page("pages/home.py", title="Dashboard", icon="🏠", default=True)
profile_page = st.Page("pages/profile.py", title="Citizen Profile", icon="👤")
planner_page = st.Page("pages/planner.py", title="AI Planner", icon="📋")
checklist_page = st.Page("pages/checklist.py", title="Preparedness Checklist", icon="✅")
weather_page = st.Page("pages/weather.py", title="Weather Terminal", icon="⛈️")
chat_page = st.Page("pages/chat.py", title="AI Assistance Chat", icon="💬")
about_page = st.Page("pages/about.py", title="About & Contacts", icon="ℹ️")

# Determine navigation based on login status
if not st.session_state.logged_in:
    pg = st.navigation([login_page], position="hidden")
else:
    # Sidebar control panel
    with st.sidebar:
        st.markdown("### ⛈️ Monsoon Assistant")
        st.write(f"Welcome, **{st.session_state.user_profile.name}**")
        st.caption(f"📍 Location: {st.session_state.user_profile.city}")
        
        # User details card summary
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border: 1px dashed rgba(255,255,255,0.1); margin-bottom: 20px;">
                <small>👪 Family size: {st.session_state.user_profile.family_members}</small><br/>
                <small>👶 Children: {st.session_state.user_profile.children} | 👴 Seniors: {st.session_state.user_profile.senior_citizens}</small><br/>
                <small>🐾 Pets: {"Yes" if st.session_state.user_profile.pets else "No"}</small>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.divider()
        
        # Dev / Presenter Dashboard
        with st.expander("🛠️ Developer Tooling", expanded=False):
            st.caption("Customize the models and keys for testing or presentation.")
            user_key = st.text_input("Override Groq API Key", value=st.session_state.groq_api_key, type="password", key="dev_api_key")
            if user_key:
                st.session_state.groq_api_key = user_key
                
            model_options = [
                "llama-3.3-70b-versatile",
                "mixtral-8x7b-32768",
                "llama3-8b-8192",
                "gemma2-9b-it"
            ]
            chosen_model = st.selectbox("LLM Model Selection", options=model_options, index=model_options.index(st.session_state.groq_model) if st.session_state.groq_model in model_options else 0)
            st.session_state.groq_model = chosen_model
            
            st.caption(f"Active Key: {'Configured ➔ State' if st.session_state.groq_api_key else 'Missing'}")
            st.caption(f"Active Model: `{st.session_state.groq_model}`")

        # Logout Button
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            logout()
            
    pg = st.navigation({
        "Citizen Dashboard": [home_page, profile_page],
        "AI Preparedness Tools": [planner_page, checklist_page, weather_page],
        "Support & Info": [chat_page, about_page]
    })

# Run the selected page context
pg.run()
