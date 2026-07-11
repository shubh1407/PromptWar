import streamlit as st
from typing import Dict, Any

def emergency_notification_bar(weather: Dict[str, Any]) -> None:
    """
    Render a global top notification banner on active pages,
    matching emergency warning levels.
    """
    if not weather:
        return
        
    alert_level = weather.get("alert_level", "Normal")
    alert_clean = alert_level.lower()
    
    if "red" in alert_clean:
        bar_html = """
        <div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold; animation: pulse 2s infinite;">
            ⚠️ EMERGENCY FLASH: Severe Red Alert Active. Avoid commuting. Keep phones charged.
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)
    elif "orange" in alert_clean:
        bar_html = """
        <div style="background-color: #ffa500; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold;">
            ⚠️ SAFETY WARNING: Orange Alert. Keep emergency kits ready and monitor drainage systems.
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)
    elif "yellow" in alert_clean:
        bar_html = """
        <div style="background-color: #ffd700; color: #1e1e1e; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold;">
            🔔 STATUS NOTICE: Yellow Alert. Periodic showers active. Stay updated.
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)
