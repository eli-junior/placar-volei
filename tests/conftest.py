from pathlib import Path

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def isolate_test_fixtures(tmp_path: Path):
    """
    Garante que os testes não modifiquem nem dependam do arquivo real defaultArenas.json.
    Aponta settings.default_arenas_file para um arquivo temporário limpo.
    """
    original_settings = settings.model_dump()
    test_fixture = str(tmp_path / "defaultArenas_test.json")
    settings.default_arenas_file = test_fixture
    yield
    for key, value in original_settings.items():
        setattr(settings, key, value)
