from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: str = "data/placar.db"
    owner_secret: str = "troque-este-segredo-em-producao"
    admin_timeout_seconds: int = 120
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
