import streamlit as st
from services.llm_service import LLMService
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css
from components.branding import emergency_notification_bar

apply_custom_css()

st.title("✅ Interactive Monsoon Readiness Checklist")
st.write(
    """
    Check off tasks as you prepare. Keeping your checklist updated helps you track house safety readiness 
    and ration stocking in real-time.
    """
)

# Active states
profile = st.session_state.user_profile
weather = st.session_state.get("weather")

# Render active top warning notification bar
emergency_notification_bar(weather)
checklist = st.session_state.get("checklist")

# Sync weather if missing
if weather is None:
    try:
        weather = WeatherService.get_weather(profile.city)
        st.session_state.weather = weather
    except Exception:
        pass

# Setup checklists if empty
if checklist is None:
    # We display a prompt to build it
    st.markdown("<br/>", unsafe_allow_html=True)
    st.info("💡 No checklists generated yet. Compile your personalized task cards below.")
    
    # Generate button
    if st.button("🚀 Synthesize Personalized Checklist", type="primary"):
        if not st.session_state.get("groq_api_key"):
            st.warning("⚠️ **Developer Warning:** Configure your GROQ_API_KEY in the sidebar before generating AI checklists.")
        else:
            with st.spinner("🤖 Mapping emergency tasks from weather and demographics..."):
                try:
                    generated = LLMService.generate_checklist(profile, weather)
                    st.session_state.checklist = generated
                    st.success("Checklist compiled!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error compiling checklist: {e}")
else:
    # 1. Progress Bar Card
    total_tasks = len(checklist)
    completed_tasks = sum(1 for item in checklist if item["completed"])
    completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"#### 📊 Preparedness Score: {int(completion_rate * 100)}%")
    st.progress(completion_rate)
    st.write(f"Completed **{completed_tasks}** out of **{total_tasks}** recommendations.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Interactive Checklist Render
    st.subheader("📋 Your Checklist Items")
    
    # Collect updates without interrupting render flow
    state_changed = False
    
    # Group items by category to make it beautiful
    categories = sorted(list(set(item["category"] for item in checklist)))
    
    for category in categories:
        st.markdown(f"#### 🏷️ {category}")
        
        # Pull matching items
        for idx, item in enumerate(checklist):
            if item["category"] == category:
                # Unique key identifier
                chk_key = f"chk_task_{idx}_{item['task'][:20]}"
                
                # Checkbox
                checked_status = st.checkbox(
                    item["task"],
                    value=item["completed"],
                    key=chk_key
                )
                
                # If checked status has been changed by user click, save it
                if checked_status != item["completed"]:
                    st.session_state.checklist[idx]["completed"] = checked_status
                    state_changed = True
                    
        st.write("") # small divider

    # If any checkboxes changed state, rerun the page to update progress percentage
    if state_changed:
        st.rerun()

    st.markdown("---")
    
    # Action card: Resynthesis & Custom Tasks
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔄 Synthesize Fresh AI Checklist", use_container_width=True):
            if not st.session_state.get("groq_api_key"):
                st.warning("Please configure your GROQ_API_KEY path.")
            else:
                with st.spinner("Re-compiling tasks..."):
                    st.session_state.checklist = LLMService.generate_checklist(profile, weather)
                    st.success("New checklist set loaded.")
                    st.rerun()
    with col_b2:
        if st.button("🗑️ Reset Checked Items", use_container_width=True, type="secondary"):
            for idx in range(len(st.session_state.checklist)):
                st.session_state.checklist[idx]["completed"] = False
            st.rerun()
