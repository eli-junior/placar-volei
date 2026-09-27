from pathlib import Path

import pytest

from app.config import settings
from app.rate_limit import entrada_rate_limiter

# Fixture `client` e helpers dos testes do relógio (CV3.DS1.TS1). Arquivos
# com `client` próprio continuam usando o seu.
pytest_plugins = ["tests.watch_support"]


@pytest.fixture(autouse=True)
def isolate_test_settings(tmp_path: Path):
    """Garante isolamento de configurações entre execuções de testes."""
    original_settings = settings.model_dump()
    # O .env local é de produção ou de dev (COOKIE_SECURE, TRUST_CLOUDFLARE,
    # PRODUCAO) e não pode mudar o resultado dos testes, que usam http://.
    settings.cookie_secure = False
    settings.trust_cloudflare = False
    settings.producao = False
    entrada_rate_limiter.resetar()
    yield
    for key, value in original_settings.items():
        setattr(settings, key, value)
