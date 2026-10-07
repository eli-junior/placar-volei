"""Backup e restauração do `gerenciador.db` (CV8.TS1).

A cópia usa a API de backup do SQLite, que é consistente com o app gravando e
com o WAL ativo (um `cp` do arquivo não seria). Cada cópia é verificada antes
de ganhar o nome final; uma cópia ruim nunca substitui nem faz podar as boas.

Linha de comando (o app precisa estar parado só para `restaurar`):

    python -m app.backup agora
    python -m app.backup listar
    python -m app.backup restaurar <arquivo> [--destino <caminho>]
"""

import argparse
import asyncio
import logging
import sqlite3
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

PREFIXO = "gerenciador-"
SOBRA_PARCIAL_SEGUNDOS = 3600
TABELAS_ESPERADAS = {"jogadores", "jogador_fotos", "sessoes", "presencas"}


class BackupInvalido(Exception):
    """A cópia não passou na verificação de integridade."""


class BackupDesligado(Exception):
    """`GERENCIADOR_BACKUP_DIR` não está configurado."""


def _carimbo() -> str:
    # Microssegundos: nomes únicos e em ordem alfabética = ordem cronológica.
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def _copiar(origem: Path | str, destino: Path | str) -> None:
    src = sqlite3.connect(str(origem), timeout=10.0)
    dst = sqlite3.connect(str(destino))
    try:
        src.backup(dst)
        # A cópia herda o modo WAL do original; em DELETE ela é um arquivo
        # único e completo, sem -wal/-shm soltos ao lado.
        dst.execute("PRAGMA journal_mode=DELETE")
    finally:
        dst.close()
        src.close()


def verificar(caminho: Path | str) -> None:
    """Levanta `BackupInvalido` se o arquivo não for um gerenciador.db íntegro."""
    try:
        conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        try:
            resultado = [r[0] for r in conn.execute("PRAGMA integrity_check")]
            tabelas = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            conn.close()
    except sqlite3.Error as e:
        raise BackupInvalido(f"não é um banco SQLite legível ({e})") from None
    if resultado != ["ok"]:
        raise BackupInvalido(f"falhou na verificação de integridade: {resultado[:3]}")
    faltando = TABELAS_ESPERADAS - tabelas
    if faltando:
        raise BackupInvalido(f"faltam tabelas: {', '.join(sorted(faltando))}")


def listar(pasta: Path | str) -> list[Path]:
    """Cópias finais, da mais recente para a mais antiga."""
    pasta = Path(pasta)
    if not pasta.is_dir():
        return []
    return sorted(
        (p for p in pasta.glob(f"{PREFIXO}*.db") if p.is_file()),
        key=lambda p: p.name,
        reverse=True,
    )


def podar(pasta: Path | str, manter: int) -> list[Path]:
    removidas = []
    for antiga in listar(pasta)[max(manter, 1) :]:
        antiga.unlink(missing_ok=True)
        removidas.append(antiga)
    return removidas


def fazer_backup(
    origem: str | None = None,
    pasta: str | None = None,
    manter: int | None = None,
) -> Path:
    """Gera uma cópia verificada e poda as antigas. Devolve o caminho dela."""
    origem = origem or settings.gerenciador_db_path
    pasta = pasta or settings.gerenciador_backup_dir
    manter = manter if manter is not None else settings.gerenciador_backup_manter
    if not pasta:
        raise BackupDesligado("GERENCIADOR_BACKUP_DIR não está configurado")
    if not Path(origem).is_file():
        raise FileNotFoundError(f"banco não encontrado: {origem}")

    destino_dir = Path(pasta)
    destino_dir.mkdir(parents=True, exist_ok=True)
    # Sobras de uma queda no meio de um backup anterior. Só as velhas: uma
    # cópia em andamento (a rotina do app, ou `agora` na linha de comando)
    # tem um .parcial recente que não pode ser apagado por baixo dela.
    limite = time.time() - SOBRA_PARCIAL_SEGUNDOS
    for sobra in destino_dir.glob(f"{PREFIXO}*.parcial"):
        try:
            if sobra.stat().st_mtime < limite:
                sobra.unlink(missing_ok=True)
        except FileNotFoundError:
            pass

    final = destino_dir / f"{PREFIXO}{_carimbo()}.db"
    parcial = final.with_name(final.name + ".parcial")
    try:
        _copiar(origem, parcial)
        verificar(parcial)
        parcial.replace(final)
    except BaseException:
        parcial.unlink(missing_ok=True)
        raise
    # Só poda depois de ter uma cópia nova e boa.
    podar(destino_dir, manter)
    return final


def restaurar(arquivo: str, destino: str | None = None) -> Path:
    """Troca o banco por uma cópia verificada, guardando o atual como `.antes-*`.

    O app precisa estar parado: trocar o arquivo debaixo de um processo que o
    mantém aberto pode corromper a troca.
    """
    origem = Path(arquivo)
    if not origem.is_file():
        raise FileNotFoundError(f"cópia não encontrada: {arquivo}")
    verificar(origem)

    alvo = Path(destino or settings.gerenciador_db_path)
    alvo.parent.mkdir(parents=True, exist_ok=True)
    temporario = alvo.with_name(alvo.name + ".restaurando")
    temporario.unlink(missing_ok=True)
    try:
        # Pela API de backup: sai um arquivo novo, sem -wal/-shm herdados.
        _copiar(origem, temporario)
        verificar(temporario)
    except BaseException:
        temporario.unlink(missing_ok=True)
        raise

    carimbo = _carimbo()
    for sufixo in ("", "-wal", "-shm"):
        atual = alvo.with_name(alvo.name + sufixo)
        if atual.exists():
            atual.rename(alvo.with_name(f"{alvo.name}.antes-{carimbo}{sufixo}"))
    temporario.replace(alvo)
    return alvo


async def rotina(intervalo_segundos: float | None = None) -> None:
    """Tarefa do `lifespan`: um backup na subida e outro a cada intervalo.

    Falha de backup é logada e nunca derruba o app.
    """
    if not settings.gerenciador_backup_dir:
        logger.warning(
            "Backup do gerenciador desligado: defina GERENCIADOR_BACKUP_DIR."
        )
        return
    espera = (
        intervalo_segundos
        if intervalo_segundos is not None
        else settings.gerenciador_backup_intervalo_horas * 3600
    )
    while True:
        try:
            caminho = await asyncio.to_thread(fazer_backup)
            logger.info("Backup do gerenciador gravado: %s", caminho)
        except asyncio.CancelledError:
            break
        except Exception as e:  # noqa: BLE001 - nada aqui pode derrubar o app
            logger.error("Falha no backup do gerenciador: %s", e)
        try:
            await asyncio.sleep(max(espera, 1))
        except asyncio.CancelledError:
            break


def _principal(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.backup")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("agora", help="faz um backup imediato")
    sub.add_parser("listar", help="lista as cópias, da mais recente para a mais antiga")
    rest = sub.add_parser("restaurar", help="restaura uma cópia (com o app parado)")
    rest.add_argument("arquivo")
    rest.add_argument("--destino", help="caminho do banco a gravar (padrão: o real)")
    args = parser.parse_args(argv)

    try:
        if args.comando == "agora":
            print(fazer_backup())
        elif args.comando == "listar":
            if not settings.gerenciador_backup_dir:
                raise BackupDesligado("GERENCIADOR_BACKUP_DIR não está configurado")
            for p in listar(settings.gerenciador_backup_dir):
                print(f"{p.name}\t{p.stat().st_size} bytes")
        else:
            if args.destino is None:
                print(
                    "ATENÇÃO: restaurar sobre o banco real exige o app parado "
                    "(docker compose stop placar).",
                    file=sys.stderr,
                )
            print(restaurar(args.arquivo, args.destino))
    except (BackupDesligado, BackupInvalido, FileNotFoundError, sqlite3.Error) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_principal())
