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


class CatalogIndex:
    """
    Índice em memória para busca rápida no catálogo (P-304, P-305).
    Indexa nome, slug, categoria, fornecedor, sabores, apresentação e descrição.
    """

    def __init__(self):
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
        detected_filters: Dict[str, Any] = {
            "category": [],
            "supplier": [],
            "search": query.strip()
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

        # 2. Expansão simples de sinônimos na query
        query_tokens = norm_query.split()
        expanded_tokens = set(query_tokens)
        for token in query_tokens:
            for canon, syn_list in self._synonyms.items():
                if token in syn_list:
                    expanded_tokens.add(canon)
                    expanded_tokens.update(syn_list)

        # 3. Score e ranqueamento
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
            # Exata na query
            if norm_query and norm_query in p_name:
                score += 10
            elif norm_query and norm_query in haystack:
                score += 5

            # Token matches
            for t in expanded_tokens:
                if len(t) < 3:
                    continue
                if t in p_name:
                    score += 3
                elif t in haystack:
                    score += 1

            if score > 0:
                scored_products.append((score, p))

        scored_products.sort(key=lambda x: x[0], reverse=True)
        top_products = [item[1] for item in scored_products[:limit]]

        return top_products, detected_filters
