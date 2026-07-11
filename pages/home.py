import streamlit as st
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css
from components.branding import emergency_notification_bar

apply_custom_css()

# Retrieve user statistics from session state
profile = st.session_state.user_profile
weather = st.session_state.get("weather")

# Auto-fetch weather if not present
if weather is None:
    try:
        weather = WeatherService.get_weather(profile.city)
        st.session_state.weather = weather
    except Exception:
        pass

# Header Section
st.header("🌧️ Monsoon Preparedness Central")
st.caption(f"Welcome back, {profile.name}. Your current session is {st.session_state.user_role.capitalize()}.")

# Render active top warning notification bar
emergency_notification_bar(weather)

# Content layout columns
col_main, col_actions = st.columns([2, 1], gap="large")

with col_main:
    # 1. Emergency Risk Level Component
    st.subheader("⚠️ Current Emergency Risk Assessment")
    
    if weather:
        alert_lv = weather.get("alert_level", "Normal Alert Level")
        alert_clean = alert_lv.lower()
        
        # Decide Alert card contents & classes
        if "red" in alert_clean:
            css_class = "alert-red"
            alert_header = "🚨 CRITICAL RISK - RED ALERT"
            alert_desc = f"Severe tropical monsoon storm active in {profile.city}. Flooding, power outages, and travel hazards are highly likely. Stay indoors and ensure emergency systems are active."
        elif "orange" in alert_clean:
            css_class = "alert-orange"
            alert_header = "🟠 HIGH RISK - ORANGE ALERT"
            alert_desc = f"Heavy continuous downpours reported in {profile.city}. Low-lying areas are prone to waterlogging. Prepare emergency kits and avoid unnecessary commuting."
        elif "yellow" in alert_clean:
            css_class = "alert-yellow"
            alert_header = "🟡 MODERATE RISK - YELLOW ALERT"
            alert_desc = f"Moderate rain triggers in {profile.city}. Maintain vigilance. Keep check of local travel updates and secure drainage systems around your residence."
        else:
            css_class = "alert-normal"
            alert_header = "🟢 LOW RISK - NORMAL CONDITIONS"
            alert_desc = f"Weather in {profile.city} is currently within manageable levels. Standard seasonal preparedness is recommended."
            
        if "red" in alert_clean:
            st.error(f"**{alert_header}**\n\n{alert_desc}")
        elif "orange" in alert_clean:
            st.warning(f"**{alert_header}**\n\n{alert_desc}")
        elif "yellow" in alert_clean:
            st.info(f"**{alert_header}**\n\n{alert_desc}")
        else:
            st.success(f"**{alert_header}**\n\n{alert_desc}")
    else:
        st.warning("Weather information is currently unavailable. Setup your profile or verify connectivity.")

    st.markdown("---")

    # 2. Weather Grid Component
    st.subheader(f"⛈️ Weather Insights for {profile.city}")
    if weather:
        st.caption(f"Current conditions: {weather.get('conditions', 'Unknown')}")

        w_cols = st.columns(4)
        with w_cols[0]:
            st.metric("Temperature", f"{weather.get('temperature', '--')}°C", help="Current temperature in your city")
        with w_cols[1]:
            st.metric("Rain Probability", f"{weather.get('rain_probability', '--')}%", help="Estimated chance of rain")
        with w_cols[2]:
            st.metric("Wind Speed", f"{weather.get('wind_speed', '--')} kph", help="Current wind speed")
        with w_cols[3]:
            st.metric("Humidity", f"{weather.get('humidity', '--')}%", help="Current humidity")

        st.caption(f"Source: {'Simulated fallback metrics' if weather.get('is_mock') else 'Live OpenWeather feeds'} • Refresh for latest updates.")
    else:
        st.info("Please fill out your target details in profile setup to enable weather tracking.")

with col_actions:
    st.subheader("⚡ Quick Control Actions")
    st.caption("Choose a task to move quickly between the main preparedness tools.")

    if st.button("👤 View & Edit Profile Info", use_container_width=True, help="Open the profile page to update household details"):
        st.switch_page("pages/profile.py")

    if st.button("📋 Generate AI Preparedness Plan", use_container_width=True, help="Create a tailored preparedness plan"):
        st.switch_page("pages/planner.py")

    if st.button("✅ Access Action Checklist", use_container_width=True, help="Open the checklist for your preparedness tasks"):
        st.switch_page("pages/checklist.py")

    if st.button("💬 Ask Citizen AI Chatbot", use_container_width=True, help="Open the assistant chat experience"):
        st.switch_page("pages/chat.py")

    if st.button("⛈️ Weather integration board", use_container_width=True, help="Open the weather information page"):
        st.switch_page("pages/weather.py")

    st.markdown("---")
    st.subheader("📍 Location Tracker")
    st.caption(f"Current tracking city: {profile.city}")

    if st.button("🌀 Force Refresh Local Data", use_container_width=True, type="secondary", help="Refresh weather information for your current city"):
        with st.spinner("Refreshing..."):
            st.session_state.weather = WeatherService.get_weather(profile.city)
            st.success("Weather details updated from service.")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
