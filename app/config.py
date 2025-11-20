from pydantic import computed_field, PostgresDsn
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_ignore_empty=True
    )
    """Load .env file if it exists. Ignore fields not defined in this model."""

    # Database
    # --------------------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str  # Required - must be set in .env
    POSTGRES_DB: str  # Required - must be set in .env

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgres",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @computed_field
    @property
    def TORTOISE_ORM(self) -> dict:
        return {
            "connections": {
                "default": str(self.DATABASE_URL),
            },
            "apps": {
                "models": {
                    "models": [],  # Empty since we're only using raw queries
                    "default_connection": "default",
                },
            },
        }

    # Directories
    # --------------------
    BASE_DIR: Path = Path(__file__).resolve().parent

    @computed_field
    @property
    def TEMPLATES_DIR(self) -> Path:
        return self.BASE_DIR / "templates"

    # LLM Configuration (using LiteLLM)
    # --------------------
    # Model for SQL generation (use best reasoning model)
    SQL_MODEL: str = "claude-sonnet-4-5"

    # Model for answer generation (use fast/cheap model)
    ANSWER_MODEL: str = "claude-haiku-4-5"


settings = Settings()  # type: ignore
