import inspect
import re
import sys
from unittest.mock import MagicMock

import pytest

import app.domains.chat.infrastructure.catalog_index as catalog_index_module
from app.domains.chat.infrastructure.catalog_index import CatalogIndex
from app.domains.chat.schemas.chat_dto import ProductSnippetDto


def _install_fake_psycopg2(monkeypatch, cursor_side_effect=None, fetchall_results=None):
    """Instala um stub em memoria para psycopg2 sem tocar banco real."""
    executed_queries = []
    mock_cursor = MagicMock()

    def _execute(sql, *args, **kwargs):
        executed_queries.append(sql)
        if cursor_side_effect is not None:
            cursor_side_effect(sql, *args, **kwargs)

    mock_cursor.execute.side_effect = _execute
    if fetchall_results is not None:
        mock_cursor.fetchall.side_effect = fetchall_results
    else:
        mock_cursor.fetchall.return_value = []

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    fake_psycopg2 = MagicMock()
    fake_psycopg2.connect.return_value = mock_conn

    monkeypatch.setitem(sys.modules, "psycopg2", fake_psycopg2)
    if hasattr(catalog_index_module, "psycopg2"):
        monkeypatch.setattr(catalog_index_module, "psycopg2", fake_psycopg2)

    return fake_psycopg2, mock_conn, mock_cursor, executed_queries


class TestCatalogIndexCredentialsAndSecurity:
    """Invariantes de credencial fail-closed e privacidade P-408."""

    def test_load_from_db_fails_closed_when_postgres_password_missing(self, monkeypatch):
        # Arrange
        monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
        monkeypatch.delenv("PostgresPassword", raising=False)
        fake_psycopg2, _, _, _ = _install_fake_psycopg2(monkeypatch)
        index = CatalogIndex(auto_load_db=False)

        # Act
        loaded = index.load_from_db()

        # Assert
        assert loaded is False
        fake_psycopg2.connect.assert_not_called()

    def test_load_from_db_fails_closed_when_postgres_password_blank(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("POSTGRES_PASSWORD", "   ")
        monkeypatch.delenv("PostgresPassword", raising=False)
        fake_psycopg2, _, _, _ = _install_fake_psycopg2(monkeypatch)
        index = CatalogIndex(auto_load_db=False)

        # Act
        loaded = index.load_from_db()

        # Assert
        assert loaded is False
        fake_psycopg2.connect.assert_not_called()

    def test_catalog_index_source_contains_no_hardcoded_password(self):
        # Arrange
        source = inspect.getsource(catalog_index_module)

        # Assert
        assert "Dm120394" not in source

    def test_load_from_db_reads_postgres_password_from_env_and_never_logs_secret(
        self, monkeypatch, caplog
    ):
        # Arrange
        secret_pwd = "S3cur3_Env_Pass!"
        monkeypatch.setenv("POSTGRES_PASSWORD", secret_pwd)
        monkeypatch.delenv("PostgresPassword", raising=False)
        fake_psycopg2, mock_conn, _, _ = _install_fake_psycopg2(
            monkeypatch,
            fetchall_results=[[], [], []],
        )
        index = CatalogIndex(auto_load_db=False)

        # Act
        with caplog.at_level("DEBUG"):
            loaded = index.load_from_db()

        # Assert
        assert loaded is True
        fake_psycopg2.connect.assert_called_once()
        assert fake_psycopg2.connect.call_args.kwargs["password"] == secret_pwd
        assert secret_pwd not in caplog.text
        mock_conn.close.assert_called_once()


class TestCatalogIndexActiveFilterAndPrivacy:
    """Regras P-408, P-411 e P-412 na carga e exposicao do catalogo."""

    def test_load_from_db_filters_active_products_and_forbids_erp_tables(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("POSTGRES_PASSWORD", "valid-test-pass")
        categories_rows = [("cat-1", "Suplementos", "suplementos")]
        suppliers_rows = [("sup-1", "Probiotica", "probiotica")]
        products_rows = [
            (
                "prod-1",
                "100% Pure Whey 900g",
                "100-pure-whey-900g",
                None,
                "Proteina concentrada",
                ["Baunilha", "Chocolate", "Morango"],
                ["900g"],
                "Suplementos",
                "suplementos",
                "Probiotica",
                "probiotica",
            )
        ]
        _, mock_conn, _, executed_queries = _install_fake_psycopg2(
            monkeypatch,
            fetchall_results=[categories_rows, suppliers_rows, products_rows],
        )
        index = CatalogIndex(auto_load_db=False)

        # Act
        loaded = index.load_from_db()

        # Assert
        assert loaded is True
        assert len(index.products) == 1
        assert index.products[0]["image_url"] is None

        all_sql = "\n".join(executed_queries)
        assert re.search(
            r"COALESCE\s*\(\s*p\.active\s*,\s*TRUE\s*\)\s*=\s*TRUE",
            all_sql,
            flags=re.IGNORECASE,
        ), f"Query SQL deve filtrar COALESCE(p.active, TRUE) = TRUE. Recebido: {all_sql}"

        forbidden_tokens = [
            "product_skus",
            "erp_catalog_items",
            "erp_ignored_catalog_codes",
            "erp_sync_runs",
            "erp_code",
            "id_pro",
            "inativo_pro",
            "estoque",
            "created_by",
            "updated_by",
            "ignored_by",
            "users",
        ]
        all_sql_lower = all_sql.lower()
        for token in forbidden_tokens:
            assert token not in all_sql_lower

        product_keys = set(index.products[0].keys())
        assert product_keys.isdisjoint(
            {"erp_code", "erpCode", "id_pro", "inativo_pro", "erp_inactive", "estoque", "skus"}
        )
        mock_conn.close.assert_called_once()

    def test_load_from_db_closes_connection_and_preserves_snapshot_on_query_error(
        self, monkeypatch
    ):
        # Arrange
        monkeypatch.setenv("POSTGRES_PASSWORD", "valid-test-pass")
        initial_products = [
            {
                "name": "Creatina Creapure 300g",
                "slug": "creatina-creapure-300g",
                "image_url": "/uploads/products/creatina.png",
                "category": "Suplementos",
                "supplier": "Max Titanium",
                "flavours": [],
                "presentation": ["300g"],
            }
        ]
        index = CatalogIndex(auto_load_db=False)
        index.set_catalog(products=initial_products)
        version_before = index.catalog_version

        def _boom(sql, *args, **kwargs):
            raise RuntimeError("Simulated PostgreSQL transient error")

        _, mock_conn, _, _ = _install_fake_psycopg2(monkeypatch, cursor_side_effect=_boom)

        # Act
        loaded = index.load_from_db()

        # Assert
        assert loaded is False
        assert index.products == initial_products
        assert index.catalog_version == version_before
        mock_conn.close.assert_called_once()

    def test_product_snippet_dto_allows_null_image_url_and_excludes_erp_fields(self):
        # Arrange / Act
        dto = ProductSnippetDto(
            name="Novo Produto ERP Sem Foto",
            slug="novo-produto-erp-sem-foto",
            image_url=None,
            category="Suplementos",
            supplier="Fitoherb",
        )

        # Assert
        assert dto.image_url is None
        field_names = set(ProductSnippetDto.model_fields.keys())
        assert field_names.isdisjoint(
            {"erp_code", "erpCode", "id_pro", "inativo_pro", "erp_inactive", "estoque", "skus"}
        )


class TestCatalogIndexUnitNormalizationAndRecall:
    """Normalizacao de unidades/sabores/apresentacoes e neutralidade P-304/P-305."""

    @pytest.fixture
    def catalog_with_variants(self) -> CatalogIndex:
        index = CatalogIndex(auto_load_db=False)
        index.set_catalog(
            products=[
                {
                    "name": "Stevita Liquido Pequeno",
                    "slug": "stevita-liquido-25ml",
                    "image_url": "/uploads/products/stevita-25.png",
                    "description": "Adocante natural liquido",
                    "flavours": [],
                    "presentation": ["25ml"],
                    "category": "Naturais",
                    "supplier": "Stevita",
                },
                {
                    "name": "Stevita Liquido Grande",
                    "slug": "stevita-liquido-60ml",
                    "image_url": "/uploads/products/stevita-60.png",
                    "description": "Adocante natural liquido",
                    "flavours": [],
                    "presentation": ["60ml"],
                    "category": "Naturais",
                    "supplier": "Stevita",
                },
                {
                    "name": "B.O.P.E",
                    "slug": "bope-pre-treino",
                    "image_url": "/uploads/products/bope.png",
                    "description": "Pre treino matriz sabor e apresentacao",
                    "flavours": ["Fruit Punch", "Limao", "Uva"],
                    "presentation": ["150g", "300g"],
                    "category": "Suplementos",
                    "supplier": "Black Skull",
                },
                {
                    "name": "Omega 3 Softgel",
                    "slug": "omega-3-120-caps",
                    "image_url": "/uploads/products/omega-120.png",
                    "description": "Oleo de peixe purificado",
                    "flavours": [],
                    "presentation": ["120 cápsulas"],
                    "category": "Vitaminas",
                    "supplier": "Vital Atman",
                },
                {
                    "name": "Omega 3 Softgel",
                    "slug": "omega-3-60-caps",
                    "image_url": None,
                    "description": "Oleo de peixe purificado",
                    "flavours": [],
                    "presentation": ["60 cápsulas"],
                    "category": "Vitaminas",
                    "supplier": "Vital Atman",
                },
                {
                    "name": "Vitamina C Pura",
                    "slug": "vitamina-c-1000mg",
                    "image_url": "/uploads/products/vitc-1000.png",
                    "description": "Acido ascorbico",
                    "flavours": ["Laranja"],
                    "presentation": ["1000mg", "120 caps"],
                    "category": "Vitaminas",
                    "supplier": "Unilife",
                },
                {
                    "name": "Vitamina C Pura",
                    "slug": "vitamina-c-500mg",
                    "image_url": "/uploads/products/vitc.png",
                    "description": "Acido ascorbico",
                    "flavours": ["Laranja"],
                    "presentation": ["500mg", "60 caps"],
                    "category": "Vitaminas",
                    "supplier": "Unilife",
                },
                {
                    "name": "100% Pure Whey",
                    "slug": "100-pure-whey-probiotica",
                    "image_url": "/uploads/products/whey-prob.png",
                    "description": "Proteina concentrada",
                    "flavours": ["Morango", "Chocolate"],
                    "presentation": ["900g"],
                    "category": "Suplementos",
                    "supplier": "Probiotica",
                },
                {
                    "name": "Whey 100% Gold",
                    "slug": "whey-100-gold-max",
                    "image_url": "/uploads/products/whey-max.png",
                    "description": "Proteina do soro do leite",
                    "flavours": ["Morango", "Baunilha"],
                    "presentation": ["900g"],
                    "category": "Suplementos",
                    "supplier": "Max Titanium",
                },
            ],
            categories=[
                {"id": "1", "name": "Suplementos", "slug": "suplementos"},
                {"id": "2", "name": "Naturais", "slug": "naturais"},
                {"id": "3", "name": "Vitaminas", "slug": "vitaminas"},
            ],
            suppliers=[
                {"id": "1", "name": "Probiotica", "slug": "probiotica"},
                {"id": "2", "name": "Max Titanium", "slug": "max-titanium"},
                {"id": "3", "name": "Black Skull", "slug": "black-skull"},
            ],
        )
        return index

    @pytest.mark.parametrize(
        ("query", "expected_slug"),
        [
            ("stevita 60 ml", "stevita-liquido-60ml"),
            ("stevita 25 ml", "stevita-liquido-25ml"),
            ("bope 300 g uva", "bope-pre-treino"),
            ("bope 150g limao", "bope-pre-treino"),
            ("omega 3 60 caps", "omega-3-60-caps"),
            ("omega 3 60caps", "omega-3-60-caps"),
            ("vitamina c 500 mg", "vitamina-c-500mg"),
            ("vitamina c 60 cápsulas", "vitamina-c-500mg"),
        ],
    )
    def test_search_normalizes_units_presentations_and_flavours_for_recall(
        self, catalog_with_variants: CatalogIndex, query: str, expected_slug: str
    ):
        # Arrange
        index = catalog_with_variants

        # Act
        results, filters = index.search(query, limit=5)

        # Assert
        assert len(results) >= 1
        assert results[0]["slug"] == expected_slug
        assert filters["search"]
        for item in results:
            assert "erp_code" not in item
            assert "id_pro" not in item
            assert "inativo_pro" not in item

    def test_search_preserves_supplier_diversity_p304_for_flavour_and_grammage(
        self, catalog_with_variants: CatalogIndex
    ):
        # Arrange
        index = catalog_with_variants

        # Act
        results, _ = index.search("whey 900 g morango", limit=5)

        # Assert
        returned_slugs = [p["slug"] for p in results]
        returned_suppliers = {p["supplier"] for p in results}
        assert "100-pure-whey-probiotica" in returned_slugs
        assert "whey-100-gold-max" in returned_slugs
        assert len(returned_suppliers) >= 2

    def test_search_handles_empty_and_none_variant_lists_safely(self):
        # Arrange
        index = CatalogIndex(auto_load_db=False)
        index.set_catalog(
            products=[
                {
                    "name": "Cha Verde",
                    "slug": "cha-verde",
                    "flavours": None,
                    "presentation": None,
                    "category": "Chas",
                    "supplier": "Fitoherb",
                }
            ]
        )

        # Act
        empty_res, _ = index.search("   ")
        punct_res, _ = index.search("???!!!")
        valid_res, _ = index.search("cha verde")

        # Assert
        assert empty_res == []
        assert punct_res == []
        assert len(valid_res) == 1
        assert valid_res[0]["slug"] == "cha-verde"
