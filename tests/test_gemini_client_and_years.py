from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import sys

import pytest

from app.domains.chat.services.company_metrics import (
    FITOHERB_FOUNDING_DATE,
    get_fitoherb_years,
    get_fitoherb_years_label,
    parse_founding_date,
)
from app.domains.chat.services.intent_router import IntentRouter
from app.domains.chat.infrastructure.gemini_client import (
    CANDIDATE_FLASH_MODELS,
    CANDIDATE_MODELS,
    DEFAULT_FLASH_MODEL,
    DEFAULT_MODEL,
    FALLBACK_FLASH_MODELS,
    PRIMARY_MODEL,
    GeminiChatDecision,
    GeminiClient,
    _build_thinking_config,
)


# ---------------------------------------------------------------------------
# Entrega 1 — Contagem Automática de Anos da Fitoherb (Fundação: 01/11/1997)
# ---------------------------------------------------------------------------


def test_fitoherb_founding_date_constant():
    assert FITOHERB_FOUNDING_DATE == date(1997, 11, 1)


@pytest.mark.parametrize(
    "reference_date,expected_years",
    [
        (date(2026, 10, 31), 28),
        (date(2026, 11, 1), 29),
        (date(2026, 11, 23), 29),
        (date(2027, 10, 31), 29),
        (date(2027, 11, 1), 30),
        (date(1997, 10, 31), 0),
        (date(1990, 1, 1), 0),
    ],
)
def test_get_fitoherb_years_boundaries(reference_date: date, expected_years: int):
    assert get_fitoherb_years(reference_date=reference_date) == expected_years


def test_get_fitoherb_years_label():
    assert get_fitoherb_years_label(reference_date=date(2026, 11, 23)) == "29 anos de mercado"
    assert get_fitoherb_years_label(reference_date=date(2027, 11, 1)) == "30 anos de mercado"


def test_parse_founding_date_valid_and_fallback():
    assert parse_founding_date("1997-11-01") == date(1997, 11, 1)
    assert parse_founding_date("2000-05-15") == date(2000, 5, 15)
    assert parse_founding_date(None) == FITOHERB_FOUNDING_DATE
    assert parse_founding_date("") == FITOHERB_FOUNDING_DATE
    assert parse_founding_date("invalid-date") == FITOHERB_FOUNDING_DATE


def test_intent_router_company_about_uses_dynamic_years():
    router = IntentRouter()

    res_2026 = router.route_static("Quem é a Fitoherb?", reference_date=date(2026, 11, 23))
    assert res_2026 is not None
    reply_2026, intent_2026 = res_2026
    assert intent_2026 == "COMPANY_ABOUT"
    assert "29 anos" in reply_2026
    assert "28 anos" not in reply_2026

    res_2027 = router.route_static("Quem é a Fitoherb?", reference_date=date(2027, 11, 1))
    assert res_2027 is not None
    reply_2027, intent_2027 = res_2027
    assert intent_2027 == "COMPANY_ABOUT"
    assert "30 anos" in reply_2027


# ---------------------------------------------------------------------------
# Entrega 2 — Gemini 4 Hydrogen Principal + Fallback Família Flash
# ---------------------------------------------------------------------------


def test_gemini_model_constants_and_backward_compatibility():
    assert PRIMARY_MODEL == "gemini-4-hydrogen"
    assert DEFAULT_MODEL == "gemini-4-hydrogen"
    assert DEFAULT_FLASH_MODEL == "gemini-4-hydrogen"
    assert CANDIDATE_MODELS[0] == "gemini-4-hydrogen"
    assert CANDIDATE_MODELS[1] == "gemini-3.8-flash"
    assert CANDIDATE_MODELS[2] == "gemini-flash-latest"
    assert FALLBACK_FLASH_MODELS == CANDIDATE_FLASH_MODELS
    assert CANDIDATE_MODELS == [PRIMARY_MODEL, *FALLBACK_FLASH_MODELS]


def _make_fake_google_modules(list_models_return=None, generate_side_effect=None):
    """Cria módulos fake de google / google.genai / google.genai.types para testes isolados."""
    captured_thinking_calls = []
    captured_config_calls = []

    class FakeThinkingConfig:
        model_fields = {"thinking_level": None, "thinking_budget": None}

        def __init__(self, **kwargs):
            captured_thinking_calls.append(kwargs)
            self.kwargs = kwargs

    class FakeGenerateContentConfig:
        def __init__(self, **kwargs):
            captured_config_calls.append(kwargs)
            self.kwargs = kwargs

    class FakePart:
        @staticmethod
        def from_text(text: str):
            return SimpleNamespace(text=text)

    class FakeContent:
        def __init__(self, role: str, parts):
            self.role = role
            self.parts = parts

    fake_types = SimpleNamespace(
        ThinkingConfig=FakeThinkingConfig,
        GenerateContentConfig=FakeGenerateContentConfig,
        Part=FakePart,
        Content=FakeContent,
    )

    fake_models_api = MagicMock()
    if list_models_return is not None:
        fake_models_api.list.return_value = list_models_return
    else:
        fake_models_api.list.return_value = []

    if generate_side_effect is not None:
        fake_models_api.generate_content.side_effect = generate_side_effect

    fake_client_instance = SimpleNamespace(models=fake_models_api)

    class FakeGenaiClient:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.models = fake_client_instance.models

    fake_genai = SimpleNamespace(Client=FakeGenaiClient, types=fake_types)
    fake_google = SimpleNamespace(genai=fake_genai)

    return {
        "modules": {
            "google": fake_google,
            "google.genai": fake_genai,
            "google.genai.types": fake_types,
        },
        "models_api": fake_models_api,
        "thinking_calls": captured_thinking_calls,
        "config_calls": captured_config_calls,
        "types": fake_types,
    }


def test_init_client_prioritizes_gemini_4_hydrogen_over_flash():
    remote_models = [
        SimpleNamespace(name="models/gemini-3.8-flash"),
        SimpleNamespace(name="models/gemini-flash-latest"),
        SimpleNamespace(name="models/gemini-4-hydrogen-tts"),
        SimpleNamespace(name="models/gemini-4-hydrogen-image"),
        SimpleNamespace(name="models/gemini-4-hydrogen"),
    ]
    fake_env = _make_fake_google_modules(list_models_return=remote_models)

    with patch.dict(sys.modules, fake_env["modules"]):
        client = GeminiClient(api_key="test-key")

    assert client.is_ready is True
    assert client.model_name == "gemini-4-hydrogen"


def test_init_client_falls_back_to_flash_when_hydrogen_absent_in_remote_list():
    remote_models = [
        SimpleNamespace(name="models/gemini-3.7-flash"),
        SimpleNamespace(name="models/gemini-3.8-flash"),
    ]
    fake_env = _make_fake_google_modules(list_models_return=remote_models)

    with patch.dict(sys.modules, fake_env["modules"]):
        client = GeminiClient(api_key="test-key")

    assert client.is_ready is True
    assert client.model_name == "gemini-3.8-flash"


def test_fallback_order_hydrogen_to_38_flash_to_flash_latest_and_no_thinking_budget_zero():
    called_models = []

    def side_effect(model, contents, config):
        called_models.append((model, config))
        if model in ("gemini-4-hydrogen", "gemini-3.8-flash"):
            raise RuntimeError(f"Model {model} unavailable")
        return SimpleNamespace(
            text='{"reply": "Temos opções de creatina.", "should_redirect": true, "catalog_search": "creatina"}'
        )

    fake_env = _make_fake_google_modules(
        list_models_return=[SimpleNamespace(name="models/gemini-4-hydrogen")],
        generate_side_effect=side_effect,
    )

    with patch.dict(sys.modules, fake_env["modules"]):
        client = GeminiClient(api_key="test-key")
        decision = client.generate_chat_decision(
            system_instruction="Assistente Fitoherb",
            user_message="Quero creatina",
        )

    assert isinstance(decision, GeminiChatDecision)
    assert decision.should_redirect is True
    assert decision.catalog_search == "creatina"

    # Ordem exata de fallback: gemini-4-hydrogen -> gemini-3.8-flash -> gemini-flash-latest
    assert [m for m, _ in called_models] == [
        "gemini-4-hydrogen",
        "gemini-3.8-flash",
        "gemini-flash-latest",
    ]
    # Cliente migra dinamicamente para o modelo que respondeu com sucesso
    assert client.model_name == "gemini-flash-latest"

    # Garantia absoluta: thinking_budget=0 NUNCA é enviado para gemini-4-hydrogen ou 3.x
    for call_kwargs in fake_env["thinking_calls"]:
        assert "thinking_budget" not in call_kwargs
        assert call_kwargs.get("thinking_level") == "low"


def test_build_thinking_config_never_passes_thinking_budget_zero_to_hydrogen():
    class ModernThinkingConfig:
        model_fields = {"thinking_level": None, "thinking_budget": None}

        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class LegacyOnlyThinkingConfig:
        model_fields = {"thinking_budget": None}

        def __init__(self, **kwargs):
            self.kwargs = kwargs

    modern_types = SimpleNamespace(ThinkingConfig=ModernThinkingConfig)
    legacy_types = SimpleNamespace(ThinkingConfig=LegacyOnlyThinkingConfig)

    # SDK moderno + Gemini 4 Hydrogen -> thinking_level="low", sem thinking_budget
    cfg_hydrogen = _build_thinking_config("gemini-4-hydrogen", modern_types)
    assert cfg_hydrogen is not None
    assert cfg_hydrogen.kwargs == {"thinking_level": "low"}

    # SDK antigo sem thinking_level + Gemini 4 Hydrogen -> None (omite thinking_config)
    cfg_hydrogen_old_sdk = _build_thinking_config("gemini-4-hydrogen", legacy_types)
    assert cfg_hydrogen_old_sdk is None

    # Modelo legado Gemini 2.5 -> thinking_budget=0
    cfg_25 = _build_thinking_config("gemini-2.5-flash", modern_types)
    assert cfg_25 is not None
    assert cfg_25.kwargs == {"thinking_budget": 0}
