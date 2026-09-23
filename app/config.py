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
    version: str = "0.8.0"
    reset_db_on_startup: bool = False
    # Apelidos (separados por vírgula, qualquer caixa) que habilitam o vínculo
    # de relógio ao criar ou entrar na sala; são gravados em Title ("eli" -> "Eli").
    watch_auto_grant: str = "eli"

    # Limites de capacidade e ciclo de vida
    max_quadras: int = 20
    max_participantes_por_quadra: int = 20
    quadra_ttl_seconds: int = 3600  # 1 hora sem atualização
    # Janela de presença efetiva. Um participante sem conexão ativa no hub e sem
    # sinal de vida (`ultimo_visto_em`) dentro desta janela deixa de ocupar vaga
    # na quadra, para que a rotatividade da pelada não produza lotação fantasma.
    presenca_ttl_seconds: int = 120
    # Janela de tolerância para o controlador ativo sumir. Passado este prazo sem
    # conexão e sem sinal de vida, o controle do placar volta sozinho para o
    # admin da sala, para que a partida nunca fique sem quem aperte o botão.
    controle_timeout_seconds: int = 15


settings = Settings()
