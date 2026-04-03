from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Telegram Bot Platform'
    env: str = 'development'
    log_level: str = 'INFO'
    secret_key: str
    database_url: str = 'sqlite:///./app.db'

    telegram_bot_token: str
    telegram_channel_id: str

    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'qwen2.5:7b'

    admin_username: str = 'admin'
    admin_password: str

    timezone: str = 'UTC'
    quiet_hours_start: int = 23
    quiet_hours_end: int = 7
    rate_limit_per_minute: int = 20

    @field_validator('quiet_hours_start', 'quiet_hours_end')
    @classmethod
    def validate_hours(cls, value: int) -> int:
        if not 0 <= value <= 23:
            raise ValueError('Quiet hours must be between 0 and 23')
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
