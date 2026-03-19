from enum import StrEnum
from pathlib import Path

import yaml
from aiogram.types import BotCommand
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SettingBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class Accounts(SettingBaseModel):
    """InNoHassle Accounts integration settings"""

    api_url: str = "https://api.innohassle.ru/accounts/v0"
    "API URL for InNoHassle Accounts"
    api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"


class Settings(SettingBaseModel):
    """
    Settings for the application.
    """

    schema_: str | None = Field(None, alias="$schema")
    environment: Environment = Environment.DEVELOPMENT
    "App environment flag"
    redis_url: SecretStr | None = Field(None, examples=["redis://localhost:6379/0", "redis://redis:6379/0"])
    "Redis URL"
    bot_token: SecretStr
    "Telegram bot token from @BotFather"
    notification_bot_token: SecretStr
    "Telegram notification bot token from @BotFather"
    bot_name: str | None = None
    "Desired bot name"
    bot_description: str | None = None
    "Bot description"
    bot_short_description: str | None = None
    "Bot short description"
    bot_commands: list[BotCommand] | None = None
    "Bot commands (displayed in telegram menu)"
    admins: list[int] = []
    "Admin' telegram IDs"
    accounts: Accounts | None = None
    "Use production InNoHassle Accounts API for authentication in local development"
    telegram_bind_url: str | None = None
    "URL for binding Telegram to InNoHassle Account"
    db_url: SecretStr = Field(
        examples=[
            "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres",
            "postgresql+asyncpg://postgres:postgres@db:5432/postgres",
        ],
    )
    "Connection String for SQLAlchemy"
    mock_auth: bool = False
    "Use MockAutoAuthMiddleware to bypass Authentication via InNoHassle Accounts (for testing)"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.model_json_schema()}
            yaml.dump(schema, f, sort_keys=False)
