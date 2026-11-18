import hashlib
import threading
import time
from typing import Any, Dict, Optional


class ConversationCacheService:
    """
    Cache L1 em Memória para Respostas do Chatbot (P-310).
    Chave baseada em SHA-256 da consulta normalizada isolada por catalog_version com TTL.
    """

    _lock = threading.RLock()
    _catalog_version: int = 1
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_catalog_version(cls) -> int:
        with cls._lock:
            return cls._catalog_version

    @classmethod
    def bump_catalog_version(cls) -> int:
        with cls._lock:
            cls._catalog_version += 1
            cls._cache.clear()
            return cls._catalog_version

    @classmethod
    def _hash_key(cls, query: str, catalog_version: int) -> str:
        clean = query.lower().strip()
        scoped = f"v{catalog_version}:{clean}"
        return hashlib.sha256(scoped.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, query: str, catalog_version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        with cls._lock:
            version = cls._catalog_version if catalog_version is None else catalog_version
            key = cls._hash_key(query, version)
            entry = cls._cache.get(key)
            if not entry:
                return None

            if time.time() >= entry["expires_at"]:
                del cls._cache[key]
                return None

            return entry["data"]

    @classmethod
    def set(
        cls,
        query: str,
        data: Dict[str, Any],
        ttl_seconds: int = 3600,
        catalog_version: Optional[int] = None,
    ) -> bool:
        with cls._lock:
            version = cls._catalog_version if catalog_version is None else catalog_version
            if version < cls._catalog_version:
                return False

            key = cls._hash_key(query, version)
            cls._cache[key] = {
                "data": data,
                "expires_at": time.time() + ttl_seconds,
                "catalog_version": version,
            }
            return True

    @classmethod
    def clear(cls, reset_version: bool = True) -> None:
        with cls._lock:
            cls._cache.clear()
            if reset_version:
                cls._catalog_version = 1
