from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from app.eventos import Evento, TipoEvento


@dataclass(frozen=True)
class EstadoPartida:
    partida_id: str | None
    pontos_a: int
    pontos_b: int
    equipe_a: str
    equipe_b: str
    alvo: int
    vantagem: bool
    teto: int | None
    encerrada: bool
    vencedor: str | None
    pontos_desfeitos: tuple[int, ...]
    eventos_ativos_seq: tuple[int, ...]
    jogadores_a: tuple[str, ...] = ()
    jogadores_b: tuple[str, ...] = ()


def avaliar_vitoria(
    pontos_a: int,
    pontos_b: int,
    alvo: int,
    vantagem: bool,
    teto: int | None,
) -> tuple[bool, str | None]:
    if vantagem:
        if teto is not None and pontos_a >= teto and pontos_a > pontos_b:
            return True, "A"
        if teto is not None and pontos_b >= teto and pontos_b > pontos_a:
            return True, "B"
        if pontos_a >= alvo and (pontos_a - pontos_b) >= 2:
            return True, "A"
        if pontos_b >= alvo and (pontos_b - pontos_a) >= 2:
            return True, "B"
    else:
        if pontos_a >= alvo and pontos_a > pontos_b:
            return True, "A"
        if pontos_b >= alvo and pontos_b > pontos_a:
            return True, "B"

    return False, None


def projetar_estado(eventos: Sequence[Evento]) -> EstadoPartida:
    partida_id: str | None = None
    alvo: int = 12
    vantagem: bool = True
    teto: int | None = None
    equipe_a: str = "Equipe A"
    equipe_b: str = "Equipe B"
    jogadores_a: list[str] = []
    jogadores_b: list[str] = []

    # Coleta ref_seq dos pontos desfeitos para anulação idempotente
    pontos_desfeitos_set: set[int] = set()
    for evento in eventos:
        if evento.tipo == TipoEvento.PONTO_DESFEITO:
            ref_seq = evento.payload.get("ref_seq")
            if ref_seq is not None:
                pontos_desfeitos_set.add(int(ref_seq))

    pontos_a = 0
    pontos_b = 0
    eventos_ativos_seq: list[int] = []

    # Varredura única do log em ordem
    for evento in eventos:
        if partida_id is None and evento.partida_id:
            partida_id = evento.partida_id

        if evento.tipo in (TipoEvento.PARTIDA_INICIADA, TipoEvento.REGRA_ALTERADA):
            payload = evento.payload
            if "alvo" in payload and payload["alvo"] is not None:
                alvo = int(payload["alvo"])
            if "vantagem" in payload and payload["vantagem"] is not None:
                vantagem = bool(payload["vantagem"])
            if "teto" in payload:
                teto = int(payload["teto"]) if payload["teto"] is not None else None
            if payload.get("equipe_a"):
                equipe_a = str(payload["equipe_a"])
            if payload.get("equipe_b"):
                equipe_b = str(payload["equipe_b"])
            if "jogadores_a" in payload and isinstance(payload["jogadores_a"], list):
                jogadores_a = [str(j) for j in payload["jogadores_a"]]
            if "jogadores_b" in payload and isinstance(payload["jogadores_b"], list):
                jogadores_b = [str(j) for j in payload["jogadores_b"]]

        elif evento.tipo == TipoEvento.PONTO_MARCADO:
            if evento.seq not in pontos_desfeitos_set:
                equipe = str(evento.payload.get("equipe", "")).upper()
                if equipe == "A":
                    pontos_a += 1
                    eventos_ativos_seq.append(evento.seq)
                elif equipe == "B":
                    pontos_b += 1
                    eventos_ativos_seq.append(evento.seq)

    # Avaliação da condição de vitória aplicando as regras vigentes
    encerrada, vencedor = avaliar_vitoria(
        pontos_a=pontos_a,
        pontos_b=pontos_b,
        alvo=alvo,
        vantagem=vantagem,
        teto=teto,
    )

    return EstadoPartida(
        partida_id=partida_id,
        pontos_a=pontos_a,
        pontos_b=pontos_b,
        equipe_a=equipe_a,
        equipe_b=equipe_b,
        alvo=alvo,
        vantagem=vantagem,
        teto=teto,
        encerrada=encerrada,
        vencedor=vencedor,
        pontos_desfeitos=tuple(sorted(pontos_desfeitos_set)),
        eventos_ativos_seq=tuple(eventos_ativos_seq),
        jogadores_a=tuple(jogadores_a),
        jogadores_b=tuple(jogadores_b),
    )


def projetar_linha_do_tempo(
    eventos: Sequence[Evento],
    apelidos_por_autor: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Projeta a narrativa cronológica da partida a partir do log append-only.

    Calcula o placar resultante a cada lance, identifica pontos desfeitos
    e mapeia o apelido do autor que registrou a ação.
    """
    apelidos = apelidos_por_autor or {}
    eventos_por_seq: dict[int, Evento] = {e.seq: e for e in eventos}

    # Coleta ref_seq dos pontos desfeitos para marcar 'anulado'
    pontos_desfeitos_set: set[int] = set()
    for e in eventos:
        if e.tipo == TipoEvento.PONTO_DESFEITO:
            ref = e.payload.get("ref_seq")
            if ref is not None:
                pontos_desfeitos_set.add(int(ref))

    itens: list[dict[str, Any]] = []
    equipe_a = "Equipe A"
    equipe_b = "Equipe B"
    alvo = 12
    vantagem = True

    pontos_a_ativos: list[int] = []
    pontos_b_ativos: list[int] = []

    for evento in eventos:
        autor_apelido = (
            apelidos.get(evento.autor_id, "Participante")
            if evento.autor_id
            else "Sistema"
        )
        equipe: str | None = None
        equipe_nome: str | None = None
        ref_seq: int | None = None
        anulado = False
        descricao = ""

        if evento.tipo == TipoEvento.PARTIDA_INICIADA:
            payload = evento.payload
            if payload.get("equipe_a"):
                equipe_a = str(payload["equipe_a"])
            if payload.get("equipe_b"):
                equipe_b = str(payload["equipe_b"])
            if "alvo" in payload and payload["alvo"] is not None:
                alvo = int(payload["alvo"])
            if "vantagem" in payload and payload["vantagem"] is not None:
                vantagem = bool(payload["vantagem"])
            teto = None
            if "teto" in payload and payload["teto"] is not None:
                teto = int(payload["teto"])

            desc_vantagem = " com vantagem de 2" if vantagem else ""
            desc_teto = f" (teto {teto})" if teto else ""
            descricao = f"Partida iniciada até {alvo} pts{desc_vantagem}{desc_teto}"

        elif evento.tipo == TipoEvento.PONTO_MARCADO:
            equipe = str(evento.payload.get("equipe", "")).upper()
            equipe_nome = (
                equipe_a if equipe == "A" else (equipe_b if equipe == "B" else equipe)
            )
            descricao = f"Ponto para {equipe_nome}"
            if evento.seq in pontos_desfeitos_set:
                anulado = True

            if equipe == "A":
                pontos_a_ativos.append(evento.seq)
            elif equipe == "B":
                pontos_b_ativos.append(evento.seq)

        elif evento.tipo == TipoEvento.PONTO_DESFEITO:
            ref = evento.payload.get("ref_seq")
            if ref is not None:
                ref_seq = int(ref)
                orig = eventos_por_seq.get(ref_seq)
                if orig:
                    orig_equipe = str(orig.payload.get("equipe", "")).upper()
                    equipe = orig_equipe
                    equipe_nome = (
                        equipe_a
                        if orig_equipe == "A"
                        else (equipe_b if orig_equipe == "B" else orig_equipe)
                    )
                    descricao = f"Ponto de {equipe_nome} anulado"
                    if orig_equipe == "A" and ref_seq in pontos_a_ativos:
                        pontos_a_ativos.remove(ref_seq)
                    elif orig_equipe == "B" and ref_seq in pontos_b_ativos:
                        pontos_b_ativos.remove(ref_seq)
                else:
                    descricao = f"Ponto #{ref_seq} anulado"
            else:
                descricao = "Ponto anulado"

        elif evento.tipo == TipoEvento.REGRA_ALTERADA:
            payload = evento.payload
            partes = []
            if "alvo" in payload and payload["alvo"] is not None:
                alvo = int(payload["alvo"])
                partes.append(f"alvo {alvo} pts")
            if payload.get("equipe_a"):
                equipe_a = str(payload["equipe_a"])
                partes.append(f"Time A: {equipe_a}")
            if payload.get("equipe_b"):
                equipe_b = str(payload["equipe_b"])
                partes.append(f"Time B: {equipe_b}")
            descricao = (
                f"Configuração da partida: {', '.join(partes)}"
                if partes
                else f"Regra alterada: alvo {alvo} pts"
            )

        elif evento.tipo == TipoEvento.CONTROLE_ASSUMIDO:
            descricao = f"{autor_apelido} assumiu o controle"

        elif evento.tipo == TipoEvento.CONTROLE_TRANSFERIDO:
            destino = evento.payload.get("apelido", "outro participante")
            descricao = f"{autor_apelido} passou o controle para {destino}"

        elif evento.tipo == TipoEvento.CONTROLE_DEVOLVIDO:
            ausente = evento.payload.get("anterior_apelido", "o controlador")
            destino = evento.payload.get("apelido", "o admin")
            descricao = f"Controle devolvido para {destino} por ausência de {ausente}"

        elif evento.tipo == TipoEvento.PAPEL_ALTERADO:
            novo_papel = evento.payload.get("papel")
            alvo_nome = evento.payload.get("apelido", "participante")
            if novo_papel == "CONTROLADOR":
                descricao = f"{autor_apelido} promoveu {alvo_nome} a controlador"
            elif novo_papel == "ESPECTADOR":
                descricao = f"{autor_apelido} revogou controlador de {alvo_nome}"
            elif novo_papel == "ADMIN":
                descricao = f"{autor_apelido} autorizou {alvo_nome} como admin"
            else:
                descricao = (
                    f"{autor_apelido} alterou papel de {alvo_nome} para {novo_papel}"
                )

        elif evento.tipo == TipoEvento.ADMIN_SUCEDIDO:
            novo_admin = evento.payload.get("novo_admin_apelido")
            antigo_admin = evento.payload.get("antigo_admin_apelido")
            if novo_admin:
                descricao = f"{novo_admin} assumiu a administração por sucessão (ausência de {antigo_admin})"
            else:
                descricao = f"Administração vaga por ausência de {antigo_admin}"

        elif evento.tipo == TipoEvento.CONTROLE_RELOGIO_ALTERADO:
            dono = evento.payload.get("apelido") or "eli"
            if evento.payload.get("ativo"):
                descricao = f"Placar passou a ser controlado pelo relógio de {dono}"
            else:
                motivo = evento.payload.get("motivo")
                descricao = "Placar voltou a ser controlado pelo telefone" + (
                    f" ({motivo})" if motivo else ""
                )

        elif evento.tipo == TipoEvento.PARTIDA_ENCERRADA:
            venc = evento.payload.get("vencedor")
            venc_nome = equipe_a if venc == "A" else (equipe_b if venc == "B" else venc)
            descricao = f"Partida encerrada. Vitória de {venc_nome}!"

        else:
            descricao = evento.tipo.replace("_", " ").capitalize()

        itens.append(
            {
                "id": evento.id,
                "seq": evento.seq,
                "tipo": evento.tipo,
                "equipe": equipe,
                "equipe_nome": equipe_nome,
                "autor_id": evento.autor_id,
                "autor_apelido": autor_apelido,
                "criado_em": evento.criado_em,
                "pontos_a": len(pontos_a_ativos),
                "pontos_b": len(pontos_b_ativos),
                "anulado": anulado,
                "ref_seq": ref_seq,
                "descricao": descricao,
            }
        )

    return itens
