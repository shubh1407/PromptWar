import os
import sys
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import services.llm_service as llm_service
import services.weather_service as weather_service
from components.branding import emergency_notification_bar
from models.user_profile import UserProfile
from prompts.system_prompts import CHECKLIST_PROMPT, CHAT_SYSTEM_PROMPT, PLANNER_PROMPT
from services.llm_service import LLMService
from services.weather_service import WeatherService
from utils import ui_helpers


class SessionState(dict):
    def __getattr__(self, item: str):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key: str, value) -> None:
        self[key] = value


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class FakeStructuredResult:
    def __init__(self, payload: dict):
        self._payload = payload

    def model_dump(self) -> dict:
        return self._payload


class FakeStructuredLLM:
    def __init__(self, payload: dict):
        self._payload = payload

    def with_structured_output(self, model):
        return self

    def invoke(self, prompt):
        return FakeStructuredResult(self._payload)


class FakeJSONLLM:
    def __init__(self, content: str):
        self._content = content

    def with_structured_output(self, model):
        raise RuntimeError("structured output failed")

    def invoke(self, messages):
        return SimpleNamespace(content=self._content)


class FakeStreamLLM:
    def __init__(self, content: str):
        self._content = content

    def stream(self, messages):
        yield SimpleNamespace(content=self._content)


@pytest.fixture
def sample_profile() -> UserProfile:
    return UserProfile(
        name="Asha",
        city="Mumbai",
        family_members=3,
        children=1,
        senior_citizens=1,
        pets=True,
        medical_conditions="Diabetes",
    )


def test_user_profile_valid(sample_profile: UserProfile) -> None:
    assert sample_profile.name == "Asha"
    assert sample_profile.city == "Mumbai"


def test_user_profile_rejects_invalid_children() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            name="Ravi",
            city="Chennai",
            family_members=2,
            children=2,
            senior_citizens=0,
            pets=False,
            medical_conditions="",
        )


def test_user_profile_rejects_invalid_senior_count() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            name="Ravi",
            city="Chennai",
            family_members=2,
            children=1,
            senior_citizens=1,
            pets=False,
            medical_conditions="",
        )


def test_weather_service_uses_live_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "demo-key")

    def fake_get(url: str, timeout: int) -> FakeResponse:
        assert timeout == 5
        assert "Delhi" in url
        return FakeResponse(
            200,
            {
                "main": {"temp": 30.5, "humidity": 88},
                "wind": {"speed": 12.0},
                "weather": [{"main": "Rain"}],
                "clouds": {"all": 80},
            },
        )

    monkeypatch.setattr(weather_service.requests, "get", fake_get)

    weather = WeatherService.get_weather("Delhi")

    assert weather["is_mock"] is False
    assert weather["temperature"] == 30.5
    assert weather["rain_probability"] == 60
    assert weather["alert_level"] == "Orange Alert"


def test_weather_service_falls_back_when_api_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "demo-key")

    def fake_get(url: str, timeout: int) -> FakeResponse:
        return FakeResponse(500, {})

    monkeypatch.setattr(weather_service.requests, "get", fake_get)

    weather = WeatherService.get_weather("Mumbai")

    assert weather["is_mock"] is True
    assert weather["alert_level"].startswith("Orange") or weather["alert_level"].startswith("Red") or weather["alert_level"].startswith("Yellow")


def test_init_session_state_sets_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_state = SessionState()
    monkeypatch.setattr(ui_helpers.st, "session_state", dummy_state)
    monkeypatch.setattr(ui_helpers.st, "rerun", lambda: None)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "demo-model")

    ui_helpers.init_session_state()

    assert dummy_state["groq_api_key"] == "test-key"
    assert dummy_state["groq_model"] == "demo-model"
    assert dummy_state["logged_in"] is False
    assert isinstance(dummy_state["user_profile"], UserProfile)


def test_logout_resets_session(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_state = SessionState({"logged_in": True, "user_profile": "old", "weather": {"x": 1}})
    monkeypatch.setattr(ui_helpers.st, "session_state", dummy_state)
    rerun_calls = []
    monkeypatch.setattr(ui_helpers.st, "rerun", lambda: rerun_calls.append("rerun"))

    ui_helpers.logout()

    assert dummy_state["logged_in"] is False
    assert dummy_state["weather"] is None
    assert dummy_state["plan"] is None
    assert rerun_calls == ["rerun"]


def test_create_default_profile_has_expected_values() -> None:
    profile = ui_helpers.create_default_profile()

    assert profile.name == "Emergency Guest"
    assert profile.city == "Mumbai"
    assert profile.pets is False


def test_apply_custom_css_emits_styles(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = []
    monkeypatch.setattr(ui_helpers.st, "markdown", lambda content, unsafe_allow_html=False: rendered.append((content, unsafe_allow_html)))

    ui_helpers.apply_custom_css()

    assert rendered
    assert rendered[0][1] is True
    assert ".glass-card" in rendered[0][0]


def test_emergency_notification_bar_renders_for_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = []
    monkeypatch.setattr(ui_helpers.st, "markdown", lambda content, unsafe_allow_html=False: rendered.append((content, unsafe_allow_html)))

    emergency_notification_bar({"alert_level": "Red Alert"})

    assert rendered
    assert "EMERGENCY FLASH" in rendered[0][0]


def test_emergency_notification_bar_handles_other_alert_levels(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = []
    monkeypatch.setattr(ui_helpers.st, "markdown", lambda content, unsafe_allow_html=False: rendered.append((content, unsafe_allow_html)))

    emergency_notification_bar({"alert_level": "Yellow Alert"})

    assert rendered
    assert "STATUS NOTICE" in rendered[0][0]


def test_planner_prompt_contains_expected_fields() -> None:
    prompt = PLANNER_PROMPT.format(
        name="Asha",
        city="Mumbai",
        family_members=3,
        children=1,
        senior_citizens=1,
        pets_status="Yes",
        medical_conditions="Diabetes",
        temperature=31,
        rain_probability=80,
        wind_speed=25,
        humidity=90,
        conditions="Heavy Rain",
        alert_level="Orange Alert",
    )

    assert "Asha" in prompt
    assert "Mumbai" in prompt
    assert '"preparation"' in prompt


def test_checklist_and_chat_prompts_are_generated() -> None:
    checklist_prompt = CHECKLIST_PROMPT.format(
        city="Mumbai",
        family_members=3,
        children=1,
        senior_citizens=1,
        pets_status="Yes",
        medical_conditions="Diabetes",
        alert_level="Orange Alert",
    )
    chat_prompt = CHAT_SYSTEM_PROMPT.format(
        name="Asha",
        city="Mumbai",
        medical_conditions="Diabetes",
        alert_level="Orange Alert",
    )

    assert "checklist" in checklist_prompt.lower()
    assert "Asha" in chat_prompt
    assert "Orange Alert" in chat_prompt


def test_generate_preparedness_plan_uses_structured_output(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    monkeypatch.setattr(
        llm_service,
        "get_llm_client",
        lambda: FakeStructuredLLM({"preparation": ["secure windows"], "food": [], "medicines": [], "emergency_kit": [], "travel_advice": [], "safety_tips": []}),
    )

    plan = LLMService.generate_preparedness_plan(sample_profile, {"alert_level": "Orange Alert"})

    assert plan["preparation"] == ["secure windows"]


def test_generate_preparedness_plan_falls_back_to_json(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    monkeypatch.setattr(llm_service, "get_llm_client", lambda: FakeJSONLLM('{"preparation": ["prepare food"], "food": [], "medicines": [], "emergency_kit": [], "travel_advice": [], "safety_tips": []}'))

    plan = LLMService.generate_preparedness_plan(sample_profile, {"alert_level": "Orange Alert"})

    assert plan["preparation"] == ["prepare food"]


def test_generate_checklist_returns_sanitized_items(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    monkeypatch.setattr(
        llm_service,
        "get_llm_client",
        lambda: FakeJSONLLM('[{"task": "Store water", "category": "Food/Water"}]'),
    )

    checklist = LLMService.generate_checklist(sample_profile, {"alert_level": "Orange Alert"})

    assert checklist[0]["task"] == "Store water"
    assert checklist[0]["completed"] is False


def test_generate_checklist_returns_fallback_on_error(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    class BrokenLLM:
        def invoke(self, messages):
            raise RuntimeError("boom")

    monkeypatch.setattr(llm_service, "get_llm_client", lambda: BrokenLLM())

    checklist = LLMService.generate_checklist(sample_profile, {"alert_level": "Orange Alert"})

    assert checklist[0]["category"] == "General"


def test_stream_chat_yields_content(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    monkeypatch.setattr(llm_service, "get_llm_client", lambda: FakeStreamLLM("hello from stream"))

    chunks = list(LLMService.stream_chat(sample_profile, {"alert_level": "Orange Alert"}, []))

    assert chunks == ["hello from stream"]


def test_stream_chat_returns_error_message(monkeypatch: pytest.MonkeyPatch, sample_profile: UserProfile) -> None:
    class BrokenStreamLLM:
        def stream(self, messages):
            raise RuntimeError("stream failed")

    monkeypatch.setattr(llm_service, "get_llm_client", lambda: BrokenStreamLLM())

    chunks = list(LLMService.stream_chat(sample_profile, {"alert_level": "Orange Alert"}, []))

    assert chunks and "Error" in chunks[0]
