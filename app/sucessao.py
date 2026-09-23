import asyncio
from datetime import UTC, datetime
from typing import Any

from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, get_quadra_lock


def verificar_sucessao_quadra_sync(
    db_path: str,
    quadra_id: str,
    online_ids: set[str],
    timeout_seconds: float | None = None,
) -> dict[str, Any] | None:
    """Verifica e executa a sucessão automática do admin caso esteja ausente.

    Retorna o novo snapshot da quadra se uma sucessão ocorreu, ou None caso contrário.
    """
    timeout = (
        timeout_seconds
        if timeout_seconds is not None
        else settings.admin_timeout_seconds
    )
    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM quadras WHERE id = ?", (quadra_id,))
        quadra = cursor.fetchone()
        if not quadra:
            return None

        cursor.execute(
            "SELECT id, apelido, papel, ultimo_visto_em FROM participantes WHERE quadra_id = ? AND papel = 'ADMIN'",
            (quadra_id,),
        )
        admin = cursor.fetchone()
        if not admin:
            # Não há admin ativo na quadra (já foi sucedido ou posto vago)
            return None

        # Se o admin estiver online, nenhuma sucessão deve ocorrer. O relógio
        # vinculado a ele conta como presença do dono (CV3.DS1.US2): o
        # telefone fica bloqueado no bolso enquanto o Eli joga.
        relogios = cursor.execute(
            """SELECT p.id, p.ultimo_visto_em FROM watch_devices d
            JOIN participantes p ON p.id = d.participant_id
            WHERE d.owner_id = ? AND d.revoked = 0""",
            (admin["id"],),
        ).fetchall()
        if admin["id"] in online_ids or any(r["id"] in online_ids for r in relogios):
            return None

        agora = datetime.now(UTC)
        ultimo_visto = max(
            datetime.fromisoformat(v)
            for v in [
                admin["ultimo_visto_em"],
                *(r["ultimo_visto_em"] for r in relogios),
            ]
        )
        segundos_offline = (agora - ultimo_visto).total_seconds()
        if segundos_offline < timeout:
            return None

        # Admin ausente por tempo >= timeout! Dispara a sucessão.
        cursor.execute(
            "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
            (quadra_id,),
        )
        partida = cursor.fetchone()
        if not partida:
            return None

        # Seleciona controladores online ordenados por criado_em ASC
        cursor.execute(
            """
            SELECT id, apelido, papel, criado_em
            FROM participantes
            WHERE quadra_id = ? AND papel = 'CONTROLADOR'
            ORDER BY criado_em ASC
            """,
            (quadra_id,),
        )
        todos_controladores = cursor.fetchall()
        controladores_online = [c for c in todos_controladores if c["id"] in online_ids]

        if controladores_online:
            novo_admin = controladores_online[0]
            # Promove o controlador online mais antigo a ADMIN
            conn.execute(
                "UPDATE participantes SET papel = 'ADMIN' WHERE id = ?",
                (novo_admin["id"],),
            )
            # Rebaixa o admin anterior a CONTROLADOR
            conn.execute(
                "UPDATE participantes SET papel = 'CONTROLADOR' WHERE id = ?",
                (admin["id"],),
            )
            # Transfere o controle ativo se estava com o admin anterior
            if quadra["controle_id"] == admin["id"]:
                conn.execute(
                    "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
                    (novo_admin["id"], quadra_id),
                )
            payload = {
                "antigo_admin_id": admin["id"],
                "antigo_admin_apelido": admin["apelido"],
                "novo_admin_id": novo_admin["id"],
                "novo_admin_apelido": novo_admin["apelido"],
                "motivo": "ausencia_admin",
            }
            autor_id = novo_admin["id"]
        else:
            # Nenhum controlador online: quadra segue sem admin (posto vago)
            conn.execute(
                "UPDATE participantes SET papel = 'CONTROLADOR' WHERE id = ?",
                (admin["id"],),
            )
            payload = {
                "antigo_admin_id": admin["id"],
                "antigo_admin_apelido": admin["apelido"],
                "novo_admin_id": None,
                "novo_admin_apelido": None,
                "motivo": "ausencia_admin",
            }
            autor_id = None

        agora_iso = agora.isoformat()
        conn.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
            (agora_iso, quadra_id),
        )
        append_evento_sync(
            db_path,
            quadra_id=quadra_id,
            partida_id=partida["id"],
            tipo=TipoEvento.ADMIN_SUCEDIDO,
            payload=payload,
            autor_id=autor_id,
            connection=conn,
        )
        conn.commit()

    from app.comandos import snapshot_sync

    return snapshot_sync(db_path, quadra_id)


async def verificar_sucessao_quadra(
    db_path: str,
    quadra_id: str,
    timeout_seconds: float | None = None,
) -> dict[str, Any] | None:
    from app.hub import hub

    lock = get_quadra_lock(quadra_id)
    async with lock:
        online_ids = await hub.participantes_online(quadra_id)
        return await asyncio.to_thread(
            verificar_sucessao_quadra_sync,
            db_path,
            quadra_id,
            online_ids,
            timeout_seconds,
        )


def verificar_controle_ocioso_sync(
    db_path: str,
    quadra_id: str,
    online_ids: set[str],
    timeout_seconds: float | None = None,
) -> dict[str, Any] | None:
    """Devolve o comando do placar ao admin quando o controlador some.

    Sucessão de admin e devolução de controle são coisas diferentes: a primeira
    troca quem manda na sala depois de dois minutos, a segunda só recoloca o
    botão na mão de quem está presente depois de quinze segundos. Uma pelada não
    pode ficar sem quem marque ponto porque o controlador guardou o celular.

    Devolve o novo snapshot quando houve devolução, ou `None` quando nada mudou.
    """
    timeout = (
        timeout_seconds
        if timeout_seconds is not None
        else settings.controle_timeout_seconds
    )
    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM quadras WHERE id = ?", (quadra_id,))
        quadra = cursor.fetchone()
        if not quadra or not quadra["controle_id"]:
            return None

        cursor.execute(
            "SELECT id, apelido, papel FROM participantes WHERE quadra_id = ? AND papel = 'ADMIN' ORDER BY criado_em ASC",
            (quadra_id,),
        )
        admin = cursor.fetchone()
        # Sem admin presente não há para quem devolver: quem cuida desse caso é
        # a sucessão, não esta rotina.
        if not admin or admin["id"] == quadra["controle_id"]:
            return None
        if admin["id"] not in online_ids:
            return None

        cursor.execute(
            "SELECT id, apelido, ultimo_visto_em FROM participantes WHERE quadra_id = ? AND id = ?",
            (quadra_id, quadra["controle_id"]),
        )
        controlador = cursor.fetchone()
        if controlador and controlador["id"] in online_ids:
            return None
        # Controle delegado ao relógio não volta por ausência: a tela apaga
        # durante o jogo. O admin retoma com "Assumir o controle".
        if (
            controlador
            and cursor.execute(
                "SELECT 1 FROM watch_devices WHERE participant_id = ? AND revoked = 0",
                (controlador["id"],),
            ).fetchone()
        ):
            return None

        agora = datetime.now(UTC)
        if controlador:
            ultimo_visto = datetime.fromisoformat(controlador["ultimo_visto_em"])
            if (agora - ultimo_visto).total_seconds() < timeout:
                return None
            apelido_ausente = controlador["apelido"]
        else:
            # O controlador não existe mais na sala (saiu ou foi removido).
            apelido_ausente = "controlador anterior"

        cursor.execute(
            "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
            (quadra_id,),
        )
        partida = cursor.fetchone()
        if not partida:
            return None

        conn.execute(
            "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
            (admin["id"], quadra_id),
        )
        agora_iso = agora.isoformat()
        conn.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
            (agora_iso, quadra_id),
        )
        append_evento_sync(
            db_path,
            quadra_id=quadra_id,
            partida_id=partida["id"],
            tipo=TipoEvento.CONTROLE_DEVOLVIDO,
            payload={
                "anterior_id": quadra["controle_id"],
                "anterior_apelido": apelido_ausente,
                "controle_id": admin["id"],
                "apelido": admin["apelido"],
                "motivo": "ausencia_controlador",
            },
            autor_id=admin["id"],
            connection=conn,
        )
        conn.commit()

    from app.comandos import snapshot_sync

    return snapshot_sync(db_path, quadra_id)


async def verificar_controle_ocioso(
    db_path: str,
    quadra_id: str,
    timeout_seconds: float | None = None,
) -> dict[str, Any] | None:
    from app.hub import hub

    lock = get_quadra_lock(quadra_id)
    async with lock:
        online_ids = await hub.participantes_online(quadra_id)
        return await asyncio.to_thread(
            verificar_controle_ocioso_sync,
            db_path,
            quadra_id,
            online_ids,
            timeout_seconds,
        )
