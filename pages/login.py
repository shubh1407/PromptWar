import streamlit as st
from models.user_profile import UserProfile
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css

# Page configuration is inherited from app.py, but custom css is initialized
apply_custom_css()

# Center Layout
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.header("⛈️ Monsoon Preparedness Hub", divider="blue")
    st.caption("Generative AI-Powered Citizen Assistance & Emergency Planning")

    try:
        st.image(
            "assets/monsoon_banner.png",
            use_container_width=True,
            caption="Monsoon preparedness illustration for the citizen assistance portal",
        )
    except Exception:
        st.info("The banner image could not be loaded, but the portal remains fully usable.")

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
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🔐 Sign In / Profile Setup", "🚶 Demo Guest Access"])

    with tab1:
        st.write("Enter your basic details to build your customized preparedness model.")
        st.caption("Required fields are marked clearly below so the form is easier to complete with assistive technology.")

        name_input = st.text_input(
            "Full Name",
            placeholder="e.g. John Doe",
            help="Enter your full name so the assistant can personalize recommendations.",
        )
        city_input = st.text_input(
            "City Name",
            placeholder="e.g. Mumbai, Chennai, Kolkata",
            help="Enter the city where you want weather-based preparedness guidance.",
        )

        login_btn = st.button(
            "🔐 Initialize Portal",
            use_container_width=False,
            type="primary",
            help="Create your profile and begin using the preparedness dashboard.",
        )

        if login_btn:
            if len(name_input.strip()) < 2:
                st.error("Please enter a valid name with at least 2 characters so the portal can personalize your experience.")
            elif len(city_input.strip()) < 2:
                st.error("Please enter a valid city name with at least 2 characters.")
            else:
                with st.spinner("Analyzing weather data and creating session..."):
                    profile = UserProfile(
                        name=name_input.strip(),
                        city=city_input.strip(),
                        family_members=1,
                        children=0,
                        senior_citizens=0,
                        pets=False,
                        medical_conditions="",
                    )

                    st.session_state.user_profile = profile
                    st.session_state.user_role = "authenticated"

                    try:
                        weather_data = WeatherService.get_weather(profile.city)
                        st.session_state.weather = weather_data
                    except Exception as exc:
                        st.session_state.weather = None
                        st.warning(f"Weather could not be loaded automatically: {exc}")

                    st.session_state.logged_in = True
                    st.success(f"Welcome {profile.name}! Your dashboard is ready.")
                    st.rerun()

    with tab2:
        st.write("Use the guest experience for a quick demo of the portal.")
        st.caption("This option skips the form and starts the application with a default sample profile.")
        st.markdown(
            """
            * Logs in as **Emergency Guest**
            * Simulates location context: **Mumbai, MH**
            * Bypasses form validations
            * Configures fallback data caches instantly
            """
        )

        guest_btn = st.button(
            "⚡ Continue in Guest Mode",
            use_container_width=True,
            type="secondary",
            help="Start the portal immediately with a sample guest profile.",
        )

        if guest_btn:
            with st.spinner("Initializing Guest Sandbox..."):
                profile = UserProfile(
                    name="Emergency Guest",
                    city="Mumbai",
                    family_members=1,
                    children=0,
                    senior_citizens=0,
                    pets=False,
                    medical_conditions="",
                )
                st.session_state.user_profile = profile
                st.session_state.user_role = "guest"

                try:
                    weather_data = WeatherService.get_weather("Mumbai")
                    st.session_state.weather = weather_data
                except Exception:
                    st.session_state.weather = None

                st.session_state.logged_in = True
                st.rerun()

    st.markdown(
        "<br/><hr style='opacity:0.1;'/><p style='text-align:center; color:#8892b0; font-size:0.8rem;'>Monsoon Assistance Engine • Developed with Streamlit & LangChain</p>",
        unsafe_allow_html=True,
    )
