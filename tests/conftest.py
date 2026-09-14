from pathlib import Path

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def isolate_test_fixtures(tmp_path: Path):
    """
    Garante que os testes não modifiquem nem dependam do arquivo real defaultArenas.json.
    Aponta settings.default_arenas_file para um arquivo temporário limpo.
    """
    original_fixture = settings.default_arenas_file
    test_fixture = str(tmp_path / "defaultArenas_test.json")
    settings.default_arenas_file = test_fixture
    yield
    settings.default_arenas_file = original_fixture
