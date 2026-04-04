#!/usr/bin/env python3
"""Clear aiogram/aiogram_dialog data from Redis.

Usage:
    python scripts/clear_aiogram_redis.py
    python scripts/clear_aiogram_redis.py --settings settings.yaml --dry-run
"""

from __future__ import annotations

import sys
from pathlib import Path

# add parent dir to sys.path
sys.path.append(str(Path(__file__).parents[1]))

import argparse

from redis import Redis
from src.config import settings


def load_redis_url() -> str:
    if settings.redis_url is None:
        raise ValueError("redis_url is not set in settings.yaml")
    return settings.redis_url.get_secret_value()


def collect_aiogram_keys(redis_client: Redis) -> list[str]:
    patterns = [
        "fsm:*",  # aiogram FSM storage keys (also used by aiogram_dialog state)
        "aiogram_dialog:*",
        "aiogram:*",
    ]

    found: set[str] = set()
    for pattern in patterns:
        for key in redis_client.scan_iter(match=pattern, count=1000):
            if isinstance(key, bytes):
                found.add(key.decode("utf-8", errors="replace"))
            else:
                found.add(str(key))

    return sorted(found)


def delete_keys(redis_client: Redis, keys: list[str]) -> int:
    if not keys:
        return 0

    deleted = 0
    chunk_size = 1000
    for i in range(0, len(keys), chunk_size):
        chunk = keys[i : i + chunk_size]
        deleted += redis_client.delete(*chunk)
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description="Clear aiogram/aiogram_dialog data from Redis")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print matched keys count, do not delete",
    )
    args = parser.parse_args()

    redis_url = load_redis_url()
    redis_client = Redis.from_url(redis_url, decode_responses=False)

    try:
        keys = collect_aiogram_keys(redis_client)
        print(f"Found {len(keys)} aiogram/aiogram_dialog keys")

        if args.dry_run:
            for key in keys[:50]:
                print(key)
            if len(keys) > 50:
                print(f"... and {len(keys) - 50} more")
            return 0

        deleted = delete_keys(redis_client, keys)
        print(f"Deleted {deleted} keys")
        return 0
    finally:
        redis_client.close()


if __name__ == "__main__":
    raise SystemExit(main())
