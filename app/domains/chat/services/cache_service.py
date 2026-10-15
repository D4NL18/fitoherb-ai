import hashlib
import time
from typing import Dict, Any, Optional

class ConversationCacheService:
    """
    Cache L1 em Memória para Respostas do Chatbot (P-310).
    Chave baseada em SHA-256 da consulta normalizada com TTL.
    """
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _hash_key(cls, query: str) -> str:
        clean = query.lower().strip()
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, query: str) -> Optional[Dict[str, Any]]:
        key = cls._hash_key(query)
        entry = cls._cache.get(key)
        if not entry:
            return None

        if time.time() > entry["expires_at"]:
            del cls._cache[key]
            return None

        return entry["data"]

    @classmethod
    def set(cls, query: str, data: Dict[str, Any], ttl_seconds: int = 3600):
        key = cls._hash_key(query)
        cls._cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl_seconds
        }

    @classmethod
    def clear(cls):
        cls._cache.clear()
