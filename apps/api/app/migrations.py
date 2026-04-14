from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from app.config import get_settings


def _alembic_config() -> Config:
    base_dir = Path(__file__).resolve().parents[1]
    config = Config(str(base_dir / "alembic.ini"))
    config.set_main_option("script_location", str(base_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", get_settings().database_url)
    return config


def upgrade_database() -> None:
    config = _alembic_config()
    command.upgrade(config, "head")
