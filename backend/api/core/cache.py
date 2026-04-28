from __future__ import annotations

import json
import os
from typing import Any, Optional

import redis


class CacheManager:
    def __init__(self) -> None:
        self._enabled = os.getenv("REDIS_CACHE_ENABLED", "true").lower() == "true"
        self._client: Optional[redis.Redis] = None
        if not self._enabled:
            return

        redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        try:
            self._client = redis.Redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
        except Exception:
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def get_json(self, key: str) -> Any:
        if not self._client:
            return None
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if not self._client:
            return
        self._client.setex(key, ttl_seconds, json.dumps(value))

    def delete(self, key: str) -> None:
        if not self._client:
            return
        self._client.delete(key)

    def delete_pattern(self, pattern: str) -> None:
        if not self._client:
            return
        keys = self._client.keys(pattern)
        if keys:
            self._client.delete(*keys)


cache_manager = CacheManager()


def student_topics_cache_key(student_id: int, classroom_id: Optional[int]) -> str:
    return f"student:topics:{student_id}:{classroom_id or 'all'}"


def teacher_topics_cache_key(teacher_id: int) -> str:
    return f"teacher:topics:{teacher_id}"


def evaluation_cache_key(topic_id: int, text_hash: str) -> str:
    return f"evaluation:{topic_id}:{text_hash}"


def teacher_analytics_cache_key(teacher_id: int) -> str:
    return f"teacher:analytics:{teacher_id}"
