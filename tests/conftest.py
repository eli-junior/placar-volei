from pathlib import Path

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def isolate_test_settings(tmp_path: Path):
    """Garante isolamento de configurações entre execuções de testes."""
    original_settings = settings.model_dump()
    yield
    for key, value in original_settings.items():
        setattr(settings, key, value)
