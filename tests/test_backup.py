import asyncio
import sqlite3
import threading
from pathlib import Path

import pytest

from app import backup
from app.config import settings
from app.jogadores import criar_sync, init_jogadores_sync, salvar_foto_sync
from app.sessao import abrir_sync, marcar_sync

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 200


@pytest.fixture(autouse=True)
def banco(tmp_path: Path):
    settings.gerenciador_db_path = str(tmp_path / "gerenciador.db")
    settings.gerenciador_backup_dir = str(tmp_path / "backups")
    settings.gerenciador_backup_manter = 28
    init_jogadores_sync()
    yield


def popular() -> dict:
    ana = criar_sync("Ana Souza", "M", 80)
    salvar_foto_sync(ana["id"], JPEG)
    abrir_sync()
    marcar_sync(ana["id"])
    return ana


def contar(caminho, tabela):
    with sqlite3.connect(caminho) as c:
        return c.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def test_backup_gera_copia_integra_com_tudo(tmp_path):
    popular()
    cópia = backup.fazer_backup()
    assert cópia.parent == tmp_path / "backups" and cópia.suffix == ".db"
    assert cópia.name.startswith("gerenciador-")
    backup.verificar(cópia)
    for tabela in ("jogadores", "jogador_fotos", "sessoes", "presencas"):
        assert contar(cópia, tabela) == 1
    # só o arquivo final na pasta: sem .parcial nem -wal/-shm soltos
    assert [p.name for p in (tmp_path / "backups").iterdir()] == [cópia.name]


def test_backup_consistente_com_escrita_concorrente():
    popular()
    parar = threading.Event()
    erros = []

    def escritor():
        i = 0
        while not parar.is_set():
            try:
                criar_sync(f"Jogador{i} Teste", "M", 50)
            except Exception as e:  # noqa: BLE001
                erros.append(e)
            i += 1

    t = threading.Thread(target=escritor)
    t.start()
    try:
        copias = [backup.fazer_backup() for _ in range(5)]
    finally:
        parar.set()
        t.join()
    assert not erros
    for c in copias:
        backup.verificar(c)


def test_retencao_mantem_as_mais_recentes():
    popular()
    pasta = Path(settings.gerenciador_backup_dir)
    pasta.mkdir()
    for i in range(30):
        (pasta / f"gerenciador-2020010{i % 10}T0000{i:02d}000000Z.db").write_bytes(b"x")
    nova = backup.fazer_backup(manter=28)
    ficaram = backup.listar(pasta)
    assert len(ficaram) == 28 and ficaram[0] == nova


def test_falha_nao_poda_nem_substitui(tmp_path, monkeypatch):
    popular()
    boas = [backup.fazer_backup() for _ in range(3)]
    antes = {p.name: p.read_bytes() for p in boas}

    def quebra(origem, destino):
        Path(destino).write_bytes(b"isto nao e um banco sqlite")

    monkeypatch.setattr(backup, "_copiar", quebra)
    with pytest.raises(backup.BackupInvalido):
        backup.fazer_backup(manter=1)  # manter=1 podaria as boas se desse certo
    assert {
        p.name: p.read_bytes() for p in backup.listar(settings.gerenciador_backup_dir)
    } == antes
    assert not list(Path(settings.gerenciador_backup_dir).glob("*.parcial"))


def test_desligado_sem_pasta_e_origem_inexistente(tmp_path):
    settings.gerenciador_backup_dir = ""
    with pytest.raises(backup.BackupDesligado):
        backup.fazer_backup()
    settings.gerenciador_backup_dir = str(tmp_path / "b")
    settings.gerenciador_db_path = str(tmp_path / "nao-existe.db")
    with pytest.raises(FileNotFoundError):
        backup.fazer_backup()


def test_pasta_sem_permissao_falha_com_erro_claro(tmp_path):
    popular()
    arquivo = tmp_path / "e-um-arquivo"
    arquivo.write_text("x")
    with pytest.raises(OSError):
        backup.fazer_backup(pasta=str(arquivo / "dentro"))


def test_sobras_parciais_sao_limpas():
    popular()
    pasta = Path(settings.gerenciador_backup_dir)
    pasta.mkdir()
    (pasta / "gerenciador-20200101T000000000000Z.db.parcial").write_bytes(b"x")
    backup.fazer_backup()
    assert [p.suffix for p in pasta.iterdir()] == [".db"]


def test_restaurar_devolve_tudo_num_banco_novo(tmp_path):
    ana = popular()
    cópia = backup.fazer_backup()
    novo = str(tmp_path / "restaurado.db")
    assert backup.restaurar(str(cópia), novo) == Path(novo)
    assert sorted(p.name for p in tmp_path.glob("restaurado.db*")) == ["restaurado.db"]
    assert contar(novo, "jogadores") == 1 and contar(novo, "jogador_fotos") == 1
    with sqlite3.connect(novo) as c:
        assert c.execute("SELECT imagem FROM jogador_fotos").fetchone()[0] == JPEG
        assert c.execute("SELECT nome, nota FROM jogadores").fetchone() == (
            "Ana Souza",
            80,
        )
        assert (
            c.execute(
                "SELECT COUNT(*) FROM sessoes WHERE encerrada_em IS NULL"
            ).fetchone()[0]
            == 1
        )
        assert c.execute("SELECT jogador_id, ordem FROM presencas").fetchone() == (
            ana["id"],
            1,
        )


def test_restaurar_sobre_banco_existente_guarda_o_antes(tmp_path):
    popular()
    cópia = backup.fazer_backup()
    criar_sync("Bia Lima", "M")  # só existe no banco atual
    atual = Path(settings.gerenciador_db_path)
    backup.restaurar(str(cópia))
    assert contar(atual, "jogadores") == 1
    antes = [
        p
        for p in atual.parent.glob(f"{atual.name}.antes-*")
        if not p.name.endswith(("-wal", "-shm"))
    ]
    assert len(antes) == 1 and contar(antes[0], "jogadores") == 2
    # o app volta a abrir o banco restaurado
    init_jogadores_sync()
    assert contar(atual, "jogadores") == 1


def test_restaurar_recusa_copia_corrompida_sem_tocar_no_banco(tmp_path):
    popular()
    atual = Path(settings.gerenciador_db_path)
    antes = atual.read_bytes()
    ruim = tmp_path / "ruim.db"
    ruim.write_bytes(b"lixo" * 100)
    with pytest.raises(backup.BackupInvalido):
        backup.restaurar(str(ruim))
    assert atual.read_bytes() == antes
    assert not list(tmp_path.glob("*.antes-*")) and not list(
        tmp_path.glob("*.restaurando")
    )
    # banco válido mas sem as tabelas do gerenciador também é recusado
    outro = tmp_path / "outro.db"
    with sqlite3.connect(outro) as c:
        c.execute("CREATE TABLE x (a)")
    with pytest.raises(backup.BackupInvalido, match="faltam tabelas"):
        backup.restaurar(str(outro))
    with pytest.raises(FileNotFoundError):
        backup.restaurar(str(tmp_path / "nao-existe.db"))


@pytest.mark.asyncio
async def test_rotina_faz_backup_na_subida_e_repete_sem_derrubar():
    popular()
    tarefa = asyncio.create_task(backup.rotina(intervalo_segundos=1))
    await asyncio.sleep(2.5)
    tarefa.cancel()
    await tarefa
    assert len(backup.listar(settings.gerenciador_backup_dir)) >= 2


@pytest.mark.asyncio
async def test_rotina_sobrevive_a_falha_e_desligada_encerra(tmp_path):
    settings.gerenciador_db_path = str(tmp_path / "nao-existe.db")
    tarefa = asyncio.create_task(backup.rotina(intervalo_segundos=1))
    await asyncio.sleep(1.5)
    assert not tarefa.done()  # falhou mas segue viva
    tarefa.cancel()
    await tarefa
    settings.gerenciador_backup_dir = ""
    await asyncio.wait_for(backup.rotina(), timeout=2)  # desligada: retorna na hora


def test_cli_agora_listar_e_restaurar(tmp_path, capsys):
    popular()
    assert backup._principal(["agora"]) == 0
    caminho = capsys.readouterr().out.strip()
    assert Path(caminho).is_file()
    assert backup._principal(["listar"]) == 0
    assert Path(caminho).name in capsys.readouterr().out
    destino = str(tmp_path / "ensaio.db")
    assert backup._principal(["restaurar", caminho, "--destino", destino]) == 0
    assert contar(destino, "jogadores") == 1
    assert (
        backup._principal(["restaurar", str(tmp_path / "x.db"), "--destino", destino])
        == 1
    )
    settings.gerenciador_backup_dir = ""
    assert backup._principal(["agora"]) == 1
