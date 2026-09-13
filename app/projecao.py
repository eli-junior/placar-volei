from collections.abc import Sequence
from dataclasses import dataclass

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

        if evento.tipo == TipoEvento.PARTIDA_INICIADA:
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

        elif evento.tipo == TipoEvento.REGRA_ALTERADA:
            payload = evento.payload
            if "alvo" in payload and payload["alvo"] is not None:
                alvo = int(payload["alvo"])
            if "vantagem" in payload and payload["vantagem"] is not None:
                vantagem = bool(payload["vantagem"])
            if "teto" in payload:
                teto = int(payload["teto"]) if payload["teto"] is not None else None

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
    )
