import streamlit as st
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css

apply_custom_css()

st.title("⛈️ Weather Terminal & Alert Board")
st.write(
    """
    Monitor localized monsoon advisories, rainfall levels, and severe wind speeds. 
    This terminal is integrated with OpenWeatherMap API capabilities and simulates active monsoon systems.
    """
)

profile = st.session_state.user_profile
weather = st.session_state.get("weather")

# Auto-initialize weather if missing
if weather is None:
    try:
        weather = WeatherService.get_weather(profile.city)
        st.session_state.weather = weather
    except Exception:
        pass

# Sidebar/Header indicator for connection status
import os
api_configured = bool(os.getenv("OPENWEATHER_API_KEY"))

status_text = "💚 LIVE OPENWEATHER API CONNECTED" if (api_configured and weather and not weather.get("is_mock")) else "🔌 SIMULATED MONSOON SANDBOX ACTIVE"
status_color = "#00c853" if (api_configured and weather and not weather.get("is_mock")) else "#ffa500"

st.markdown(
    f"""
    <div style="background: rgba(255, 255, 255, 0.02); padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 25px; display: inline-block;">
        <span style="color: {status_color}; font-weight: 600; font-size: 0.85rem;">{status_text}</span>
    </div>
    """,
    unsafe_allow_html=True
)

if weather:
    alert_lbl = weather.get("alert_level", "Yellow Alert")
    alert_clean = alert_lbl.lower()
    
    # Stylized Large Weather Block
    st.markdown(
        f"""
        <div class="glass-card" style="text-align: center; border-left: 6px solid #00e5ff; margin-bottom: 30px;">
            <p style="margin: 0px; font-size: 1rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1px;">Current Climate in {profile.city}</p>
            <h1 style="font-size: 4rem; color: #ffffff; margin: 10px 0px;">{weather.get('temperature', '--')}°C</h1>
            <h3 style="color: #00e5ff; margin: 0px; font-weight: 500;">🌧️ {weather.get('conditions', 'Monsoon')}</h3>
            <p style="color: #a8b2d1; margin-top: 10px; font-size: 0.95rem;">
                State Alert Level: <span style="font-weight: 700;">{alert_lbl}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4 stats layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-cell">
                <div class="metric-val">{weather.get('rain_probability', '--')}%</div>
                <div class="metric-label">Precipitation</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-cell">
                <div class="metric-val">{weather.get('wind_speed', '--')} kph</div>
                <div class="metric-label">Wind Velocity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-cell">
                <div class="metric-val">{weather.get('humidity', '--')}%</div>
                <div class="metric-label">Humidity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        # Custom mock tag
        mock_indicator = "Simulated" if weather.get("is_mock") else "Live REST"
        st.markdown(
            f"""
            <div class="metric-cell">
                <div class="metric-val" style="color: #b57cff; font-size: 1.6rem; padding-top: 5px;">{mock_indicator}</div>
                <div class="metric-label">Data Mode</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.warning("Weather metrics could not be retrieved. Refresh active profile coordinates.")

st.markdown("<br/>", unsafe_allow_html=True)

# Interactive Sandbox Settings expander (The Promptwars Demo Touch)
with st.expander("🛠️ Interactive Demo Sandbox (Change parameters for prompt testing)", expanded=True):
    st.write(
        """
        Manually override weather conditions. Changing these variables operates local settings caches 
        and allows you to immediately test how model prompts structure disaster recommendations 
        (like medical refrigeration or pet shelter rules).
        """
    )
    
    # Form to submit sandbox details
    with st.form("sandbox_weather_form"):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            sb_temp = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(weather.get("temperature", 28.0)), step=0.5)
            sb_rain = st.slider("Rain Probability (%)", min_value=0, max_value=100, value=int(weather.get("rain_probability", 80)))
        with col_s2:
            sb_wind = st.number_input("Wind Speed (km/h)", min_value=0.0, max_value=150.0, value=float(weather.get("wind_speed", 25.0)), step=1.0)
            sb_humidity = st.slider("Humidity (%)", min_value=20, max_value=100, value=int(weather.get("humidity", 90)))
        with col_s3:
            sb_alerts = [
                "Green Alert (Normal)", 
                "Yellow Alert (Stay Updated)", 
                "Orange Alert (Be Prepared)", 
                "Red Alert (Severe Danger)"
            ]
            current_sb_index = 0
            for idx, a in enumerate(sb_alerts):
                if weather.get("alert_level") and weather.get("alert_level").split()[0] in a:
                    current_sb_index = idx
                    break
            sb_alert_level = st.selectbox("Trigger Alert Level", options=sb_alerts, index=current_sb_index)
            sb_conditions = st.text_input("Conditions Description", value=weather.get("conditions", "Heavy Downpour"))
            
        sb_submit = st.form_submit_button("🔥 Apply Sandbox Alert Conditions", type="secondary")
        
        if sb_submit:
            # Overwrite active weather cache
            st.session_state.weather = {
                "temperature": sb_temp,
                "rain_probability": sb_rain,
                "wind_speed": sb_wind,
                "humidity": sb_humidity,
                "alert_level": sb_alert_level,
                "conditions": sb_conditions,
                "is_mock": True
            }
            # Clear compiled plan cache so the model is forced to plan for this emergency state next click
            st.session_state.plan = None
            st.session_state.checklist = None
            st.success("✅ Sandbox parameters synchronized. Click AI Planner or Checklist to see response alterations.")
            st.rerun()
