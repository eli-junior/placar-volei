from pydantic_settings import BaseSettings, SettingsConfigDict

SEGREDO_PADRAO = "troque-este-segredo-em-producao"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: str = "data/placar.db"
    # Base de jogadores (CV8): durável, nunca apagada pelo reset do banco das quadras.
    gerenciador_db_path: str = "data/gerenciador.db"
    # Backup do gerenciador.db (CV8.TS1): pasta fora do volume; vazio = desligado.
    gerenciador_backup_dir: str = ""
    gerenciador_backup_intervalo_horas: float = 6
    gerenciador_backup_manter: int = 28
    owner_secret: str = SEGREDO_PADRAO
    # Em produção o app não sobe com o segredo padrão nem sem segredo.
    producao: bool = False
    # Cookie de sessão só por HTTPS (produção atrás do túnel).
    cookie_secure: bool = False
    admin_timeout_seconds: int = 120
    host: str = "0.0.0.0"
    port: int = 8000
    version: str = "0.39.0"
    reset_db_on_startup: bool = False
    # Apelidos (separados por vírgula, qualquer caixa) que habilitam o vínculo
    # de relógio ao criar ou entrar na sala; são gravados em Title ("eli" -> "Eli").
    watch_auto_grant: str = "eli"
    # Atrás do Cloudflare Tunnel: o IP do cliente vem de `CF-Connecting-IP`.
    # Desligado, vale o IP da conexão (acesso direto, testes).
    trust_cloudflare: bool = False

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


def validar_producao(config: Settings) -> None:
    """Recusa subir em produção com um segredo de owner que qualquer um conhece."""
    if config.producao and config.owner_secret.strip() in ("", SEGREDO_PADRAO):
        raise RuntimeError(
            "OWNER_SECRET ausente ou com o valor de exemplo. "
            "Defina um segredo próprio no .env antes de subir em produção."
        )


settings = Settings()
