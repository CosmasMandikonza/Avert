from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AVERT API"
    app_mode: str = "DEMO_MODE"
    database_url: str = "sqlite:///./avert.db"
    ave_api_base_url: str = "https://data.ave-api.xyz/v2"
    ave_api_key: str | None = None
    ave_request_timeout_seconds: float = 20.0
    ave_trade_api_base_url: str = "https://bot-api.ave.ai"
    ave_trade_request_timeout_seconds: float = 20.0
    ave_trade_preview_amount: str = "0.001"
    ave_wss_base_url: str = "wss://wss.ave-api.xyz"
    ave_wss_heartbeat_seconds: int = 30
    ave_wss_subscription_refresh_seconds: int = 180
    ave_wss_open_timeout_seconds: float = 20.0
    ave_wss_reconnect_seconds: int = 10
    ave_topic_limit: int = 12
    ave_topic_token_limit: int = 12
    live_snapshot_cache_seconds: int = 120
    auto_seed_demo: bool = True
    auto_run_migrations: bool = True
    live_execution_enabled: bool = False
    chain_executor_base_url: str | None = None
    chain_executor_api_key: str | None = None
    proxy_executor_base_url: str | None = None
    proxy_executor_api_key: str | None = None
    chain_wallet_address: str | None = None
    chain_wallet_private_key: str | None = None
    proxy_wallet_id: str | None = None
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://web-saferta.vercel.app",
        "https://avert-tau-two-93.vercel.app",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()