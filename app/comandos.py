from contextlib import nullcontext
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, carregar_eventos_sync
from app.identidade import hash_sessao
from app.projecao import projetar_estado, projetar_linha_do_tempo

# Allowlist de campos da tabela `quadras` que podem sair da borda do servidor.
# Qualquer coluna nova (sensível ou não) fica de fora do payload por padrão:
# para expor um campo é preciso adicioná-lo aqui conscientemente. Foi a ausência
# desse contrato explícito que fez `codigo_mestre` vazar no snapshot do
# WebSocket quando a coluna foi criada (débito `debt-codigo-mestre-no-websocket`).
CAMPOS_PUBLICOS_QUADRA = (
    "id",
    "nome",
    "criado_em",
    "atualizado_em",
    "controle_id",
    "controle_versao",
    "controle_relogio",
    "relogio_versao",
)

_SELECT_QUADRA_PUBLICA = (
    f"SELECT {', '.join(CAMPOS_PUBLICOS_QUADRA)} FROM quadras WHERE id = ?"
)


def projetar_quadra_publica(row) -> dict:
    """Projeta a linha de `quadras` na allowlist pública.

    Nunca receber `SELECT *` refletido direto no payload é o ponto: mesmo que a
    consulta traga colunas a mais, apenas os campos declarados saem daqui.
    """
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS_QUADRA}


def snapshot(conn, quadra_id):
    quadra = conn.execute(_SELECT_QUADRA_PUBLICA, (quadra_id,)).fetchone()
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
    sala = projetar_quadra_publica(quadra)
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


def participante_presente(linha, ids_online, limite) -> bool:
    """Diz se um participante ainda está de fato na sala.

    Mesmo critério da capacidade (`contar_presentes`): conexão viva no hub ou
    sinal de vida dentro da janela de presença. Reaproveitar o critério é o que
    impede a sala ter duas noções diferentes de "está online".
    """
    if linha is None:
        return False
    return linha["id"] in ids_online or (linha["ultimo_visto_em"] or "") >= limite


def relogio_vinculado(conn, participante_id) -> bool:
    """Participante habilitado e com relógio aprovado e não revogado."""
    return (
        conn.execute(
            """SELECT 1 FROM watch_devices d
            JOIN watch_grants g ON g.participant_id = d.participant_id
            WHERE d.participant_id = ? AND d.revoked = 0 AND d.approved_at IS NOT NULL""",
            (participante_id,),
        ).fetchone()
        is not None
    )


def alterar_controle_relogio(conn, quadra_id, novo_dono_id, dono, motivo=None):
    """Liga (novo_dono_id) ou desliga (None) a chave "Controlar pelo Relógio".

    As duas versões avançam: `relogio_versao` invalida lances do relógio feitos
    sob o modo anterior e `controle_versao` invalida toques em voo no site.
    Devolve o evento a gravar; quem chama faz o append.
    """
    conn.execute(
        """UPDATE quadras SET controle_relogio = ?, relogio_versao = relogio_versao + 1,
        controle_versao = controle_versao + 1 WHERE id = ?""",
        (novo_dono_id, quadra_id),
    )
    payload = {
        "ativo": novo_dono_id is not None,
        "dono_id": dono["id"],
        "apelido": dono["apelido"],
    }
    if motivo:
        payload["motivo"] = motivo
    return TipoEvento.CONTROLE_RELOGIO_ALTERADO, payload


def desligar_controle_relogio_sync(conn, quadra_id, participante_id, autor_id, motivo):
    """Desliga a chave se ela pertence ao participante. Devolve se mudou algo.

    Usado quando o relógio deixa de valer: revogação, novo vínculo ou acesso
    desabilitado. Sem isso o site ficaria sem poder pontuar e sem relógio.
    """
    quadra = conn.execute(
        "SELECT controle_relogio FROM quadras WHERE id = ?", (quadra_id,)
    ).fetchone()
    if not quadra or quadra["controle_relogio"] != participante_id:
        return False
    dono = conn.execute(
        "SELECT id, apelido FROM participantes WHERE id = ?", (participante_id,)
    ).fetchone()
    tipo, payload = alterar_controle_relogio(conn, quadra_id, None, dono, motivo)
    partida = conn.execute(
        "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
        (quadra_id,),
    ).fetchone()
    append_evento_sync(
        settings.db_path,
        quadra_id,
        partida["id"],
        tipo,
        payload,
        autor_id,
        connection=conn,
    )
    return True


def executar_sync(
    db_path,
    quadra_id,
    session_id,
    acao,
    *,
    equipe=None,
    versao=None,
    alvo_id=None,
    ids_online=None,
    autor_id=None,
    origem="web",
    connection=None,
    **kwargs,
):
    # A presença chega como valor, vinda da borda HTTP que conhece o hub. A
    # transação não importa o hub nem toca no event loop de dentro da thread.
    ids_online = frozenset(ids_online or ())
    # O lock de escrita cobre autorização, leitura do log e toda a alteração.
    # O relógio passa a própria conexão para gravar o recibo na mesma transação.
    with nullcontext(connection) if connection is not None else get_db(db_path) as conn:
        if connection is None:
            conn.execute("BEGIN IMMEDIATE")
        quadra = conn.execute(_SELECT_QUADRA_PUBLICA, (quadra_id,)).fetchone()
        limite = (
            datetime.now(UTC) - timedelta(seconds=settings.quadra_ttl_seconds)
        ).isoformat()
        if not quadra or quadra["atualizado_em"] < limite:
            raise HTTPException(404, "Sala não encontrada ou expirada.")
        if autor_id is not None:
            # Autor já autenticado pela credencial do relógio.
            autor = conn.execute(
                "SELECT id, papel, apelido FROM participantes WHERE quadra_id = ? AND id = ?",
                (quadra_id, autor_id),
            ).fetchone()
        else:
            if not session_id:
                raise HTTPException(401, "Participante não autenticado.")
            autor = conn.execute(
                "SELECT id, papel, apelido FROM participantes WHERE quadra_id = ? AND session_hash = ?",
                (quadra_id, hash_sessao(session_id)),
            ).fetchone()
        if not autor:
            raise HTTPException(403, "Participante não registrado nesta quadra.")
        atual = snapshot(conn, quadra_id)
        if acao in ("pontos", "desfazer"):
            if autor["papel"] not in ("ADMIN", "CONTROLADOR"):
                raise HTTPException(
                    403, "Apenas administradores e controladores podem operar o placar."
                )
            if origem == "relogio":
                # Com a chave ligada quem pontua é o relógio do dono, qualquer
                # que seja o `controle_id` do site. A base é a versão da chave.
                if quadra["controle_relogio"] != autor["id"]:
                    raise HTTPException(
                        409,
                        "O controle está no telefone. Ative Controlar pelo Relógio.",
                    )
                if versao != str(quadra["relogio_versao"]):
                    raise HTTPException(
                        409, "A chave Controlar pelo Relógio mudou depois deste lance."
                    )
            else:
                if quadra["controle_relogio"]:
                    raise HTTPException(
                        409, "O placar está sendo controlado pelo relógio."
                    )
                if quadra["controle_id"] != autor["id"]:
                    raise HTTPException(
                        403, "Outro operador está no controle do placar."
                    )
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
        elif acao == "modo_relogio":
            ativo = bool(kwargs.get("ativo"))
            dono_atual = quadra["controle_relogio"]
            if ativo:
                if dono_atual == autor["id"]:
                    return atual
                if autor["papel"] not in (
                    "ADMIN",
                    "CONTROLADOR",
                ) or not relogio_vinculado(conn, autor["id"]):
                    raise HTTPException(
                        403,
                        "Vincule o seu relógio antes de controlar o placar por ele.",
                    )
                if dono_atual:
                    raise HTTPException(
                        409, "O placar já está sendo controlado por outro relógio."
                    )
                dono = autor
            else:
                if not dono_atual:
                    return atual
                # Desligar é mais permissivo que ligar: qualquer ADMIN recupera a
                # partida se o relógio ficar sem bateria.
                if autor["papel"] != "ADMIN" and autor["id"] != dono_atual:
                    raise HTTPException(
                        403,
                        "Só o dono do relógio ou um administrador desligam o controle pelo relógio.",
                    )
                dono = conn.execute(
                    "SELECT id, apelido FROM participantes WHERE id = ?", (dono_atual,)
                ).fetchone()
            tipo, payload = alterar_controle_relogio(
                conn, quadra_id, autor["id"] if ativo else None, dono
            )
        elif acao == "assumir":
            if autor["papel"] not in ("ADMIN", "CONTROLADOR"):
                raise HTTPException(
                    403,
                    "Apenas administradores e controladores podem assumir o controle.",
                )
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
        elif acao == "transferir":
            # Passar o comando do placar para outra pessoa. Só o admin transfere,
            # só quem já tem permissão recebe, e só recebe quem está online —
            # repassar para um aparelho desconectado é deixar a partida sem
            # operador até alguém perceber.
            from app.quadras import limite_de_presenca

            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403, "Apenas administradores podem passar o controle do placar."
                )
            alvo = conn.execute(
                "SELECT id, papel, apelido, ultimo_visto_em FROM participantes WHERE quadra_id = ? AND id = ?",
                (quadra_id, alvo_id),
            ).fetchone()
            if not alvo:
                raise HTTPException(404, "Participante não encontrado nesta sala.")
            if alvo["papel"] not in ("ADMIN", "CONTROLADOR"):
                raise HTTPException(
                    400,
                    "Só é possível passar o controle para quem já é controlador ou admin.",
                )
            if not participante_presente(alvo, ids_online, limite_de_presenca()):
                raise HTTPException(
                    409,
                    f"{alvo['apelido']} está offline. O controle do placar só passa para quem está conectado.",
                )
            if quadra["controle_id"] == alvo["id"]:
                return atual
            conn.execute(
                "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
                (alvo_id, quadra_id),
            )
            tipo, payload = (
                TipoEvento.CONTROLE_TRANSFERIDO,
                {
                    "anterior_id": quadra["controle_id"],
                    "controle_id": alvo_id,
                    "apelido": alvo["apelido"],
                },
            )
        elif acao == "promover":
            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403, "Apenas administradores podem gerenciar permissões."
                )
            alvo = conn.execute(
                "SELECT id, papel, apelido FROM participantes WHERE quadra_id = ? AND id = ?",
                (quadra_id, alvo_id),
            ).fetchone()
            if not alvo:
                raise HTTPException(404, "Participante não encontrado nesta sala.")
            if alvo["id"] == autor["id"]:
                raise HTTPException(400, "Não é possível alterar o próprio papel.")
            if alvo["papel"] == "ADMIN":
                raise HTTPException(
                    400, "Não é possível alterar o papel de um administrador."
                )
            if alvo["papel"] == "CONTROLADOR":
                return atual
            conn.execute(
                "UPDATE participantes SET papel = 'CONTROLADOR' WHERE id = ?",
                (alvo_id,),
            )
            # Promover concede PERMISSÃO e nada mais. Passar o comando do placar
            # é um segundo ato, explícito, feito pela ação `transferir`. Eram a
            # mesma coisa até a CV2.DS2.US5, e por isso o admin perdia o placar
            # sem querer ao autorizar alguém a ajudar.
            tipo, payload = (
                TipoEvento.PAPEL_ALTERADO,
                {
                    "participante_id": alvo_id,
                    "apelido": alvo["apelido"],
                    "papel": "CONTROLADOR",
                    "anterior": alvo["papel"],
                },
            )
        elif acao == "revogar":
            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403, "Apenas administradores podem gerenciar permissões."
                )
            alvo = conn.execute(
                "SELECT id, papel, apelido FROM participantes WHERE quadra_id = ? AND id = ?",
                (quadra_id, alvo_id),
            ).fetchone()
            if not alvo:
                raise HTTPException(404, "Participante não encontrado nesta sala.")
            if alvo["id"] == autor["id"]:
                raise HTTPException(400, "Não é possível alterar o próprio papel.")
            if alvo["papel"] == "ADMIN":
                raise HTTPException(
                    400, "Não é possível alterar o papel de um administrador."
                )
            if alvo["papel"] == "ESPECTADOR":
                return atual
            conn.execute(
                "UPDATE participantes SET papel = 'ESPECTADOR' WHERE id = ?", (alvo_id,)
            )
            if quadra["controle_relogio"] == alvo_id:
                conn.execute(
                    "UPDATE quadras SET controle_relogio = NULL, relogio_versao = relogio_versao + 1 WHERE id = ?",
                    (quadra_id,),
                )
            # Se o participante que perdeu o controle estava operando, retorna controle ao admin
            if quadra["controle_id"] == alvo_id:
                conn.execute(
                    "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
                    (autor["id"], quadra_id),
                )
            tipo, payload = (
                TipoEvento.PAPEL_ALTERADO,
                {
                    "participante_id": alvo_id,
                    "apelido": alvo["apelido"],
                    "papel": "ESPECTADOR",
                    "anterior": alvo["papel"],
                },
            )
        elif acao == "autorizar":
            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403, "Apenas administradores podem gerenciar permissões."
                )
            alvo = conn.execute(
                "SELECT id, papel, apelido FROM participantes WHERE quadra_id = ? AND id = ?",
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
                    "anterior": alvo["papel"],
                },
            )
        elif acao == "reiniciar":
            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403, "Apenas administradores podem iniciar uma nova partida."
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
                "alvo": kwargs.get("alvo")
                if kwargs.get("alvo") is not None
                else estado["alvo"],
                "vantagem": kwargs.get("vantagem")
                if kwargs.get("vantagem") is not None
                else estado["vantagem"],
                "teto": kwargs.get("teto") if "teto" in kwargs else estado["teto"],
                "equipe_a": kwargs.get("equipe_a")
                or estado.get("equipe_a", "Equipe A"),
                "equipe_b": kwargs.get("equipe_b")
                or estado.get("equipe_b", "Equipe B"),
                "jogadores_a": kwargs.get("jogadores_a")
                if kwargs.get("jogadores_a") is not None
                else estado.get("jogadores_a", []),
                "jogadores_b": kwargs.get("jogadores_b")
                if kwargs.get("jogadores_b") is not None
                else estado.get("jogadores_b", []),
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
        elif acao == "configurar":
            if autor["papel"] != "ADMIN":
                raise HTTPException(
                    403,
                    "Apenas administradores podem ajustar as configurações da partida.",
                )
            payload_config = {}
            for k in (
                "equipe_a",
                "equipe_b",
                "jogadores_a",
                "jogadores_b",
                "alvo",
                "vantagem",
                "teto",
            ):
                if k in kwargs and kwargs[k] is not None:
                    payload_config[k] = kwargs[k]
                elif k == "teto" and "teto" in kwargs:
                    payload_config["teto"] = kwargs["teto"]
            if not payload_config:
                return atual
            tipo, payload = TipoEvento.REGRA_ALTERADA, payload_config
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
