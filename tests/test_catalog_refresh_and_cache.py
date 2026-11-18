import hmac
import sys
import time
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import app.domains.chat.infrastructure.catalog_index as catalog_index_module
from app.domains.chat.infrastructure.gemini_client import GeminiChatDecision
from app.domains.chat.schemas.chat_dto import ChatRequest
from app.domains.chat.services.cache_service import ConversationCacheService
from app.domains.chat.services.chat_orchestrator import ChatOrchestrator
from app.main import app


client = TestClient(app)


def _mock_psycopg2_with_products(monkeypatch, products_rows, categories_rows=None, suppliers_rows=None):
    categories = categories_rows if categories_rows is not None else [("cat-1", "Suplementos", "suplementos")]
    suppliers = suppliers_rows if suppliers_rows is not None else [("sup-1", "Probiotica", "probiotica")]

    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [categories, suppliers, products_rows]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    fake_psycopg2 = MagicMock()
    fake_psycopg2.connect.return_value = mock_conn

    monkeypatch.setitem(sys.modules, "psycopg2", fake_psycopg2)
    if hasattr(catalog_index_module, "psycopg2"):
        monkeypatch.setattr(catalog_index_module, "psycopg2", fake_psycopg2)

    return fake_psycopg2, mock_conn


class TestConversationCacheServiceVersioning:
    """Versionamento por catalog_version e invalidacao contra race condition."""

    def setup_method(self):
        ConversationCacheService.clear()

    def test_cache_key_isolated_by_catalog_version(self):
        # Arrange
        payload_v1 = {"reply": "Whey v1", "intent": "PRODUCT_SEARCH"}

        # Act
        ConversationCacheService.set("quais opcoes de whey?", payload_v1, catalog_version=1)
        hit_v1 = ConversationCacheService.get("quais opcoes de whey?", catalog_version=1)
        miss_v2 = ConversationCacheService.get("quais opcoes de whey?", catalog_version=2)

        # Assert
        assert hit_v1 == payload_v1
        assert miss_v2 is None

    def test_bump_catalog_version_increments_and_invalidates_existing_entries(self):
        # Arrange
        version_before = ConversationCacheService.get_catalog_version()
        ConversationCacheService.set("creatina 300g", {"reply": "Creatina", "intent": "PRODUCT_SEARCH"})
        assert ConversationCacheService.get("creatina 300g") is not None

        # Act
        version_after = ConversationCacheService.bump_catalog_version()
        after_bump = ConversationCacheService.get("creatina 300g")

        # Assert
        assert version_after == version_before + 1
        assert ConversationCacheService.get_catalog_version() == version_after
        assert after_bump is None

    def test_inflight_stale_write_for_old_catalog_version_cannot_pollute_new_version(self):
        # Arrange
        v_start = ConversationCacheService.get_catalog_version()
        v_new = ConversationCacheService.bump_catalog_version()

        # Act: requisicao em voo capturou v_start e tenta gravar depois do refresh
        ConversationCacheService.set(
            "produto recem inativado",
            {"reply": "Produto antigo", "intent": "PRODUCT_SEARCH"},
            catalog_version=v_start,
        )
        current_hit = ConversationCacheService.get("produto recem inativado")

        # Assert
        assert v_new > v_start
        assert current_hit is None

    def test_cache_respects_ttl_expiration(self):
        # Arrange
        ConversationCacheService.set("expira rapido", {"reply": "ok", "intent": "GENERAL_QUERY"}, ttl_seconds=0)
        time.sleep(0.02)

        # Act
        res = ConversationCacheService.get("expira rapido")

        # Assert
        assert res is None


class TestCatalogRefreshEndpoint:
    """Contrato do endpoint POST /api/v1/chat/catalog/refresh e /health."""

    def setup_method(self):
        ConversationCacheService.clear()

    def test_refresh_returns_503_fail_closed_when_env_token_not_configured(self, monkeypatch):
        # Arrange
        monkeypatch.delenv("INTERNAL_REFRESH_TOKEN", raising=False)

        # Act
        response = client.post(
            "/api/v1/chat/catalog/refresh",
            headers={"X-Internal-Refresh-Token": "any-token"},
            json={"reason": "DAILY_ERP_SYNC"},
        )

        # Assert
        assert response.status_code == 503
        assert "REFRESH_TOKEN_NOT_CONFIGURED" in response.text

    def test_refresh_returns_503_fail_closed_when_env_token_blank(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "   ")

        # Act
        response = client.post(
            "/api/v1/chat/catalog/refresh",
            headers={"X-Internal-Refresh-Token": "   "},
        )

        # Assert
        assert response.status_code == 503
        assert "REFRESH_TOKEN_NOT_CONFIGURED" in response.text

    def test_refresh_returns_401_when_header_missing_or_wrong_header_name_used(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "super-secret-internal-token")

        # Act
        resp_missing = client.post("/api/v1/chat/catalog/refresh")
        resp_wrong_header = client.post(
            "/api/v1/chat/catalog/refresh",
            headers={"X-Refresh-Signature": "super-secret-internal-token"},
        )
        resp_query_param = client.post(
            "/api/v1/chat/catalog/refresh?token=super-secret-internal-token"
        )

        # Assert
        for resp in (resp_missing, resp_wrong_header, resp_query_param):
            assert resp.status_code == 401
            assert "MISSING_REFRESH_TOKEN" in resp.text

    def test_refresh_returns_403_when_token_invalid_and_uses_constant_time_compare(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "super-secret-internal-token")

        # Act
        with patch("hmac.compare_digest", wraps=hmac.compare_digest) as spy_compare:
            response = client.post(
                "/api/v1/chat/catalog/refresh",
                headers={"X-Internal-Refresh-Token": "wrong-token"},
            )

        # Assert
        assert response.status_code == 403
        assert "INVALID_REFRESH_TOKEN" in response.text
        assert spy_compare.called

    def test_refresh_returns_200_reloads_catalog_bumps_version_and_clears_cache(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "super-secret-internal-token")
        monkeypatch.setenv("POSTGRES_PASSWORD", "valid-db-pass")
        _mock_psycopg2_with_products(
            monkeypatch,
            products_rows=[
                (
                    "prod-10",
                    "Stevita Liquido",
                    "stevita-liquido",
                    None,
                    "Adocante",
                    [],
                    ["25ml", "60ml"],
                    "Naturais",
                    "naturais",
                    "Stevita",
                    "stevita",
                )
            ],
            categories_rows=[("cat-1", "Naturais", "naturais")],
            suppliers_rows=[("sup-1", "Stevita", "stevita")],
        )
        ConversationCacheService.set("stevita 25ml", {"reply": "cached", "intent": "PRODUCT_SEARCH"})
        version_before = ConversationCacheService.get_catalog_version()

        # Act
        with patch("hmac.compare_digest", wraps=hmac.compare_digest) as spy_compare:
            response = client.post(
                "/api/v1/chat/catalog/refresh",
                headers={"X-Internal-Refresh-Token": "super-secret-internal-token"},
                json={"reason": "DAILY_ERP_SYNC", "sync_run_id": "11111111-1111-1111-1111-111111111111"},
            )

        # Assert
        assert response.status_code == 200
        assert spy_compare.called
        body = response.json()
        data = body["data"]
        meta = body["meta"]

        assert data["refreshed"] is True
        assert data["catalog_items"] == 1
        assert data["categories_count"] == 1
        assert data["suppliers_count"] == 1
        assert data["cache_cleared"] is True
        assert data["catalog_version"] == version_before + 1
        assert data["refreshed_at"]

        assert meta["service"] == "fitoherb-ai-chat"
        assert meta["trigger_reason"] == "DAILY_ERP_SYNC"
        assert meta["tokens"] == {"prompt_tokens": 0, "completion_tokens": 0}

        # Cache antigo foi invalidado
        assert ConversationCacheService.get("stevita 25ml") is None

    def test_refresh_returns_503_and_preserves_snapshot_when_db_fails(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "super-secret-internal-token")
        monkeypatch.setenv("POSTGRES_PASSWORD", "valid-db-pass")

        from app.api.v1.routers.chat_router import get_orchestrator

        orchestrator = get_orchestrator()
        existing_snapshot = [
            {
                "name": "Produto Snapshot Anterior",
                "slug": "produto-snapshot-anterior",
                "image_url": None,
                "category": "Suplementos",
                "supplier": "Fitoherb",
                "flavours": [],
                "presentation": [],
            }
        ]
        orchestrator.catalog_index.set_catalog(products=existing_snapshot)
        version_before = ConversationCacheService.get_catalog_version()

        def _db_fail(*args, **kwargs):
            raise ConnectionError("postgres password=secret internal host=10.0.0.5")

        fake_psycopg2 = MagicMock()
        fake_psycopg2.connect.side_effect = _db_fail
        monkeypatch.setitem(sys.modules, "psycopg2", fake_psycopg2)
        if hasattr(catalog_index_module, "psycopg2"):
            monkeypatch.setattr(catalog_index_module, "psycopg2", fake_psycopg2)

        # Act
        response = client.post(
            "/api/v1/chat/catalog/refresh",
            headers={"X-Internal-Refresh-Token": "super-secret-internal-token"},
        )

        # Assert
        assert response.status_code == 503
        assert "CATALOG_REFRESH_FAILED" in response.text
        assert "10.0.0.5" not in response.text
        assert "password=secret" not in response.text
        assert orchestrator.catalog_index.products == existing_snapshot
        assert ConversationCacheService.get_catalog_version() == version_before

    def test_health_endpoint_exposes_catalog_version_and_last_refresh(self):
        # Arrange / Act
        response = client.get("/api/v1/chat/health")

        # Assert
        assert response.status_code == 200
        body = response.json()
        payload = body.get("data", body)
        assert "catalog_version" in payload
        assert "catalog_last_refresh" in payload

    def test_orchestrator_cache_invalidated_after_catalog_refresh_and_supports_null_image(
        self, monkeypatch
    ):
        # Arrange
        monkeypatch.setenv("INTERNAL_REFRESH_TOKEN", "super-secret-internal-token")
        monkeypatch.setenv("POSTGRES_PASSWORD", "valid-db-pass")

        mock_gemini = MagicMock()
        mock_gemini.is_ready = True
        mock_gemini.model_name = "gemini-2.5-flash"
        mock_gemini.generate_chat_decision.return_value = GeminiChatDecision(
            reply="Temos opcoes de creatina no catalogo.",
            should_redirect=True,
            catalog_search="creatina",
        )

        from app.api.v1.routers.chat_router import get_orchestrator

        orchestrator = get_orchestrator()
        monkeypatch.setattr(orchestrator, "gemini_client", mock_gemini)
        orchestrator.catalog_index.set_catalog(
            products=[
                {
                    "name": "Creatina Antiga",
                    "slug": "creatina-antiga",
                    "image_url": "/uploads/products/old.png",
                    "category": "Suplementos",
                    "supplier": "Fitoherb",
                    "flavours": [],
                    "presentation": ["300g"],
                }
            ]
        )

        # Primeira chamada popula cache L1
        first_res = orchestrator.process_message(ChatRequest(message="Tem creatina 300g?"))
        assert first_res.meta["cache"] == "MISS"
        assert first_res.data.products[0].slug == "creatina-antiga"

        # Segunda chamada acerta cache L1
        second_res = orchestrator.process_message(ChatRequest(message="Tem creatina 300g?"))
        assert second_res.meta["cache"] == "HIT"

        # Refresh troca catalogo para produto novo sem imagem (P-412)
        _mock_psycopg2_with_products(
            monkeypatch,
            products_rows=[
                (
                    "prod-20",
                    "Creatina Nova Sem Foto",
                    "creatina-nova-sem-foto",
                    None,
                    "Creatina monohidratada",
                    [],
                    ["300g"],
                    "Suplementos",
                    "suplementos",
                    "Fitoherb",
                    "fitoherb",
                )
            ],
        )
        refresh_resp = client.post(
            "/api/v1/chat/catalog/refresh",
            headers={"X-Internal-Refresh-Token": "super-secret-internal-token"},
        )
        assert refresh_resp.status_code == 200

        # Act: terceira chamada nao pode servir cache stale e deve aceitar image_url=None
        third_res = orchestrator.process_message(ChatRequest(message="Tem creatina 300g?"))

        # Assert
        assert third_res.meta["cache"] == "MISS"
        assert len(third_res.data.products) == 1
        assert third_res.data.products[0].slug == "creatina-nova-sem-foto"
        assert third_res.data.products[0].image_url is None
