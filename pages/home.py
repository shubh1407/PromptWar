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
st.title("🌧️ Monsoon Preparedness Central")
st.write(f"Welcome back, **{profile.name}** | Status: `{st.session_state.user_role.capitalize()} Session`")

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
            
        st.markdown(
            f"""
            <div class="{css_class}">
                <strong style="font-size: 1.15rem; color: #ffffff;">{alert_header}</strong><br/>
                <span style="color: #e2e8f0; font-size: 0.95rem; display: block; margin-top: 5px;">{alert_desc}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.warning("Weather information is currently unavailable. Setup your profile or verify connectivity.")

    st.markdown("---")

    # 2. Weather Grid Component
    st.subheader(f"⛈️ Weather Insights for `{profile.city}`")
    if weather:
        # Mini description banner
        st.markdown(f"**Current Status:** __{weather.get('conditions', 'Unknown')}__")
        
        w_cols = st.columns(4)
        
        with w_cols[0]:
            st.markdown(
                f"""
                <div class="metric-cell">
                    <div class="metric-val">{weather.get('temperature', '--')}°C</div>
                    <div class="metric-label">Temp</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with w_cols[1]:
            st.markdown(
                f"""
                <div class="metric-cell">
                    <div class="metric-val">{weather.get('rain_probability', '--')}%</div>
                    <div class="metric-label">Rain Prob</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with w_cols[2]:
            st.markdown(
                f"""
                <div class="metric-cell">
                    <div class="metric-val">{weather.get('wind_speed', '--')} kph</div>
                    <div class="metric-label">Wind</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with w_cols[3]:
            st.markdown(
                f"""
                <div class="metric-cell">
                    <div class="metric-val">{weather.get('humidity', '--')}%</div>
                    <div class="metric-label">Humidity</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Refresh and status indicator
        st.caption(f"Source: {'Simulated fallback metrics' if weather.get('is_mock') else 'Live OpenWeather feeds'} • Refresh for latest updates.")
    else:
        st.info("Please fill out your target details in profile setup to enable weather tracking.")

with col_actions:
    st.subheader("⚡ Quick Control Actions")
    
    # Render quick action buttons that programmatically route the user
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#8892b0; margin-top:0px;'>Navigate rapidly through pre-configured features:</p>", unsafe_allow_html=True)
    
    if st.button("👤 View & Edit Profile Info", use_container_width=True):
        st.switch_page("pages/profile.py")
        
    if st.button("📋 Generate AI Preparedness Plan", use_container_width=True):
        st.switch_page("pages/planner.py")
        
    if st.button("✅ Access Action Checklist", use_container_width=True):
        st.switch_page("pages/checklist.py")
        
    if st.button("💬 Ask Citizen AI Chatbot", use_container_width=True):
        st.switch_page("pages/chat.py")
        
    if st.button("⛈️ Weather integration board", use_container_width=True):
        st.switch_page("pages/weather.py")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fast weather reload card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h5 style='margin:0px 0px 8px 0px; color:#ffffff;'>📍 Location Tracker</h5>", unsafe_allow_html=True)
    st.write(f"Current tracking city: **{profile.city}**")
    
    if st.button("🌀 Force Refresh Local Data", use_container_width=True, type="secondary"):
        with st.spinner("Refreshing..."):
            st.session_state.weather = WeatherService.get_weather(profile.city)
            st.success("Weather details updated from service.")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
