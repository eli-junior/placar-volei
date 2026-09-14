from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, carregar_eventos_sync
from app.identidade import hash_sessao
from app.projecao import projetar_estado, projetar_linha_do_tempo


def snapshot(conn, quadra_id):
    quadra = conn.execute("SELECT * FROM quadras WHERE id = ?", (quadra_id,)).fetchone()
    if not quadra:
        raise HTTPException(404, "Sala não encontrada ou expirada.")
    partida = conn.execute(
        "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
        (quadra_id,),
    ).fetchone()
    eventos = carregar_eventos_sync(settings.db_path, partida["id"], connection=conn)
    participantes = [
        dict(row)
        for row in conn.execute(
            "SELECT id, quadra_id, apelido, papel, criado_em, ultimo_visto_em FROM participantes WHERE quadra_id = ? ORDER BY criado_em",
            (quadra_id,),
        )
    ]
    sala = dict(quadra)
    sala["partida_id"] = partida["id"]
    return {
        "quadra": sala,
        "partida_id": partida["id"],
        "seq": eventos[-1].seq if eventos else 0,
        "estado_partida": asdict(projetar_estado(eventos)),
        "participantes": participantes,
        "linha_do_tempo": projetar_linha_do_tempo(
            eventos, {p["id"]: p["apelido"] for p in participantes}
        ),
    }


def snapshot_sync(db_path, quadra_id):
    with get_db(db_path) as conn:
        conn.execute("BEGIN")
        return snapshot(conn, quadra_id)


def executar_sync(
    db_path, quadra_id, session_id, acao, *, equipe=None, versao=None, alvo_id=None
):
    # O lock de escrita cobre autorização, leitura do log e toda a alteração.
    with get_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        quadra = conn.execute(
            "SELECT * FROM quadras WHERE id = ?", (quadra_id,)
        ).fetchone()
        limite = (
            datetime.now(UTC) - timedelta(seconds=settings.quadra_ttl_seconds)
        ).isoformat()
        if not quadra or quadra["atualizado_em"] < limite:
            raise HTTPException(404, "Sala não encontrada ou expirada.")
        if not session_id:
            raise HTTPException(401, "Participante não autenticado.")
        autor = conn.execute(
            "SELECT id, papel FROM participantes WHERE quadra_id = ? AND session_hash = ?",
            (quadra_id, hash_sessao(session_id)),
        ).fetchone()
        if not autor or autor["papel"] != "ADMIN":
            raise HTTPException(403, "Apenas administradores podem operar o placar.")
        atual = snapshot(conn, quadra_id)
        if acao in ("pontos", "desfazer"):
            if quadra["controle_id"] != autor["id"]:
                raise HTTPException(403, "Outro admin está no controle do placar.")
            if versao is None:
                raise HTTPException(
                    428, "Atualize o estado do controle antes de operar."
                )
            if versao != str(quadra["controle_versao"]):
                raise HTTPException(
                    409, "O controle mudou. Aguarde a atualização do placar."
                )
            estado = atual["estado_partida"]
            if acao == "pontos":
                equipe = equipe.strip().upper()
                if equipe not in ("A", "B"):
                    raise HTTPException(422, "Equipe deve ser 'A' ou 'B'.")
                if estado["encerrada"]:
                    raise HTTPException(400, "A partida já está encerrada.")
                tipo, payload = TipoEvento.PONTO_MARCADO, {"equipe": equipe}
            else:
                if not estado["eventos_ativos_seq"]:
                    raise HTTPException(400, "Nenhum ponto para desfazer.")
                tipo, payload = (
                    TipoEvento.PONTO_DESFEITO,
                    {"ref_seq": estado["eventos_ativos_seq"][-1]},
                )
        elif acao == "assumir":
            if quadra["controle_id"] == autor["id"]:
                return atual
            conn.execute(
                "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
                (autor["id"], quadra_id),
            )
            tipo, payload = (
                TipoEvento.CONTROLE_ASSUMIDO,
                {"anterior_id": quadra["controle_id"], "controle_id": autor["id"]},
            )
        elif acao == "autorizar":
            alvo = conn.execute(
                "SELECT papel, apelido FROM participantes WHERE quadra_id = ? AND id = ?",
                (quadra_id, alvo_id),
            ).fetchone()
            if not alvo:
                raise HTTPException(404, "Participante não encontrado nesta sala.")
            if alvo["papel"] == "ADMIN":
                return atual
            conn.execute(
                "UPDATE participantes SET papel = 'ADMIN' WHERE id = ?", (alvo_id,)
            )
            tipo, payload = (
                TipoEvento.PAPEL_ALTERADO,
                {
                    "participante_id": alvo_id,
                    "apelido": alvo["apelido"],
                    "papel": "ADMIN",
                },
            )
        elif acao == "reiniciar":
            if quadra["controle_id"] != autor["id"]:
                raise HTTPException(
                    403, "Apenas quem está no controle pode iniciar uma nova partida."
                )
            estado = atual["estado_partida"]
            if not estado["encerrada"]:
                raise HTTPException(400, "A partida atual ainda não foi encerrada.")

            agora = datetime.now(UTC).isoformat()
            conn.execute(
                "UPDATE partidas SET status = 'ENCERRADA', encerrado_em = COALESCE(encerrado_em, ?) WHERE id = ?",
                (agora, atual["partida_id"]),
            )
            import uuid

            nova_partida_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO partidas (id, quadra_id, status, criado_em) VALUES (?, ?, 'EM_ANDAMENTO', ?)",
                (nova_partida_id, quadra_id, agora),
            )
            payload_nova = {
                "alvo": estado["alvo"],
                "vantagem": estado["vantagem"],
                "teto": estado["teto"],
                "equipe_a": estado["equipe_a"],
                "equipe_b": estado["equipe_b"],
            }
            evento = append_evento_sync(
                db_path,
                quadra_id,
                nova_partida_id,
                TipoEvento.PARTIDA_INICIADA,
                payload_nova,
                autor["id"],
                connection=conn,
            )
            conn.execute(
                "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
                (agora, quadra_id),
            )
            resultado = snapshot(conn, quadra_id)
            resultado["evento"] = asdict(evento)
            return resultado
        else:
            raise ValueError("Comando desconhecido.")
        evento = append_evento_sync(
            db_path,
            quadra_id,
            atual["partida_id"],
            tipo,
            payload,
            autor["id"],
            connection=conn,
        )

        # Se foi ponto marcado, verifica se a partida encerrou para gravar PARTIDA_ENCERRADA
        if tipo == TipoEvento.PONTO_MARCADO:
            eventos_partida = carregar_eventos_sync(
                db_path, atual["partida_id"], connection=conn
            )
            novo_estado = projetar_estado(eventos_partida)
            if novo_estado.encerrada:
                append_evento_sync(
                    db_path,
                    quadra_id,
                    atual["partida_id"],
                    TipoEvento.PARTIDA_ENCERRADA,
                    {
                        "vencedor": novo_estado.vencedor,
                        "pontos_a": novo_estado.pontos_a,
                        "pontos_b": novo_estado.pontos_b,
                        "alvo": novo_estado.alvo,
                        "vantagem": novo_estado.vantagem,
                        "teto": novo_estado.teto,
                    },
                    autor["id"],
                    connection=conn,
                )
                conn.execute(
                    "UPDATE partidas SET status = 'ENCERRADA', encerrado_em = ? WHERE id = ?",
                    (datetime.now(UTC).isoformat(), atual["partida_id"]),
                )

        # Se foi ponto desfeito, verifica se a partida foi reaberta
        elif tipo == TipoEvento.PONTO_DESFEITO:
            eventos_partida = carregar_eventos_sync(
                db_path, atual["partida_id"], connection=conn
            )
            novo_estado = projetar_estado(eventos_partida)
            if not novo_estado.encerrada:
                conn.execute(
                    "UPDATE partidas SET status = 'EM_ANDAMENTO', encerrado_em = NULL WHERE id = ?",
                    (atual["partida_id"],),
                )

        conn.execute(
            "UPDATE quadras SET atualizado_em = ? WHERE id = ?",
            (datetime.now(UTC).isoformat(), quadra_id),
        )
        resultado = snapshot(conn, quadra_id)
        resultado["evento"] = asdict(evento)
        return resultado
