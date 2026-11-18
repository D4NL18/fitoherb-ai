import logging
import os
import re
import threading
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_UNIT_CANONICAL_PATTERNS = (
    (re.compile(r"\b(?:capsulas|capsula|capsgel|caps|cap|cps)\b"), "caps"),
    (re.compile(r"\b(?:comprimidos|comprimido|comps|comp)\b"), "comp"),
    (re.compile(r"\b(?:tabletes|tablete|tabs|tab)\b"), "tab"),
    (re.compile(r"\b(?:saches|sache)\b"), "sache"),
    (re.compile(r"\b(?:mililitros|mililitro|mls)\b"), "ml"),
    (re.compile(r"\b(?:miligramas|miligrama|mgs)\b"), "mg"),
    (re.compile(r"\b(?:microgramas|micrograma|mcgs|mcg)\b"), "mcg"),
    (re.compile(r"\b(?:quilogramas|quilograma|kilos|kilo|quilos|quilo|kgs)\b"), "kg"),
    (re.compile(r"\b(?:gramas|grama|grs|gr)\b"), "g"),
    (re.compile(r"\b(?:litros|litro|lts)\b"), "l"),
    (re.compile(r"\b(?:unidades|unidade|unids|unid|unds|und)\b"), "un"),
    (re.compile(r"\b(?:gota)\b"), "gotas"),
)

_ATTACH_UNIT_PATTERN = re.compile(
    r"\b(\d+)\s+(ml|mg|mcg|kg|g|l|caps|comp|tab|sache|gotas|un|ui)\b"
)


def normalize_text(text: str) -> str:
    """Normaliza texto removendo acentos, pontuacoes e unificando unidades/apresentacoes."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Colapsa siglas pontuadas como B.O.P.E -> bope sem alterar decimais numericos
    without_acronym_dots = re.sub(r"(?<=[a-z])\.(?=[a-z])", "", without_accents)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", without_acronym_dots)
    # Separa fronteiras digito/letra para normalizar ex: 60caps -> 60 caps
    separated = re.sub(r"(\d)([a-z])", r"\1 \2", cleaned)
    separated = re.sub(r"([a-z])(\d)", r"\1 \2", separated)
    separated = re.sub(r"\s+", " ", separated).strip()

    for pattern, canonical in _UNIT_CANONICAL_PATTERNS:
        separated = pattern.sub(canonical, separated)

    attached = _ATTACH_UNIT_PATTERN.sub(r"\1\2", separated)
    return re.sub(r"\s+", " ", attached).strip()


def extract_clean_search(query: str) -> str:
    cleaned = query.strip()
    patterns = [
        r"^(por\s+favor[,]?\s*)",
        r"^(eu\s+)?(quero|queria|gostaria\s+de)\s+(a\s+lista\s+de\s+|uma\s+lista\s+de\s+|o\s+catalogo\s+de\s+|o\s+catálogo\s+de\s+|ver\s+|saber\s+sobre\s+|conhecer\s+|comprar\s+|achar\s+|encontrar\s+)?(de|da|do)?\s*",
        r"^(quais\s+(as|os|sao|são)?\s*(as|os)?\s*(opcoes|opções)?\s*(de|da|do)?\s*)",
        r"^(tem\s+(algum|alguma|opcao|opção|opcoes|opções)?\s*(de|da|do)?\s*)",
        r"^(voces|vocês|voce|você)\s+tem\s+(algum|alguma|opcao|opção|opcoes|opções)?\s*(de|da|do)?\s*",
        r"^(me\s+(mostre|mostra|diga|fale\s+sobre|mande|passa)\s*(a\s+lista\s+de\s+|as\s+opcoes\s+de\s+|as\s+opções\s+de\s*)?)",
        r"^(mostrar\s+|listar\s+|lista\s+de\s+|catalogo\s+de\s+|catálogo\s+de\s*)",
        r"^(procuro\s+por\s+|estou\s+procurando\s*(por)?\s*)",
        r"^(onde\s+(acho|encontro|tem)\s*)",
    ]
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(a|o|as|os|de|da|do|dos|das|sobre)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip("?!.,; ")
    return cleaned if len(cleaned) >= 2 else query.strip().rstrip("?!.,; ")


class CatalogIndex:
    """
    Índice em memória para busca rápida no catálogo (P-304, P-305, P-408, P-411, P-412).
    Indexa nome, slug, categoria, fornecedor, sabores, apresentação e descrição.
    Carrega apenas produtos ativos diretamente do PostgreSQL (fail-closed sem senha hardcoded).
    """

    def __init__(self, auto_load_db: bool = True):
        self.auto_load_db = auto_load_db
        self._lock = threading.RLock()
        self.products: List[Dict[str, Any]] = []
        self.categories: List[Dict[str, str]] = []
        self.suppliers: List[Dict[str, str]] = []
        self.catalog_version: int = 1
        self.last_refresh: Optional[str] = None
        self._last_loaded_monotonic: Optional[float] = None
        self._last_attempt_monotonic: Optional[float] = None
        self._synonyms = {
            "whey": ["whey", "wey", "whei", "proteina", "proteina do soro"],
            "creatina": ["creatina", "creatine", "creatina creapure"],
            "colageno": ["colageno", "collagen", "peptideos"],
            "omega": ["omega", "omega 3", "oleo de peixe"],
            "mel": ["mel", "apicola", "propolis", "extrato de propolis"],
            "cha": ["cha", "infusao", "ervas"],
            "vitamina": ["vitamina", "multivitaminico", "complexo b", "vitamina c"],
        }
        if auto_load_db:
            self.load_from_db()

    @staticmethod
    def _resolve_db_password(explicit_password: Optional[str]) -> Optional[str]:
        if explicit_password is not None:
            return explicit_password if explicit_password.strip() else None
        for env_key in ("POSTGRES_PASSWORD", "PostgresPassword"):
            val = os.getenv(env_key)
            if val and val.strip():
                return val
        return None

    def load_from_db(
        self,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> bool:
        """
        Carrega produtos ativos, categorias e fornecedores diretamente do PostgreSQL.
        Fail-closed caso POSTGRES_PASSWORD / PostgresPassword não esteja configurada.
        """
        self._last_attempt_monotonic = time.monotonic()
        db_pass = self._resolve_db_password(password)
        if not db_pass:
            logger.warning("POSTGRES_PASSWORD não configurada; carga do CatalogIndex abortada (fail-closed).")
            return False

        conn = None
        try:
            import psycopg2

            db_name = dbname or os.getenv("POSTGRES_DB") or "fitoherb-v2"
            db_user = user or os.getenv("PostgresUsername") or os.getenv("POSTGRES_USER") or "postgres"
            db_host = host or os.getenv("POSTGRES_HOST") or "localhost"
            db_port = port or int(os.getenv("POSTGRES_PORT", "5432"))

            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                connect_timeout=3,
            )
            conn.set_client_encoding("UTF8")
            cur = conn.cursor()

            # Apenas facetas com produtos ativos (P-408, P-411)
            cur.execute("""
                SELECT c.id, c.name, c.slug
                FROM product_categories c
                WHERE EXISTS (
                    SELECT 1 FROM products p
                    WHERE p.category_id = c.id AND COALESCE(p.active, TRUE) = TRUE
                )
                ORDER BY c.name ASC;
            """)
            categories = [{"id": str(r[0]), "name": r[1], "slug": r[2]} for r in cur.fetchall()]

            cur.execute("""
                SELECT s.id, s.name, s.slug
                FROM suppliers s
                WHERE EXISTS (
                    SELECT 1 FROM products p
                    WHERE p.supplier_id = s.id AND COALESCE(p.active, TRUE) = TRUE
                )
                ORDER BY s.name ASC;
            """)
            suppliers = [{"id": str(r[0]), "name": r[1], "slug": r[2]} for r in cur.fetchall()]

            # Somente campos publicos de produtos ativos (P-408, P-411, P-412)
            cur.execute("""
                SELECT p.id, p.name, p.slug, p.image_path, p.description, p.flavours, p.presentation,
                       c.name as category_name, c.slug as category_slug,
                       s.name as supplier_name, s.slug as supplier_slug
                FROM products p
                LEFT JOIN product_categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE COALESCE(p.active, TRUE) = TRUE
                ORDER BY p.name ASC;
            """)
            products = []
            for r in cur.fetchall():
                products.append({
                    "id": str(r[0]),
                    "name": r[1] or "",
                    "slug": r[2] or "",
                    "image_url": f"/uploads/products/{r[3]}" if r[3] else None,
                    "description": r[4] or "",
                    "flavours": r[5] or [],
                    "presentation": r[6] or [],
                    "category": r[7] or "",
                    "category_slug": r[8] or "",
                    "supplier": r[9] or "",
                    "supplier_slug": r[10] or "",
                })

            self.set_catalog(products=products, categories=categories, suppliers=suppliers, bump_version=True)
            logger.info(
                "CatalogIndex populado com sucesso: %d produtos, %d categorias, %d fornecedores.",
                len(products),
                len(categories),
                len(suppliers),
            )
            return True
        except Exception as exc:
            logger.warning(
                "Não foi possível carregar catálogo diretamente do PostgreSQL (%s).",
                type(exc).__name__,
            )
            return False
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def set_catalog(
        self,
        products: List[Dict[str, Any]],
        categories: Optional[List[Dict[str, str]]] = None,
        suppliers: Optional[List[Dict[str, str]]] = None,
        bump_version: bool = False,
    ) -> None:
        with self._lock:
            self.products = list(products or [])
            self.categories = list(categories or [])
            self.suppliers = list(suppliers or [])
            if bump_version:
                self.catalog_version += 1
            self.last_refresh = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            self._last_loaded_monotonic = time.monotonic()

    def set_catalog_version(self, version: int) -> None:
        with self._lock:
            self.catalog_version = version

    def ensure_fresh(self, ttl_seconds: Optional[int] = None) -> bool:
        """Revalida passivamente o catalogo caso o TTL configuravel tenha expirado."""
        if not self.auto_load_db:
            return False
        ttl = ttl_seconds if ttl_seconds is not None else int(os.getenv("CATALOG_REFRESH_TTL_SECONDS", "3600"))
        with self._lock:
            ref = self._last_loaded_monotonic if self._last_loaded_monotonic is not None else self._last_attempt_monotonic
            if ref is not None and (time.monotonic() - ref) < ttl:
                return False
        return self.load_from_db()

    def search(self, query: str, limit: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executa busca por relevância e identifica facetas (categoria, fornecedor).
        Retorna (lista_produtos, filtros_detectados).
        """
        with self._lock:
            products_snapshot = list(self.products)
            categories_snapshot = list(self.categories)
            suppliers_snapshot = list(self.suppliers)

        norm_query = normalize_text(query)
        clean_search_text = extract_clean_search(query)
        detected_filters: Dict[str, Any] = {
            "category": [],
            "supplier": [],
            "search": clean_search_text,
        }

        if not norm_query:
            return [], detected_filters

        # 1. Checa correspondência com fornecedores e categorias conhecidas
        for cat in categories_snapshot:
            cat_norm = normalize_text(cat.get("name", ""))
            cat_slug = cat.get("slug", "")
            if cat_norm and (cat_norm in norm_query or cat_slug in norm_query):
                if cat_slug not in detected_filters["category"]:
                    detected_filters["category"].append(cat_slug)

        for sup in suppliers_snapshot:
            sup_norm = normalize_text(sup.get("name", ""))
            sup_slug = sup.get("slug", "")
            if sup_norm and (sup_norm in norm_query or sup_slug in norm_query):
                if sup_slug not in detected_filters["supplier"]:
                    detected_filters["supplier"].append(sup_slug)

        # 2. Extração de tokens principais e expansão controlada de sinônimos
        norm_clean = normalize_text(clean_search_text)
        stopwords = {
            "quais", "as", "os", "sao", "opcoes", "opcao",
            "de", "da", "do", "das", "dos", "para", "com", "em", "um", "uma", "tem",
            "voces", "voce", "sobre", "ver", "gostaria", "a", "o", "e", "u",
        }
        raw_tokens = norm_clean.split() if norm_clean else norm_query.split()
        core_tokens = [
            t for t in raw_tokens
            if t not in stopwords and (len(t) >= 2 or t.isalnum())
        ]
        if not core_tokens:
            core_tokens = [
                t for t in norm_query.split()
                if t not in stopwords and (len(t) >= 2 or t.isalnum())
            ]

        if not core_tokens:
            return [], detected_filters

        expanded_tokens = set(core_tokens)
        for token in core_tokens:
            for canon, syn_list in self._synonyms.items():
                if token in syn_list or token == canon:
                    expanded_tokens.add(canon)
                    expanded_tokens.update(syn_list)
        extra_synonyms = expanded_tokens - set(core_tokens)

        # 3. Score e ranqueamento considerando nome, sabores e apresentações normalizadas
        scored_products = []
        for p in products_snapshot:
            p_name = normalize_text(p.get("name", ""))
            p_cat = normalize_text(p.get("category", "") or "")
            p_sup = normalize_text(p.get("supplier", "") or "")
            p_desc = normalize_text(p.get("description", "") or "")
            flavours = " ".join(normalize_text(f) for f in (p.get("flavours") or []))
            presentation = " ".join(normalize_text(pr) for pr in (p.get("presentation") or []))

            haystack = f"{p_name} {p_cat} {p_sup} {p_desc} {flavours} {presentation}".strip()

            p_name_tokens = set(p_name.split())
            flavour_tokens = set(flavours.split())
            presentation_tokens = set(presentation.split())
            name_and_variant_tokens = p_name_tokens | flavour_tokens | presentation_tokens
            haystack_tokens = (
                name_and_variant_tokens
                | set(p_cat.split())
                | set(p_sup.split())
                | set(p_desc.split())
            )

            score = 0

            # Correspondência contígua no nome ou no texto completo
            if norm_clean and norm_clean in p_name:
                score += 100
            elif norm_clean and norm_clean in haystack:
                score += 40

            # Correspondência de tokens principais em nome, sabores e apresentações
            name_matches = sum(1 for t in core_tokens if t in p_name_tokens)
            flavour_matches = sum(1 for t in core_tokens if t in flavour_tokens)
            presentation_matches = sum(1 for t in core_tokens if t in presentation_tokens)
            variant_matches = sum(1 for t in core_tokens if t in name_and_variant_tokens)
            haystack_matches = sum(1 for t in core_tokens if t in haystack_tokens)

            if name_matches == len(core_tokens):
                score += 80
            elif variant_matches == len(core_tokens):
                score += 70
                if name_matches > 0 and flavour_matches > 0:
                    score += 20
                if name_matches > 0 and presentation_matches > 0:
                    score += 25
            elif variant_matches > 0:
                score += variant_matches * 15

            if haystack_matches == len(core_tokens) and variant_matches < len(core_tokens):
                score += 30
            elif haystack_matches > variant_matches:
                score += (haystack_matches - variant_matches) * 5

            # Bônus para expansão de sinônimos
            for syn in extra_synonyms:
                syn_parts = syn.split()
                if all(part in p_name_tokens for part in syn_parts):
                    score += 5
                elif all(part in name_and_variant_tokens for part in syn_parts):
                    score += 4
                elif all(part in haystack_tokens for part in syn_parts):
                    score += 2

            if score > 0:
                scored_products.append((score, p))

        # Ordena decrescente por relevância
        scored_products.sort(key=lambda x: x[0], reverse=True)

        # 4. Diversificação de marcas/fornecedores entre os melhores resultados (P-304, P-305)
        top_products: List[Dict[str, Any]] = []
        seen_suppliers = set()

        for _, p in scored_products:
            sup_name = p.get("supplier", "")
            if sup_name and sup_name not in seen_suppliers:
                top_products.append(p)
                seen_suppliers.add(sup_name)
            if len(top_products) >= limit:
                break

        # Se ainda houver vagas para atingir o limite, preenche com os restantes de maior score
        if len(top_products) < limit:
            for _, p in scored_products:
                if p not in top_products:
                    top_products.append(p)
                if len(top_products) >= limit:
                    break

        return top_products, detected_filters
