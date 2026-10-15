import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Remove acentos
    nfkd = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Remove pontuações e excesso de espaços
    cleaned = re.sub(r"[^a-z0-9\s]", " ", without_accents)
    return re.sub(r"\s+", " ", cleaned).strip()


import logging
import os

logger = logging.getLogger(__name__)


def extract_clean_search(query: str) -> str:
    cleaned = query.strip()
    patterns = [
        r"^(quais\s+(as|os|sao|são)?\s*(as|os)?\s*(opcoes|opções)?\s*(de|da|do)?\s*)",
        r"^(tem\s+(algum|alguma|opcao|opção|opcoes|opções)?\s*(de|da|do)?\s*)",
        r"^(voces|vocês)\s+tem\s+(opcao|opção|opcoes|opções)?\s*(de|da|do)?\s*",
        r"^(voce|você)\s+tem\s+(opcao|opção|opcoes|opções)?\s*(de|da|do)?\s*",
        r"^(gostaria\s+de\s+(ver|saber\s+sobre|conhecer)?\s*)",
        r"^(me\s+(mostre|mostra|diga|fale\s+sobre)\s*)",
        r"^(mostrar\s+|listar\s+|lista\s+de\s*)",
        r"^(procuro\s+por\s+|estou\s+procurando\s*(por)?\s*)"
    ]
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip("?!.,; ")
    return cleaned if len(cleaned) >= 2 else query.strip().rstrip("?!.,; ")


class CatalogIndex:
    """
    Índice em memória para busca rápida no catálogo (P-304, P-305).
    Indexa nome, slug, categoria, fornecedor, sabores, apresentação e descrição.
    Carrega automaticamente os produtos do banco de dados PostgreSQL.
    """

    def __init__(self, auto_load_db: bool = True):
        self.products: List[Dict[str, Any]] = []
        self.categories: List[Dict[str, str]] = []
        self.suppliers: List[Dict[str, str]] = []
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

    def load_from_db(
        self,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> bool:
        """
        Carrega todos os produtos, categorias e fornecedores diretamente do PostgreSQL.
        """
        try:
            import psycopg2
            db_name = dbname or os.getenv("POSTGRES_DB") or "fitoherb-v2"
            db_user = user or os.getenv("PostgresUsername") or os.getenv("POSTGRES_USER") or "postgres"
            db_pass = password or os.getenv("PostgresPassword") or os.getenv("POSTGRES_PASSWORD") or "Dm120394"
            db_host = host or os.getenv("POSTGRES_HOST") or "localhost"
            db_port = port or int(os.getenv("POSTGRES_PORT", "5432"))

            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                connect_timeout=3
            )
            conn.set_client_encoding("UTF8")
            cur = conn.cursor()

            # Categorias
            cur.execute("SELECT id, name, slug FROM product_categories;")
            categories = [{"id": str(r[0]), "name": r[1], "slug": r[2]} for r in cur.fetchall()]

            # Fornecedores
            cur.execute("SELECT id, name, slug FROM suppliers;")
            suppliers = [{"id": str(r[0]), "name": r[1], "slug": r[2]} for r in cur.fetchall()]

            # Produtos
            cur.execute("""
                SELECT p.id, p.name, p.slug, p.image_path, p.description, p.flavours, p.presentation,
                       c.name as category_name, c.slug as category_slug,
                       s.name as supplier_name, s.slug as supplier_slug
                FROM products p
                LEFT JOIN product_categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id;
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
                    "supplier_slug": r[10] or ""
                })

            conn.close()
            self.set_catalog(products=products, categories=categories, suppliers=suppliers)
            logger.info(f"CatalogIndex populado com sucesso: {len(products)} produtos, {len(categories)} categorias, {len(suppliers)} fornecedores.")
            return True
        except Exception as exc:
            logger.warning(f"Não foi possível carregar catálogo diretamente do PostgreSQL: {exc}")
            return False

    def set_catalog(
        self,
        products: List[Dict[str, Any]],
        categories: Optional[List[Dict[str, str]]] = None,
        suppliers: Optional[List[Dict[str, str]]] = None
    ):
        self.products = products or []
        self.categories = categories or []
        self.suppliers = suppliers or []

    def search(self, query: str, limit: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executa busca por relevância e identifica facetas (categoria, fornecedor).
        Retorna (lista_produtos, filtros_detectados).
        """
        norm_query = normalize_text(query)
        clean_search_text = extract_clean_search(query)
        detected_filters: Dict[str, Any] = {
            "category": [],
            "supplier": [],
            "search": clean_search_text
        }

        # 1. Checa correspondência com fornecedores e categorias conhecidas
        for cat in self.categories:
            cat_norm = normalize_text(cat.get("name", ""))
            cat_slug = cat.get("slug", "")
            if cat_norm and (cat_norm in norm_query or cat_slug in norm_query):
                if cat_slug not in detected_filters["category"]:
                    detected_filters["category"].append(cat_slug)

        for sup in self.suppliers:
            sup_norm = normalize_text(sup.get("name", ""))
            sup_slug = sup.get("slug", "")
            if sup_norm and (sup_norm in norm_query or sup_slug in norm_query):
                if sup_slug not in detected_filters["supplier"]:
                    detected_filters["supplier"].append(sup_slug)

        # 2. Expansão simples de sinônimos na query e extração de tokens principais
        norm_clean = normalize_text(clean_search_text)
        stopwords = {
            "quais", "as", "os", "sao", "são", "opcoes", "opções", "opcao", "opção",
            "de", "da", "do", "das", "dos", "para", "com", "em", "um", "uma", "tem",
            "voces", "vocês", "voce", "você", "sobre", "ver", "gostaria"
        }
        raw_tokens = norm_clean.split() if norm_clean else norm_query.split()
        core_tokens = [t for t in raw_tokens if t not in stopwords and len(t) >= 2]
        if not core_tokens:
            core_tokens = [t for t in norm_query.split() if len(t) >= 2]

        expanded_tokens = set(core_tokens)
        for token in core_tokens:
            for canon, syn_list in self._synonyms.items():
                if token in syn_list or token == canon:
                    expanded_tokens.add(canon)
                    expanded_tokens.update(syn_list)

        # 3. Score e ranqueamento invariante à ordem das palavras (ex: 'whey 100%' == '100% whey')
        scored_products = []
        for p in self.products:
            p_name = normalize_text(p.get("name", ""))
            p_cat = normalize_text(p.get("category", "") or "")
            p_sup = normalize_text(p.get("supplier", "") or "")
            p_desc = normalize_text(p.get("description", "") or "")
            flavours = " ".join([normalize_text(f) for f in p.get("flavours", []) or []])
            presentation = " ".join([normalize_text(pr) for pr in p.get("presentation", []) or []])

            haystack = f"{p_name} {p_cat} {p_sup} {p_desc} {flavours} {presentation}"

            score = 0

            # 1. Prioridade máxima: correspondência contígua exata do termo buscado no nome (ex: 'whey 100%')
            if norm_clean and norm_clean in p_name:
                score += 100
            elif norm_clean and norm_clean in haystack:
                score += 40

            # 2. Correspondência de todos os tokens principais no nome (independente da ordem, ex: '100% whey')
            if core_tokens:
                name_token_matches = sum(1 for t in core_tokens if t in p_name)
                haystack_token_matches = sum(1 for t in core_tokens if t in haystack)

                if name_token_matches == len(core_tokens):
                    score += 50
                elif name_token_matches > 0:
                    score += name_token_matches * 10

                if haystack_token_matches == len(core_tokens) and score < 50:
                    score += 25

            # 3. Bônus para expansão de sinônimos
            for t in expanded_tokens:
                if t in p_name:
                    score += 5
                elif t in haystack:
                    score += 2

            if score > 0:
                scored_products.append((score, p))


        # Ordena decrescente por relevância
        scored_products.sort(key=lambda x: x[0], reverse=True)

        # 4. Diversificação de marcas/fornecedores entre os melhores resultados (P-305 Neutralidade)
        top_products: List[Dict[str, Any]] = []
        seen_suppliers = set()

        for s, p in scored_products:
            sup_name = p.get("supplier", "")
            if sup_name and sup_name not in seen_suppliers:
                top_products.append(p)
                seen_suppliers.add(sup_name)
            if len(top_products) >= limit:
                break

        # Se ainda houver vagas para atingir o limite, preenche com os restantes de maior score
        if len(top_products) < limit:
            for s, p in scored_products:
                if p not in top_products:
                    top_products.append(p)
                if len(top_products) >= limit:
                    break

        return top_products, detected_filters

