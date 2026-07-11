import streamlit as st
from services.llm_service import LLMService
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css
from components.branding import emergency_notification_bar

apply_custom_css()

st.header("📋 Personal AI Preparedness Plan")
st.write(
    """
    Generate customized storm guidelines, medication backups, pet escape routes,
    and general safety tips tailored precisely to your family size, location weather conditions, and vulnerable members.
    """
)
st.caption("Use this planner to create a tailored set of emergency actions for your household.")

# Grab current state
profile = st.session_state.user_profile
weather = st.session_state.get("weather")

# Render active top warning notification bar
emergency_notification_bar(weather)
cached_plan = st.session_state.get("plan")

# Ensure weather context is present
if weather is None:
    try:
        weather = WeatherService.get_weather(profile.city)
        st.session_state.weather = weather
    except Exception:
        pass

# Quick profile context summary card
st.info(
    f"Generating context for {profile.city}: alert level {weather.get('alert_level', 'No Alert')}. "
    f"Household size {profile.family_members} (including {profile.children} children and {profile.senior_citizens} seniors). "
    f"Pets: {'Yes' if profile.pets else 'No'}. Medical needs: {profile.medical_conditions or 'None reported'}."
)

# Buttons for plan actions
col_btn1, col_btn2 = st.columns([1, 2])
with col_btn1:
    btn_label = "🔄 Re-generate AI Plan" if cached_plan else "🚀 Compile AI Preparedness Plan"
    generate_trigger = st.button(btn_label, type="primary", use_container_width=True, help="Generate or refresh your personalized preparedness plan")

with col_btn2:
    if cached_plan:
        st.caption("Plan compiled successfully. Re-running will fetch updated advice from Groq.")

# AI Logic Run
if generate_trigger:
    # Key check
    if not st.session_state.get("groq_api_key"):
        st.warning("⚠️ **Secret Key Missing:** Please insert a valid GROQ_API_KEY in the sidebar Developer Panel before running.")
    else:
        with st.spinner("🤖 Groq AI is analyzing demographic vulnerability and weather levels..."):
            try:
                # Fire call to LLM
                plan = LLMService.generate_preparedness_plan(profile, weather)
                st.session_state.plan = plan
                st.success("Plan synthesized successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate structured plan: {e}")
                st.info("Check if your Groq API Key is valid or if the network is available.")

# Render Plan
if st.session_state.plan:
    plan = st.session_state.plan
    
    # 3 Column Premium Layout for the Categories
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    row3_col1, row3_col2 = st.columns(2)
    
    # 1. Preparation Card
    with row1_col1:
        st.markdown("### 🏠 House & Environment Prep")
        for item in plan.get("preparation", []):
            st.markdown(f"- {item}")
        
    # 2. Food Card
    with row1_col2:
        st.markdown("### 🍏 Food & Water Provisions")
        for item in plan.get("food", []):
            st.markdown(f"- {item}")

    # 3. Medicines Card
    with row2_col1:
        st.markdown("### 💊 Medicine & Conditions Support")
        for item in plan.get("medicines", []):
            st.markdown(f"- {item}")

    # 4. Emergency Kit Card
    with row2_col2:
        st.markdown("### 🎒 Emergency Kit List")
        for item in plan.get("emergency_kit", []):
            st.markdown(f"- {item}")

    # 5. Travel Card
    with row3_col1:
        st.markdown("### 🚗 Travel & Transit Directives")
        for item in plan.get("travel_advice", []):
            st.markdown(f"- {item}")

    # 6. Safety Tips Card
    with row3_col2:
        st.markdown("### 🛡️ Crisis & Flood Safety Tips")
        for item in plan.get("safety_tips", []):
            st.markdown(f"- {item}")

else:
    # Empty plan state
    st.markdown("<br/>", unsafe_allow_html=True)
    st.info("Tap the button above to analyze your profile constraints and generate your personalized guidelines.")
