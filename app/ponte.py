"""Ponte entre o gerenciador e o placar (CV8.DS3.US5).

O gerenciador é durável e protegido pelo `OWNER_SECRET`; as quadras do placar
são efêmeras (banco apagado a cada subida, sala expira após 1 h parada). A ponte:

- **vínculo:** a sessão guarda o código de uma quadra do placar; a cada uso o
  vínculo é conferido e pode estar "indisponível";
- **chamar partida:** o servidor age como o ADMIN da quadra (a autoridade vem
  do `OWNER_SECRET`, como o relógio de um admin) e carrega os dois times, o
  alvo e a vantagem de 2 no placar, zerado.
"""

import asyncio
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app import rodada as regras_rodada
from app.api import autenticar_owner, transmitir_estado
from app.comandos import executar_sync, snapshot_sync
from app.conducao import nome_da_equipe, nomes_curtos
from app.config import settings
from app.db import get_db
from app.eventos import get_quadra_lock
from app.gerenciador_db import (
    agora,
    conectar,
    erro_de_campo,
    escrita,
    exigir_sessao_aberta,
    sessao_aberta,
)
from app.quadras import obter_quadra_sync
from app.sincronia import publicar

CODIGO = re.compile(r"\d{5}")


def info_quadra(quadra_id: str | None) -> dict | None:
    """Vínculo da sessão com o placar, conferido agora. None se não há vínculo."""
    if not quadra_id:
        return None
    quadra = obter_quadra_sync(settings.db_path, quadra_id)
    return {
        "codigo": quadra_id,
        "nome": quadra["nome"] if quadra else None,
        "disponivel": quadra is not None and _admin_da_quadra(quadra_id) is not None,
    }


def _admin_da_quadra(quadra_id: str) -> str | None:
    with get_db(settings.db_path) as conn:
        linha = conn.execute(
            "SELECT id FROM participantes WHERE quadra_id = ? AND papel = 'ADMIN' "
            "ORDER BY criado_em LIMIT 1",
            (quadra_id,),
        ).fetchone()
    return linha["id"] if linha else None


def manter_quadras_da_rodada() -> int:
    """Renova o `atualizado_em` da quadra de uma rodada em andamento (CV8.DS7.TS2).

    O TTL de 1 h vale para sala esquecida, não para um joguinho no meio: a regra
    do TTL fica intacta e esta é a única exceção. Devolve quantas quadras renovou."""
    conn = conectar(settings.gerenciador_db_path)
    try:
        codigos = [
            r["quadra_id"]
            for r in conn.execute(
                "SELECT DISTINCT s.quadra_id FROM sessoes s "
                "JOIN rodadas r ON r.sessao_id = s.id "
                "WHERE s.encerrada_em IS NULL AND s.quadra_id IS NOT NULL "
                "AND r.estado = 'em_andamento'"
            )
        ]
    finally:
        conn.close()
    if not codigos:
        return 0
    with get_db(settings.db_path) as db:
        db.execute("BEGIN IMMEDIATE")
        marcas = ",".join("?" for _ in codigos)
        renovadas = db.execute(
            f"UPDATE quadras SET atualizado_em = ? WHERE id IN ({marcas})",
            (datetime.now(UTC).isoformat(), *codigos),
        ).rowcount
        db.commit()
    return renovadas


def reconciliar_vinculo(conn) -> None:
    """Desfaz o vínculo da sessão com uma quadra que não existe mais (CV8.DS7.TS2).

    Com partida chamada o código fica: a tela mostra a quadra indisponível e a
    saída é anular a partida; no estado seguinte o vínculo é limpo."""
    sessao = sessao_aberta(conn)
    if sessao is None or not sessao["quadra_id"]:
        return
    if obter_quadra_sync(settings.db_path, sessao["quadra_id"]) is not None:
        return
    with escrita(conn):
        if conn.execute(
            "SELECT 1 FROM partidas_rodada p JOIN rodadas r ON r.id = p.rodada_id "
            "WHERE r.sessao_id = ? AND r.estado = 'em_andamento' AND p.estado = 'chamada'",
            (sessao["id"],),
        ).fetchone():
            return
        conn.execute(
            "UPDATE sessoes SET quadra_id = NULL WHERE id = ?", (sessao["id"],)
        )


def vincular_sync(codigo) -> None:
    if isinstance(codigo, int) and not isinstance(codigo, bool):
        codigo = f"{codigo:05d}"
    if not isinstance(codigo, str) or not CODIGO.fullmatch(codigo.strip()):
        raise erro_de_campo(422, "codigo", "deve ter 5 dígitos", "formato")
    codigo = codigo.strip()
    if info_quadra(codigo) is None or not info_quadra(codigo)["disponivel"]:
        raise erro_de_campo(
            409,
            "quadra",
            "não encontrada ou expirada: confira o código",
            "indisponivel",
        )
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            _exigir_sem_partida_chamada(conn, sessao["id"])
            conn.execute(
                "UPDATE sessoes SET quadra_id = ? WHERE id = ?", (codigo, sessao["id"])
            )
    finally:
        conn.close()


def desvincular_sync() -> None:
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            _exigir_sem_partida_chamada(conn, sessao["id"])
            conn.execute(
                "UPDATE sessoes SET quadra_id = NULL WHERE id = ?", (sessao["id"],)
            )
    finally:
        conn.close()


def _exigir_sem_partida_chamada(conn, sessao_id: str) -> None:
    aberta = conn.execute(
        "SELECT 1 FROM partidas_rodada p JOIN rodadas r ON r.id = p.rodada_id "
        "WHERE r.sessao_id = ? AND r.estado = 'em_andamento' AND p.estado = 'chamada'",
        (sessao_id,),
    ).fetchone()
    if aberta:
        raise erro_de_campo(
            409,
            "quadra",
            "tem uma partida chamada: encerre-a ou anule-a antes de trocar o vínculo",
            "partida_chamada",
        )


def ler_placar(quadra_id: str, partida_quadra_id: str | None) -> dict | None:
    """Placar atual da quadra vinculada, ou None se ela não está disponível.
    `mesma_partida` diz se ainda é a partida que a chamada carregou."""
    try:
        snap = snapshot_sync(settings.db_path, quadra_id)
    except HTTPException:
        return None
    e = snap["estado_partida"]
    return {
        "a": e["pontos_a"],
        "b": e["pontos_b"],
        "encerrada": bool(e["encerrada"]),
        "vencedor": e["vencedor"],
        "mesma_partida": partida_quadra_id is None
        or snap["partida_id"] == partida_quadra_id,
    }


def _registrar_chamada() -> dict:
    """Valida o gate e grava a partida como chamada (uma só por rodada, pelo
    índice do banco). Devolve o que o placar precisa receber."""
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            rodada = regras_rodada.montar(conn, sessao["id"])
            if rodada is None or rodada["estado"] != "em_andamento":
                raise erro_de_campo(
                    409,
                    "rodada",
                    "não está em andamento: confirme a proposta antes",
                    "sem_rodada",
                )
            quadra = info_quadra(sessao["quadra_id"])
            conducao = regras_rodada.montar_conducao(conn, rodada, quadra)
            if not conducao["pode_chamar"]:
                raise erro_de_campo(
                    409, "rodada", conducao["motivo"].rstrip("."), "nao_pode_chamar"
                )
            _exigir_placar_livre(quadra["codigo"])
            time_a, time_b = conducao["em_quadra"]
            curtos = nomes_curtos([j for t in rodada["times"] for j in t["jogadores"]])

            def equipe(time: dict) -> tuple[str, list[str]]:
                nomes = [curtos[j["id"]] for j in time["jogadores"]]
                return nome_da_equipe(nomes), nomes

            nome_a, jog_a = equipe(time_a)
            nome_b, jog_b = equipe(time_b)
            ordem = conn.execute(
                "SELECT COALESCE(MAX(ordem), 0) + 1 FROM partidas_rodada WHERE rodada_id = ?",
                (rodada["id"],),
            ).fetchone()[0]
            partida_id = uuid.uuid4().hex
            conn.execute(
                "INSERT INTO partidas_rodada (id, rodada_id, ordem, time_a_id, time_b_id, "
                "estado, fase, quadra_id, chamada_em) VALUES (?, ?, ?, ?, ?, 'chamada', ?, ?, ?)",
                (
                    partida_id,
                    rodada["id"],
                    ordem,
                    time_a["id"],
                    time_b["id"],
                    conducao["fase"],
                    quadra["codigo"],
                    agora(),
                ),
            )
            return {
                "partida_id": partida_id,
                "quadra_id": quadra["codigo"],
                "alvo": rodada["alvo"],
                "equipe_a": nome_a,
                "jogadores_a": jog_a,
                "equipe_b": nome_b,
                "jogadores_b": jog_b,
            }
    finally:
        conn.close()


def _exigir_placar_livre(quadra_id: str) -> None:
    """Não zera uma partida em andamento com pontos: o operador decide antes."""
    try:
        estado = snapshot_sync(settings.db_path, quadra_id)["estado_partida"]
    except HTTPException:
        raise erro_de_campo(
            409, "quadra", "não está mais disponível: vincule de novo", "indisponivel"
        ) from None
    if not estado["encerrada"] and (estado["pontos_a"] or estado["pontos_b"]):
        raise erro_de_campo(
            409,
            "quadra",
            f"tem uma partida em andamento ({estado['pontos_a']} × {estado['pontos_b']}): "
            "encerre ou reinicie no placar antes",
            "partida_em_andamento",
        )


def _desfazer_chamada(partida_id: str) -> None:
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            conn.execute("DELETE FROM partidas_rodada WHERE id = ?", (partida_id,))
    finally:
        conn.close()


def _guardar_partida_do_placar(partida_id: str, partida_quadra_id: str) -> None:
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            conn.execute(
                "UPDATE partidas_rodada SET partida_quadra_id = ? WHERE id = ?",
                (partida_quadra_id, partida_id),
            )
    finally:
        conn.close()


async def avisar_quadra_vinculada(estado: dict, quadra_id: str | None = None) -> None:
    """Reenvia o snapshot à quadra vinculada: a trava de reinício (`em_joguinho`)
    muda com a chamada, o encerramento e a anulação da partida. Nunca levanta."""
    codigo = quadra_id or (estado.get("quadra") or {}).get("codigo")
    if not codigo:
        return
    try:
        await transmitir_estado(codigo, avisar=False)
    except HTTPException:  # quadra expirada: o joguinho segue
        return


async def _carregar_no_placar(dados: dict) -> str:
    quadra_id = dados["quadra_id"]
    admin_id = await asyncio.to_thread(_admin_da_quadra, quadra_id)
    if admin_id is None:
        raise erro_de_campo(
            409, "quadra", "não está mais disponível: vincule de novo", "indisponivel"
        )
    async with get_quadra_lock(quadra_id):
        try:
            resultado = await asyncio.to_thread(
                executar_sync,
                settings.db_path,
                quadra_id,
                None,
                "reiniciar",
                autor_id=admin_id,
                dono_admin=True,
                zerar=True,
                via_joguinho=True,
                alvo=dados["alvo"],
                vantagem=True,
                equipe_a=dados["equipe_a"],
                equipe_b=dados["equipe_b"],
                jogadores_a=dados["jogadores_a"],
                jogadores_b=dados["jogadores_b"],
            )
        except HTTPException as e:
            if e.status_code == 404:
                raise erro_de_campo(
                    409,
                    "quadra",
                    "não está mais disponível: vincule de novo",
                    "indisponivel",
                ) from None
            raise
        await transmitir_estado(quadra_id, resultado)
    return resultado["partida_id"]


async def chamar_partida() -> dict:
    from app.sessao import estado_sync

    dados = await asyncio.to_thread(_registrar_chamada)
    try:
        partida_quadra_id = await _carregar_no_placar(dados)
    except BaseException:
        await asyncio.to_thread(_desfazer_chamada, dados["partida_id"])
        raise
    await asyncio.to_thread(
        _guardar_partida_do_placar, dados["partida_id"], partida_quadra_id
    )
    return await asyncio.to_thread(estado_sync)


def _registrar_encerramento() -> None:
    """Lê o placar final da quadra e grava o resultado da partida chamada."""
    conn = conectar(settings.gerenciador_db_path)
    try:
        with escrita(conn):
            sessao = exigir_sessao_aberta(conn)
            rodada = regras_rodada.montar(conn, sessao["id"])
            if rodada is None or rodada["estado"] != "em_andamento":
                raise erro_de_campo(
                    409, "rodada", "não está em andamento", "sem_rodada"
                )
            chamada = conn.execute(
                "SELECT * FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
                (rodada["id"],),
            ).fetchone()
            if chamada is None:
                raise erro_de_campo(
                    409,
                    "rodada",
                    "não tem partida chamada para encerrar",
                    "sem_partida",
                )
            placar = ler_placar(chamada["quadra_id"], chamada["partida_quadra_id"])
            if placar is None:
                raise erro_de_campo(
                    409,
                    "quadra",
                    "não está mais disponível: anule a partida chamada para trocar "
                    "de quadra (ela continua aguardando o resultado)",
                    "indisponivel",
                )
            if not placar["mesma_partida"]:
                raise erro_de_campo(
                    409,
                    "quadra",
                    "tem outra partida em andamento: a partida chamada foi trocada "
                    "no placar e o resultado dela não pode ser lido",
                    "partida_trocada",
                )
            if not placar["encerrada"] or placar["vencedor"] not in ("A", "B"):
                raise erro_de_campo(
                    409,
                    "rodada",
                    f"A partida ainda não terminou no placar ({placar['a']} × {placar['b']})",
                    "em_jogo",
                )
            vencedor = (
                chamada["time_a_id"]
                if placar["vencedor"] == "A"
                else chamada["time_b_id"]
            )
            conn.execute(
                "UPDATE partidas_rodada SET estado = 'encerrada', placar_a = ?, "
                "placar_b = ?, vencedor_time_id = ?, encerrada_em = ? WHERE id = ?",
                (placar["a"], placar["b"], vencedor, agora(), chamada["id"]),
            )
            conn.execute(
                "UPDATE rodadas SET desfeito = 0 WHERE id = ?", (chamada["rodada_id"],)
            )
            regras_rodada.registrar_campeao(conn, sessao["id"])
    finally:
        conn.close()


async def encerrar_partida() -> dict:
    from app.sessao import estado_sync

    await asyncio.to_thread(_registrar_encerramento)
    estado = await asyncio.to_thread(estado_sync)
    await avisar_quadra_vinculada(estado)
    return estado


class CodigoBody(BaseModel):
    codigo: Any = None


router = APIRouter(tags=["ponte"])


@router.put("/api/sessao/quadra")
async def put_quadra(body: CodigoBody, request: Request):
    from app.sessao import estado_sync

    autenticar_owner(request)
    await asyncio.to_thread(vincular_sync, body.codigo)
    estado = await asyncio.to_thread(estado_sync)
    await publicar(estado)
    return estado


@router.delete("/api/sessao/quadra")
async def delete_quadra(request: Request):
    from app.sessao import estado_sync

    autenticar_owner(request)
    await asyncio.to_thread(desvincular_sync)
    estado = await asyncio.to_thread(estado_sync)
    await publicar(estado)
    return estado
