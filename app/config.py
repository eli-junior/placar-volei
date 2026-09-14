from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: str = "data/placar.db"
    default_arenas_file: str = "fixtures/defaultArenas.json"
    owner_secret: str = "troque-este-segredo-em-producao"
    admin_timeout_seconds: int = 120
    host: str = "0.0.0.0"
    port: int = 8000
    version: str = "0.3.0"
    reset_db_on_startup: bool = False

    # Limites de capacidade e ciclo de vida
    max_quadras: int = 20
    max_participantes_por_quadra: int = 20
    quadra_ttl_seconds: int = 3600  # 1 hora sem atualização
    max_arenas: int = 50
    max_quadras_por_arena: int = 20


settings = Settings()
