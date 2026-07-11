import streamlit as st
from utils.ui_helpers import apply_custom_css

apply_custom_css()

st.title("ℹ️ About the Platform & Help Numbers")
st.write(
    """
    Explore the architecture, vision, and core capabilities driving the 
    Monsoon Preparedness and Citizen Assistance portal.
    """
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("🎯 Project Mission & Vision")
st.markdown(
    """
    Every monsoon season, regions experience severe flooding, disruption of services, and healthcare risks. 
    **Monsoon Preparedness Hub** is a citizens' application that bridges the gap between weather alerts 
    and personalized preparation.
    
    Rather than generic checklist pamphlets, our application leverages **Generative Action Models** to tailor safety tasks, 
    survival kits, and travel instructions precisely to a family's constraints (like diabetic support or pet evacuations) and local weather conditions.
    """
)
st.markdown('</div>', unsafe_allow_html=True)

# Technical Details
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("🛠️ Technical Architecture & Stack")
st.markdown(
    """
    The application is built using a clean, light-weight architecture optimized for rapid prototype hosting 
    on **Streamlit Community Cloud**:
    
    - **Frontend Layer**: Streamlit Multipage `st.navigation` framework with customizable glassmorphic themes.
    - **Validation Engine**: Pydantic v2 schemas validating family details and preventing logical input anomalies.
    - **Service Orchestration**: LangChain wrapping API client connections.
    - **Intelligence Model**: Groq Chat client running state-of-the-art LLMs (e.g. `llama-3.3-70b-versatile`).
    - **Weather Feed**: REST integration ready for OpenWeather API payloads with consistent fallback mocks.
    """
)
st.markdown('</div>', unsafe_allow_html=True)

# Emergency Contacts
st.subheader("🚨 National & Local Emergency Help Desk")
st.write("Save these numbers offline for access during power outages or cellular disruptions:")

contacts_table = """
| Agency / Department | Toll-Free Helpline | Scope of Support |
| :--- | :---: | :--- |
| **National Disaster Response Force (NDRF)** | **011-24363260** / **9711077372** | Search, Rescue, Evacuation |
| **All India Emergency Response Support** | **112** | Integrated Police, Fire, Ambulance |
| **Police Control Room** | **100** | Law Enforcement & Local Order |
| **Fire Command Center** | **101** | Fire Risks & Water Pumpouts |
| **Ambulance Services** | **102** / **108** | Medical Emergencies & Evacuation |
| **Disaster Management Center** | **1078** | Incident Command & Relief Shelters |
| **Central Water Commission Forecasts** | **1070** | Flood Advisories and Dam Release alerts |
"""

st.markdown(contacts_table)

st.markdown("<br/><hr style='opacity:0.1;'/><p style='text-align:center; color:#8892b0; font-size:0.85rem;'>Democratizing disaster safety intelligence with Generative AI • PromptWars Hackathon 2026</p>", unsafe_allow_html=True)
