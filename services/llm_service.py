import os
import json
import logging
import streamlit as st
from typing import Dict, Any, List, Generator
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from models.user_profile import UserProfile
from prompts.system_prompts import PLANNER_PROMPT, CHECKLIST_PROMPT, CHAT_SYSTEM_PROMPT


def _sanitize_llm_json_content(content: str) -> str:
    """Remove markdown fences around JSON responses so the payload can be parsed reliably."""
    cleaned = content.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

# Configure logger
logger = logging.getLogger(__name__)

# Pydantic schema helpers for structured outputs
class PreparednessPlanModel(BaseModel):
    preparation: List[str] = Field(..., description="Actionable house/surroundings preparedness steps")
    food: List[str] = Field(..., description="Food storage & ration recommendations")
    medicines: List[str] = Field(..., description="Medicines & healthcare steps tailored for any conditions")
    emergency_kit: List[str] = Field(..., description="Survival & emergency supplies kit items")
    travel_advice: List[str] = Field(..., description="Safety advice on transit & travel")
    safety_tips: List[str] = Field(..., description="General storm/flood safety precautions")

def get_llm_client() -> ChatGroq:
    """
    Constructs the ChatGroq client.
    First checks if the user provided an API key in the session state (from UI input).
    Otherwise, checks the environment variable.
    """
    api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    model_name = st.session_state.get("groq_model") or os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
    
    # Strip whitespace/quotes
    if api_key:
        api_key = api_key.strip().strip("'\"")
    if model_name:
        model_name = model_name.strip().strip("'\"")
        
    if not api_key:
        raise ValueError("Groq API Key is not configured. Please add it via a .env file or the sidebar developer panel.")
        
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=0.3,
        max_tokens=2048,
    )

class LLMService:
    @staticmethod
    def generate_preparedness_plan(profile: UserProfile, weather: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generates a structured preparedness plan using Group Chat LLM.
        Employs with_structured_output for robust schemas, falls back to direct JSON prompt parsing.
        """
        logger.info(f"Generating personalized Preparedness Plan for: {profile.name}")
        llm = get_llm_client()
        
        pets_status = "Yes (needs evacuation and feed planning)" if profile.pets else "No pets"
        
        prompt_content = PLANNER_PROMPT.format(
            name=profile.name,
            city=profile.city,
            family_members=profile.family_members,
            children=profile.children,
            senior_citizens=profile.senior_citizens,
            pets_status=pets_status,
            medical_conditions=profile.medical_conditions or "None reported",
            temperature=weather.get("temperature", 28.0),
            rain_probability=weather.get("rain_probability", 80),
            wind_speed=weather.get("wind_speed", 25.0),
            humidity=weather.get("humidity", 90),
            conditions=weather.get("conditions", "Heavy Rain"),
            alert_level=weather.get("alert_level", "Orange Alert")
        )
        
        # Method 1: structured output
        try:
            structured_llm = llm.with_structured_output(PreparednessPlanModel)
            res = structured_llm.invoke(prompt_content)
            return res.model_dump()
        except Exception as exc:
            logger.warning("Structured output parsing failed; falling back to manual JSON parsing.", exc_info=exc)
            
            # Method 2: Manual JSON query
            messages = [
                SystemMessage(content="You are a JSON assistant. You must output a valid JSON and ONLY a valid JSON. Do not write explanation text or wrap inside code fences unless required. The JSON must follow the schema: {preparation: [], food: [], medicines: [], emergency_kit: [], travel_advice: [], safety_tips: []}."),
                HumanMessage(content=prompt_content)
            ]
            response = llm.invoke(messages)
            content = _sanitize_llm_json_content(response.content)
            
            try:
                parsed = json.loads(content)
                # Validation check matches structure
                validated = {}
                for key in ["preparation", "food", "medicines", "emergency_kit", "travel_advice", "safety_tips"]:
                    val = parsed.get(key, [])
                    validated[key] = val if isinstance(val, list) else [str(val)]
                return validated
            except Exception as json_err:
                logger.exception("Fallback JSON parsing also failed. Raw content: %s", content)
                raise ValueError("The AI model returned an invalid format. Please try again.")

    @staticmethod
    def generate_checklist(profile: UserProfile, weather: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates individual checklist items based on the user profile and current weather condition.
        """
        logger.info(f"Generating personalized checklist for: {profile.name}")
        llm = get_llm_client()
        pets_status = "Yes" if profile.pets else "No"
        
        prompt_content = CHECKLIST_PROMPT.format(
            city=profile.city,
            family_members=profile.family_members,
            children=profile.children,
            senior_citizens=profile.senior_citizens,
            pets_status=pets_status,
            medical_conditions=profile.medical_conditions or "None reported",
            alert_level=weather.get("alert_level", "Orange Alert")
        )
        
        messages = [
            SystemMessage(content="You are a JSON assistant. Output a valid raw JSON array of objects representing emergency checklist tasks. Each object must have keys 'task' and 'category' and nothing else. Output only valid JSON."),
            HumanMessage(content=prompt_content)
        ]
        
        try:
            response = llm.invoke(messages)
            content = _sanitize_llm_json_content(response.content)
            
            items = json.loads(content)
            if not isinstance(items, list):
                if isinstance(items, dict) and "tasks" in items:
                    items = items["tasks"]
                else:
                    raise ValueError("JSON parsed but is not a list")
            
            # Format and sanitize
            sanitized = []
            for item in items:
                task = item.get("task", "").strip()
                category = item.get("category", "General").strip()
                if task:
                    sanitized.append({
                        "task": task,
                        "category": category,
                        "completed": False
                    })
            return sanitized
        except Exception:
            logger.exception("Error generating checklist")
            # Dynamic fallback list if API fails
            fallback = [
                {"task": f"Check weather forecasts and alert updates for {profile.city} daily.", "category": "General", "completed": False},
                {"task": "Prepare emergency drinking water (at least 3 liters per person per day).", "category": "Food/Water", "completed": False},
                {"task": "Keep medical prescriptions and critical health supplies in waterproof bags.", "category": "Medical", "completed": False},
                {"task": "Charge backup power banks and emergency lighting/flashlights.", "category": "Utilities", "completed": False},
                {"task": "Identify local emergency evacuation shelter locations.", "category": "Safety", "completed": False}
            ]
            if profile.children:
                fallback.append({"task": "Ensure diapers, baby food, and children's activities are prepared.", "category": "Children Care", "completed": False})
            if profile.pets:
                fallback.append({"task": "Store extra pet food and ensure leash/crate are accessible.", "category": "Pet Care", "completed": False})
            return fallback

    @staticmethod
    def stream_chat(profile: UserProfile, weather: Dict[str, Any], history: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Streams chat responses for the AI Assistance page.
        Passes user profile details and current weather as context.
        """
        logger.info(f"Streaming chat response to user query.")
        llm = get_llm_client()
        
        # Build the system instruction prompt
        sys_instruction = CHAT_SYSTEM_PROMPT.format(
            name=profile.name or "Citizen",
            city=profile.city or "Unknown Location",
            medical_conditions=profile.medical_conditions or "None reported",
            alert_level=weather.get("alert_level", "Orange Alert")
        )
        
        messages = [SystemMessage(content=sys_instruction)]
        
        # Add history
        # History format: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
                
        # Call streaming
        try:
            for response_chunk in llm.stream(messages):
                yield response_chunk.content
        except Exception as exc:
            logger.exception("Chat streaming error")
            yield f"\n\n**Error:** {str(exc)}\nMake sure your GROQ_API_KEY is correct."
