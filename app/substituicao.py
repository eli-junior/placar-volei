"""Substituir jogador que saiu de um time ativo (CV8.DS3.US10, RN-08).

O substituto vem do jogador ímpar/atrasado que aguarda na fila (o time dele
desaparece) ou da lista de escalação (eliminados, que passam a jogar por um
segundo time). O time mantém vitórias e posição. Quem saiu fica ausente na
sessão (reversível: volta como "atrasado" ou na próxima rodada). Respeita a
RN-01: não forma dupla H+H havendo mulher elegível.
"""

from app.conducao import Candidato
from app.gerenciador_db import erro_de_campo, exigir_sessao_aberta
from app.jogadores import recompactar_presencas
from app.rodada import _contexto, elegiveis, montar


def opcoes(rodada: dict, por_id: dict, linhas, situacao) -> dict:
    """Quem pode sair e quem pode entrar, para a tela."""
    ativos = list(dict.fromkeys([*situacao.em_quadra, *situacao.fila, *situacao.reis]))
    saem = []
    vistos: set[str] = set()
    for t in ativos:
        for j in por_id[t]["jogadores"]:
            if j["id"] not in vistos:  # o escalado joga por dois times
                vistos.add(j["id"])
                saem.append(
                    {"id": j["id"], "nome": j["nome"], "time": por_id[t]["fila"]}
                )
    eliminados, _ = elegiveis(por_id, linhas, situacao)
    entram = [(c, "eliminado") for c in eliminados]
    for t in situacao.fila:
        if por_id[t]["incompleto"]:
            j = por_id[t]["jogadores"][0]
            entram.append(
                (
                    Candidato(
                        j["id"], j["nome"], j["genero"], j["nota"], j["ordem_chegada"]
                    ),
                    "aguardando",
                )
            )
    entram.sort(key=lambda x: (x[0].ordem_chegada, x[0].nome))
    return {
        "saem": saem,
        "entram": [
            {
                "id": c.id,
                "nome": c.nome,
                "genero": c.genero,
                "nota": c.nota,
                "origem": origem,
            }
            for c, origem in entram
        ],
    }


def substituir(conn, saiu_id, entra_id) -> None:
    sessao = exigir_sessao_aberta(conn)
    rodada = montar(conn, sessao["id"])
    if rodada is None or rodada["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não está em andamento", "sem_rodada")
    if conn.execute(
        "SELECT 1 FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    ).fetchone():
        raise erro_de_campo(
            409,
            "rodada",
            "tem uma partida chamada: encerre-a antes de substituir",
            "partida_chamada",
        )
    for campo, valor in (("saiu_id", saiu_id), ("entra_id", entra_id)):
        if not isinstance(valor, str):
            raise erro_de_campo(422, campo, "informe o jogador", "valor_invalido")
    if saiu_id == entra_id:
        raise erro_de_campo(422, "entra_id", "deve ser outro jogador", "valor_invalido")
    por_id, linhas, situacao = _contexto(conn, rodada)
    lista = opcoes(rodada, por_id, linhas, situacao)
    time = next(
        (
            por_id[t]
            for t in [*situacao.em_quadra, *situacao.fila, *situacao.reis]
            if any(j["id"] == saiu_id for j in por_id[t]["jogadores"])
        ),
        None,
    )
    if time is None:
        raise erro_de_campo(
            409, "saiu_id", "não está em um time ativo", "fora_de_time_ativo"
        )
    candidato = next((c for c in lista["entram"] if c["id"] == entra_id), None)
    if candidato is None or entra_id == saiu_id:
        raise erro_de_campo(
            409, "entra_id", "não está entre os substitutos", "fora_da_lista"
        )
    # Time aguardando que seria desfeito não pode ser o do próprio que sai.
    if candidato["origem"] == "aguardando" and any(
        j["id"] == entra_id for j in time["jogadores"]
    ):
        raise erro_de_campo(
            409, "entra_id", "não está entre os substitutos", "fora_da_lista"
        )
    parceiros = [j for j in time["jogadores"] if j["id"] != saiu_id]
    if (
        parceiros
        and parceiros[0]["genero"] == "H"
        and candidato["genero"] == "H"
        and any(c["genero"] == "M" for c in lista["entram"])
    ):
        raise erro_de_campo(
            409,
            "entra_id",
            "formaria dupla H+H havendo mulher elegível: escolha uma delas",
            "hh_com_alternativa",
        )
    escalado = 1 if candidato["origem"] == "eliminado" else 0
    if candidato["origem"] == "aguardando":
        origem_time = next(
            t
            for t in por_id.values()
            if any(j["id"] == entra_id for j in t["jogadores"])
            and t["incompleto"]
            and t["id"] in situacao.fila
        )
        conn.execute(
            "DELETE FROM time_jogadores WHERE time_id = ?", (origem_time["id"],)
        )
        conn.execute("DELETE FROM times WHERE id = ?", (origem_time["id"],))
    conn.execute(
        "UPDATE time_jogadores SET jogador_id = ?, nota = ?, ordem_chegada = ?, "
        "escalado = ? WHERE time_id = ? AND jogador_id = ?",
        (
            entra_id,
            candidato["nota"],
            _ordem(por_id, entra_id),
            escalado,
            time["id"],
            saiu_id,
        ),
    )
    conn.execute(
        "DELETE FROM presencas WHERE sessao_id = ? AND jogador_id = ?",
        (sessao["id"], saiu_id),
    )
    recompactar_presencas(conn, sessao["id"])


def _ordem(por_id: dict, jogador_id: str) -> int:
    return next(
        j["ordem_chegada"]
        for t in por_id.values()
        for j in t["jogadores"]
        if j["id"] == jogador_id
    )
