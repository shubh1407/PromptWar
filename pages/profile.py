import streamlit as st
from pydantic import ValidationError
from models.user_profile import UserProfile
from services.weather_service import WeatherService
from utils.ui_helpers import apply_custom_css

apply_custom_css()

st.title("👤 Citizen Demographics & Profile Support")
st.write(
    """
    Keep your household profile updated. Our Generative AI Preparedness Planner
    utilizes these metrics to tailor medicine requirements, food rations, pet safety,
    and general emergency tips.
    """
)
st.caption("Update your profile to improve the relevance of AI-generated preparedness advice.")

current_profile = st.session_state.user_profile

with st.form("profile_update_form", clear_on_submit=False):
    st.subheader("📋 Household Demographics Setup")
    st.caption("These fields help the planner tailor emergency guidance for your household.")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Name / Primary Contact",
            value=current_profile.name,
            help="Enter the main contact name for the household profile.",
        )
        city = st.text_input(
            "City of Residence",
            value=current_profile.city,
            help="Enter the city to receive location-specific weather context.",
        )

    with col2:
        family_members = st.number_input(
            "Total Family Members (Including self)",
            min_value=1,
            value=current_profile.family_members,
            step=1,
            help="Enter the total number of people living in your home.",
        )
        pets = st.checkbox(
            "Check if you have pets in the house",
            value=current_profile.pets,
            help="This helps the planner include pet-specific safety advice.",
        )

    st.markdown("---")
    st.subheader("👴 Vulnerable Household Members")
    st.caption("These counts help the assistant tailor advice for children, seniors, and medical needs.")

    col3, col4 = st.columns(2)
    with col3:
        children = st.number_input(
            "Number of Children (Under 18)",
            min_value=0,
            value=current_profile.children,
            step=1,
            help="Enter the number of children in the household.",
        )
    with col4:
        senior_citizens = st.number_input(
            "Number of Senior Citizens (60+)",
            min_value=0,
            value=current_profile.senior_citizens,
            step=1,
            help="Enter the number of senior adults in the household.",
        )

    st.markdown("---")
    st.subheader("💊 Medical Conditions & Regular Medications")
    medical_conditions = st.text_area(
        "Specify medical needs",
        value=current_profile.medical_conditions,
        placeholder="e.g. Grandma has diabetes, needs refrigeration for insulin. Toddler requires inhaler.",
        help="Share medical conditions or regular medicines so recommendations can be tailored to your household.",
    )

    submit_btn = st.form_submit_button(
        "💾 Save Profile & Update Weather",
        type="primary",
        help="Save the updated profile and refresh weather guidance.",
    )

    if submit_btn:
        try:
            validated_profile = UserProfile(
                name=name.strip(),
                city=city.strip(),
                family_members=family_members,
                children=children,
                senior_citizens=senior_citizens,
                pets=pets,
                medical_conditions=medical_conditions.strip(),
            )

            st.session_state.user_profile = validated_profile

            with st.spinner("Fetching weather context for the updated city..."):
                weather_data = WeatherService.get_weather(validated_profile.city)
                st.session_state.weather = weather_data

                st.session_state.plan = None
                st.session_state.checklist = None

            st.success("Profile settings verified and saved. Active weather rules updated.")
            st.rerun()

        except ValidationError as exc:
            st.error("Validation failed. Review the issues below and update the highlighted fields.")
            for err in exc.errors():
                loc_field = err["loc"][0] if err["loc"] else "Parameters"
                err_msg = err["msg"]
                st.markdown(f"* **{str(loc_field).replace('_', ' ').capitalize()}**: {err_msg}")
