import streamlit as st
from services.llm_service import LLMService
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css
from components.branding import emergency_notification_bar

apply_custom_css()

st.title("💬 Emergency Assistance AI Chatbot")
st.write(
    """
    Ask instant, monsoon-related safety questions. Your profile demographics and local weather alert levels 
    are automatically sent as conversational context to the LLM to deliver appropriate advice.
    """
)

# Initialize data
profile = st.session_state.user_profile
weather = st.session_state.get("weather")

# Render active top warning notification bar
emergency_notification_bar(weather)
history = st.session_state.get("chat_history", [])

if weather is None:
    try:
        weather = WeatherService.get_weather(profile.city)
        st.session_state.weather = weather
    except Exception:
        pass

# Quick suggestion prompt triggers
st.markdown("##### 💡 Suggested Questions")
sug_col1, sug_col2, sug_col3 = st.columns(3)
clicked_prompt = None

with sug_col1:
    if st.button("🌧️ General Storm Prep?", use_container_width=True):
        clicked_prompt = "How should I prepare for heavy rain?"
with sug_col2:
    if st.button("🩺 Chronic Medicine Info?", use_container_width=True):
        clicked_prompt = "What medicines should diabetics keep during rains?"
with sug_col3:
    if st.button("🚗 Travel Feasibility?", use_container_width=True):
        clicked_prompt = "Is it safe to travel tomorrow?"

# Input box
user_input = st.chat_input("Ask a monsoon preparation question...")

# Determine final query text (either from text input or suggestions clicks)
active_query = user_input or clicked_prompt

# API Check prior to rendering
api_configured = bool(st.session_state.get("groq_api_key"))

# Display message history
for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if active_query:
    # 1. Check API validation
    if not api_configured:
        st.error("⚠️ **AI Communication Interrupted:** Please enter a valid GROQ_API_KEY in the sidebar settings panel before chatting.")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(active_query)
            
        # Add to history list
        st.session_state.chat_history.append({"role": "user", "content": active_query})
        
        # Display assistant streaming message
        with st.chat_message("assistant"):
            try:
                # Setup streaming generator
                stream_generator = LLMService.stream_chat(
                    profile, 
                    weather or {}, 
                    st.session_state.chat_history
                )
                
                # Stream into container
                full_reply = st.write_stream(stream_generator)
                
                # Save assistant output
                st.session_state.chat_history.append({"role": "assistant", "content": full_reply})
            except Exception as stream_err:
                st.error(f"Streaming failed: {stream_err}")
                
        # Force a refresh to align states
        st.rerun()

# Clear Button in Sidebar/Footer
if len(history) > 0:
    st.markdown("---")
    if st.button("🗑️ Clear Chat Conversations", type="secondary"):
        st.session_state.chat_history = []
        st.success("Chat history wiped.")
        st.rerun()
