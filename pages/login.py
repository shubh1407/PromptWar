import streamlit as st
from models.user_profile import UserProfile
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css

# Page configuration is inherited from app.py, but custom css is initialized
apply_custom_css()

# Center Layout
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    # Display the generated visual header
    try:
        st.image("assets/monsoon_banner.png", use_container_width=True)
    except Exception:
        # Fallback if image has issues loading
        pass
        
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #00e5ff; margin-bottom: 0px;">⛈️ Monsoon Preparedness Hub</h1>
            <p style="color: #8892b0; font-size: 1.1rem; margin-top: 5px;">
                Generative AI-Powered Citizen Assistance & Emergency Planning
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Hero description
    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin-top:0px; color:#ffffff;">🔒 Crisis Readiness Dashboard</h4>
            <p style="font-size:0.95rem; color:#a8b2d1; line-height:1.6;">
                Welcome to the official <b>Monsoon Preparedness and Citizen Assistance Platform</b>. 
                Using real-time safety models, we provide hyper-localized preparedness strategies, emergency kit tallies, 
                and live AI assistant support to navigate challenging tropical weather seasons.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Form Tab and Guest Tab
    tab1, tab2 = st.tabs(["🔐 Sign In / Profile Setup", "🚶 Demo Guest Access"])
    
    with tab1:
        st.write("Enter your basic details to build your customized preparedness model:")
        
        # Form inputs
        name_input = st.text_input("Full Name", placeholder="e.g. John Doe")
        city_input = st.text_input("City Name", placeholder="e.g. Mumbai, Chennai, Kolkata")
        
        login_btn = st.button("🔐 Initialize Portal", use_container_width=False, type="primary")
        
        if login_btn:
            if len(name_input.strip()) < 2:
                st.error("⚠️ Please enter a valid name (minimum 2 characters).")
            elif len(city_input.strip()) < 2:
                st.error("⚠️ Please enter a valid city (minimum 2 characters).")
            else:
                with st.spinner("Analyzing weather data and creating session..."):
                    # Save user details to profile
                    profile = UserProfile(
                        name=name_input.strip(),
                        city=city_input.strip(),
                        family_members=1,
                        children=0,
                        senior_citizens=0,
                        pets=False,
                        medical_conditions=""
                    )
                    
                    # Store in session state
                    st.session_state.user_profile = profile
                    st.session_state.user_role = "authenticated"
                    
                    # Pre-cache weather immediately for home page speed
                    try:
                        weather_data = WeatherService.get_weather(profile.city)
                        st.session_state.weather = weather_data
                    except Exception as e:
                        st.session_state.weather = None
                        st.warning(f"Could not load weather: {e}")
                        
                    # Set logged in state to true
                    st.session_state.logged_in = True
                    st.success(f"Welcome {profile.name}! Dashboard configured successfully.")
                    st.rerun()

    with tab2:
        st.write("Ideal for quick evaluations, testing features, or developer demos:")
        st.markdown(
            """
            * Logs in as **Emergency Guest**
            * Simulates location context: **Mumbai, MH**
            * Bypasses form validations
            * Configures fallback data caches instantly
            """
        )
        
        guest_btn = st.button("⚡ Continue in Guest Mode", use_container_width=True, type="secondary")
        
        if guest_btn:
            with st.spinner("Initializing Guest Sandbox..."):
                # Initialize default profile
                profile = UserProfile(
                    name="Emergency Guest",
                    city="Mumbai",
                    family_members=1,
                    children=0,
                    senior_citizens=0,
                    pets=False,
                    medical_conditions=""
                )
                st.session_state.user_profile = profile
                st.session_state.user_role = "guest"
                
                # Pre-fetch weather for Guest City (Mumbai)
                try:
                    weather_data = WeatherService.get_weather("Mumbai")
                    st.session_state.weather = weather_data
                except Exception:
                    st.session_state.weather = None

                st.session_state.logged_in = True
                st.rerun()
                
    st.markdown("<br/><hr style='opacity:0.1;'/><p style='text-align:center; color:#8892b0; font-size:0.8rem;'>Monsoon Assistance Engine • Developed with Streamlit & LangChain</p>", unsafe_allow_html=True)
