from typing import Any

import httpx

from src.config import settings


class InNoHassleAPI:
    api_root_path: str

    def __init__(self, api_url: str):
        self.api_root_path = api_url

    def _create_client(self, /, telegram_id: int | None = None) -> httpx.AsyncClient:
        if telegram_id is not None:
            auth_header = {"Authorization": f"Bearer {telegram_id}:{settings.bot_token.get_secret_value()}"}
        else:
            auth_header = {"Authorization": f"Bearer {settings.bot_token.get_secret_value()}"}

        client = httpx.AsyncClient(headers=auth_header, base_url=self.api_root_path)
        return client

    async def start_registration(self, telegram_id: int) -> tuple[bool | None, Any]:
        params = {"telegram_id": telegram_id}
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.post("/auth/registration", params=params)
            print(response, response.text)
            response.raise_for_status()
