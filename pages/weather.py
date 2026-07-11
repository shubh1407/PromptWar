import streamlit as st
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css

apply_custom_css()

st.header("⛈️ Weather Terminal & Alert Board")
st.write(
    """
    Monitor localized monsoon advisories, rainfall levels, and severe wind speeds.
    This terminal is integrated with OpenWeatherMap API capabilities and simulates active monsoon systems.
    """
)
st.caption("Review the current weather conditions and adjust the sandbox values to explore different monsoon scenarios.")

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

if api_configured and weather and not weather.get("is_mock"):
    st.success(status_text)
else:
    st.warning(status_text)

if weather:
    alert_lbl = weather.get("alert_level", "Yellow Alert")
    alert_clean = alert_lbl.lower()
    
    # Stylized Large Weather Block
    st.markdown(f"### Current Climate in {profile.city}")
    st.markdown(f"**{weather.get('temperature', '--')}°C**")
    st.caption(f"Conditions: {weather.get('conditions', 'Monsoon')} • Alert level: {alert_lbl}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Precipitation", f"{weather.get('rain_probability', '--')}%", help="Estimated chance of rainfall")
    with col2:
        st.metric("Wind Velocity", f"{weather.get('wind_speed', '--')} kph", help="Current wind speed")
    with col3:
        st.metric("Humidity", f"{weather.get('humidity', '--')}%", help="Current humidity level")
    with col4:
        mock_indicator = "Simulated" if weather.get("is_mock") else "Live REST"
        st.metric("Data Mode", mock_indicator, help="Whether the data is simulated or live")

else:
    st.warning("Weather metrics could not be retrieved. Refresh active profile coordinates.")

st.markdown("<br/>", unsafe_allow_html=True)

# Interactive Sandbox Settings expander (The Promptwars Demo Touch)
with st.expander("🛠️ Interactive Demo Sandbox (change parameters for prompt testing)", expanded=True):
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
            sb_temp = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(weather.get("temperature", 28.0)), step=0.5, help="Adjust the temperature used for planning")
            sb_rain = st.slider("Rain Probability (%)", min_value=0, max_value=100, value=int(weather.get("rain_probability", 80)), help="Adjust the predicted chance of rain")
        with col_s2:
            sb_wind = st.number_input("Wind Speed (km/h)", min_value=0.0, max_value=150.0, value=float(weather.get("wind_speed", 25.0)), step=1.0, help="Adjust the wind speed used for planning")
            sb_humidity = st.slider("Humidity (%)", min_value=20, max_value=100, value=int(weather.get("humidity", 90)), help="Adjust the humidity value used for planning")
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
            sb_alert_level = st.selectbox("Trigger Alert Level", options=sb_alerts, index=current_sb_index, help="Choose the alert level used for planning")
            sb_conditions = st.text_input("Conditions Description", value=weather.get("conditions", "Heavy Downpour"), help="Describe the weather condition you want to simulate")

        sb_submit = st.form_submit_button("🔥 Apply Sandbox Alert Conditions", type="secondary", help="Apply the sandbox values to the current session")
        
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
