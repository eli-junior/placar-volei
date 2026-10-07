"""Rodada: sorteio da primeira rodada, proposta, confirmação (CV8.DS2.US3).

Só regras e dados; as rotas ficam em `app.sessao` (a rodada sempre sai junto do
estado da sessão). O algoritmo está em `app.sorteio`.

Ciclo: `proposta` (pode resortear, descartar ou confirmar) → `em_andamento`
(fila fixa; jogar as partidas é a DS3) → `cancelada`. Presença e inativação
ficam travadas enquanto houver rodada em proposta ou em andamento.
"""

import uuid

from app.conducao import (
    Candidato,
    ResultadoEntrada,
    TimeEntrada,
    derivar,
    lista_de_escalacao,
    saldos,
)
from app.gerenciador_db import agora, erro_de_campo, exigir_sessao_aberta
from app.reequilibrio import (
    duplas_anteriores,
    nota_efetiva,
    saldos_da_sessao,
)
from app.sorteio import JogadoresInsuficientes, Participante, sortear

ALVOS = (10, 12)
ATIVAS = ("proposta", "em_andamento")


def rodada_ativa(conn, sessao_id: str):
    return conn.execute(
        "SELECT * FROM rodadas WHERE sessao_id = ? AND estado IN ('proposta', 'em_andamento')",
        (sessao_id,),
    ).fetchone()


def exigir_sem_rodada_ativa(conn, sessao_id: str) -> None:
    if rodada_ativa(conn, sessao_id):
        raise erro_de_campo(
            409,
            "rodada",
            "ativa: descarte a proposta ou cancele a rodada antes de mexer na presença",
            "rodada_ativa",
        )


def montar(conn, sessao_id: str) -> dict | None:
    """A rodada ativa da sessão no formato da API, ou None."""
    r = rodada_ativa(conn, sessao_id)
    if r is None:
        return None
    times = []
    for t in conn.execute(
        "SELECT * FROM times WHERE rodada_id = ? ORDER BY fila", (r["id"],)
    ):
        jogadores = [
            {
                "id": j["jogador_id"],
                "nome": j["nome"],
                "genero": j["genero"],
                "nota": j["nota"],
                "nota_base": j["nota_base"],
                "ordem_chegada": j["ordem_chegada"],
                "escalado": bool(j["escalado"]),
            }
            for j in conn.execute(
                "SELECT tj.jogador_id, tj.nota, tj.ordem_chegada, tj.escalado, "
                "j.nome, j.genero, j.nota AS nota_base "
                "FROM time_jogadores tj JOIN jogadores j ON j.id = tj.jogador_id "
                "WHERE tj.time_id = ? ORDER BY tj.ordem_chegada",
                (t["id"],),
            )
        ]
        times.append(
            {
                "id": t["id"],
                "fila": t["fila"],
                "incompleto": bool(t["incompleto"]),
                "origem": t["origem"],
                "soma": sum(j["nota"] for j in jogadores),
                "jogadores": jogadores,
            }
        )
    return {
        "id": r["id"],
        "numero": r["numero"],
        "alvo": r["alvo"],
        "estado": r["estado"],
        "tentativa": r["tentativa"],
        "distintas": r["distintas"],
        "mata_mata_iniciado": bool(r["mata_mata_em"]),
        "times": times,
    }


def _alvo_valido(bruto) -> int:
    if isinstance(bruto, bool) or bruto not in ALVOS:
        raise erro_de_campo(422, "alvo", "deve ser 10 ou 12", "valor_invalido")
    return int(bruto)


def _participantes(conn, sessao_id: str) -> list[Participante]:
    """Presentes com a nota do sorteio: a cadastrada na primeira rodada; da
    segunda em diante, a efetiva, ajustada pelo saldo da sessão (RN-14). A
    ordem de chegada continua valendo em todas as rodadas."""
    saldos_sessao = saldos_da_sessao(conn, sessao_id)
    return [
        Participante(
            r["id"],
            r["genero"],
            nota_efetiva(r["nota"], *saldos_sessao.get(r["id"], (0, 0))),
            r["ordem"],
        )
        for r in conn.execute(
            "SELECT j.id, j.genero, j.nota, p.ordem FROM presencas p "
            "JOIN jogadores j ON j.id = p.jogador_id WHERE p.sessao_id = ? "
            "ORDER BY p.ordem",
            (sessao_id,),
        )
    ]


def _sortear(conn, sessao_id: str, tentativa: int):
    try:
        return sortear(
            _participantes(conn, sessao_id),
            tentativa,
            duplas_anteriores(conn, sessao_id),
        )
    except JogadoresInsuficientes as e:
        raise erro_de_campo(
            409,
            "rodada",
            f"precisa de ao menos 4 presentes: {e}",
            "minimo",
        ) from None


def _gravar_times(conn, rodada_id: str, resultado, notas_por_id=None) -> None:
    for time in resultado.times:
        time_id = uuid.uuid4().hex
        conn.execute(
            "INSERT INTO times (id, rodada_id, fila, incompleto) VALUES (?, ?, ?, ?)",
            (time_id, rodada_id, time.fila, int(time.incompleto)),
        )
        for p in time.jogadores:
            conn.execute(
                "INSERT INTO time_jogadores (time_id, jogador_id, nota, ordem_chegada) "
                "VALUES (?, ?, ?, ?)",
                (time_id, p.id, p.nota, p.ordem),
            )


def _apagar_times(conn, rodada_id: str) -> None:
    conn.execute(
        "DELETE FROM time_jogadores WHERE time_id IN "
        "(SELECT id FROM times WHERE rodada_id = ?)",
        (rodada_id,),
    )
    conn.execute("DELETE FROM times WHERE rodada_id = ?", (rodada_id,))


def criar_proposta(conn, alvo) -> None:
    alvo = _alvo_valido(alvo)
    sessao = exigir_sessao_aberta(conn)
    if rodada_ativa(conn, sessao["id"]):
        raise erro_de_campo(409, "rodada", "já existe uma rodada ativa", "rodada_ativa")
    resultado = _sortear(conn, sessao["id"], 0)
    numero = conn.execute(
        "SELECT COALESCE(MAX(numero), 0) + 1 FROM rodadas WHERE sessao_id = ?",
        (sessao["id"],),
    ).fetchone()[0]
    rodada_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO rodadas (id, sessao_id, numero, alvo, estado, tentativa, "
        "distintas, criado_em) VALUES (?, ?, ?, ?, 'proposta', 0, ?, ?)",
        (rodada_id, sessao["id"], numero, alvo, resultado.distintas, agora()),
    )
    _gravar_times(conn, rodada_id, resultado)


def _exigir_proposta(conn):
    sessao = exigir_sessao_aberta(conn)
    r = rodada_ativa(conn, sessao["id"])
    if r is None or r["estado"] != "proposta":
        raise erro_de_campo(
            409, "rodada", "não há proposta para esta ação", "sem_proposta"
        )
    return sessao, r


def resortear(conn, alvo=None) -> None:
    sessao, r = _exigir_proposta(conn)
    novo_alvo = _alvo_valido(alvo) if alvo is not None else r["alvo"]
    tentativa = r["tentativa"] + 1
    resultado = _sortear(conn, sessao["id"], tentativa)
    _apagar_times(conn, r["id"])
    _gravar_times(conn, r["id"], resultado)
    conn.execute(
        "UPDATE rodadas SET alvo = ?, tentativa = ?, distintas = ? WHERE id = ?",
        (novo_alvo, tentativa, resultado.distintas, r["id"]),
    )


def confirmar(conn) -> None:
    _sessao, r = _exigir_proposta(conn)
    conn.execute(
        "UPDATE rodadas SET estado = 'em_andamento', confirmado_em = ? WHERE id = ?",
        (agora(), r["id"]),
    )


def descartar(conn) -> None:
    _sessao, r = _exigir_proposta(conn)
    _apagar_times(conn, r["id"])
    conn.execute("DELETE FROM rodadas WHERE id = ?", (r["id"],))


def cancelar(conn) -> None:
    sessao = exigir_sessao_aberta(conn)
    r = rodada_ativa(conn, sessao["id"])
    if r is None or r["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não há rodada em andamento", "sem_rodada")
    conn.execute("UPDATE rodadas SET estado = 'cancelada' WHERE id = ?", (r["id"],))


def _contexto(conn, rodada: dict):
    """Resultados encerrados e a situação do rei da quadra (US5/US6)."""
    por_id = {t["id"]: t for t in rodada["times"]}
    linhas = conn.execute(
        "SELECT * FROM partidas_rodada WHERE rodada_id = ? AND estado = 'encerrada' "
        "ORDER BY ordem",
        (rodada["id"],),
    ).fetchall()
    resultados = [
        ResultadoEntrada(
            r["time_a_id"], r["time_b_id"], r["vencedor_time_id"], r["fase"]
        )
        for r in linhas
    ]
    situacao = derivar(
        [TimeEntrada(t["id"], t["fila"], t["incompleto"]) for t in rodada["times"]],
        resultados,
        rodada["mata_mata_iniciado"],
    )
    return por_id, linhas, situacao


def elegiveis(
    por_id: dict, linhas, situacao
) -> tuple[list[Candidato], list[Candidato]]:
    """(eliminados, livres): quem pode entrar num time (RN-07). `eliminados` são
    os jogadores de times que perderam e hoje não jogam por time ativo; `livres`
    os que ainda não disputaram partida e não estão em time ativo."""
    ativos = [*situacao.em_quadra, *situacao.fila, *situacao.reis]
    em_time_ativo = {j["id"] for t in ativos for j in por_id[t]["jogadores"]}
    jogaram_times = {t for r in linhas for t in (r["time_a_id"], r["time_b_id"])}
    jogaram = {j["id"] for t in jogaram_times for j in por_id[t]["jogadores"]}

    def candidato(j: dict) -> Candidato:
        return Candidato(j["id"], j["nome"], j["genero"], j["nota"], j["ordem_chegada"])

    vistos: set[str] = set()
    eliminados: list[Candidato] = []
    for t in situacao.eliminados:
        for j in por_id[t]["jogadores"]:
            if j["id"] not in em_time_ativo and j["id"] not in vistos:
                vistos.add(j["id"])
                eliminados.append(candidato(j))
    livres = [
        candidato(j)
        for t in por_id.values()
        for j in t["jogadores"]
        if j["id"] not in em_time_ativo and j["id"] not in jogaram
    ]
    return eliminados, livres


def _escalacao(rodada: dict, por_id: dict, linhas, situacao, incompleto: dict) -> dict:
    """Lista de escalação do time incompleto que está em quadra (RN-07)."""
    eliminados, livres = elegiveis(por_id, linhas, situacao)
    dono = incompleto["jogadores"][0]
    return lista_de_escalacao(
        genero_do_incompleto=dono["genero"],
        origem=incompleto["origem"],
        eliminados=eliminados,
        livres=livres,
    )


def _opcoes_substituicao(*args):
    from app.substituicao import opcoes  # evita import circular

    return opcoes(*args)


def montar_conducao(conn, rodada: dict, quadra: dict | None, ler_placar=None) -> dict:
    """Painel da condução: em quadra, fila, reis, eliminados e o gate de
    "Chamar partida". `quadra` é o vínculo com o placar (ou None)."""
    por_id, linhas, situacao = _contexto(conn, rodada)
    resultados = linhas

    def vista(time_id: str) -> dict:
        return {**por_id[time_id], "vitorias": situacao.vitorias[time_id]}

    chamada = conn.execute(
        "SELECT * FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    ).fetchone()
    partida = None
    placar = None
    if chamada:
        if ler_placar and quadra and quadra["disponivel"]:
            placar = ler_placar(chamada["quadra_id"], chamada["partida_quadra_id"])
        partida = {
            "ordem": chamada["ordem"],
            "time_a": por_id[chamada["time_a_id"]]["fila"],
            "time_b": por_id[chamada["time_b_id"]]["fila"],
            "chamada_em": chamada["chamada_em"],
            "placar": placar,
        }
    em_quadra = [vista(t) for t in situacao.em_quadra]
    ativos_ids = {
        j["id"]
        for t in [*situacao.em_quadra, *situacao.fila, *situacao.reis]
        for j in por_id[t]["jogadores"]
    }
    em_time_ativo = ativos_ids

    motivo = None
    if quadra is None:
        motivo = "Vincule uma quadra do placar para chamar a partida."
    elif not quadra["disponivel"]:
        motivo = "A quadra vinculada não está mais disponível. Vincule de novo."
    elif chamada:
        motivo = (
            "Já há uma partida chamada; ela precisa ser encerrada antes da próxima."
        )
    elif situacao.fase == "fim_da_fila":
        motivo = (
            "Não há duas equipes para chamar: a fase de fila terminou. "
            "Inicie o mata-mata."
        )
    elif situacao.fase == "campeao":
        motivo = "A rodada já tem campeão."
    escalacao = None
    if not chamada and situacao.fase == "fila":
        for t in em_quadra:
            if t["incompleto"]:
                lista = _escalacao(rodada, por_id, linhas, situacao, t)
                escalacao = {
                    "time": t["fila"],
                    "jogador": t["jogadores"][0]["nome"],
                    "origem": t["origem"],
                    "grupos": [
                        {
                            "rotulo": g["rotulo"],
                            "jogadores": [
                                {
                                    "id": c.id,
                                    "nome": c.nome,
                                    "genero": c.genero,
                                    "nota": c.nota,
                                }
                                for c in g["jogadores"]
                            ],
                        }
                        for g in lista["grupos"]
                    ],
                    "aviso_hh": lista["aviso_hh"],
                    "ninguem": not lista["grupos"],
                }
                if motivo is None:
                    motivo = (
                        f"Escolha o parceiro do Time {t['fila']} antes de chamar a "
                        "partida."
                    )
                break
    encerradas = len(resultados)
    historico = [
        {
            "ordem": r["ordem"],
            "time_a": por_id[r["time_a_id"]]["fila"],
            "time_b": por_id[r["time_b_id"]]["fila"],
            "fase": r["fase"],
            "placar_a": r["placar_a"],
            "placar_b": r["placar_b"],
            "vencedor": por_id[r["vencedor_time_id"]]["fila"],
            "encerrada_em": r["encerrada_em"],
        }
        for r in conn.execute(
            "SELECT * FROM partidas_rodada WHERE rodada_id = ? AND estado = 'encerrada' "
            "ORDER BY ordem",
            (rodada["id"],),
        )
    ]
    motivo_encerrar = None
    if chamada:
        if placar is None:
            motivo_encerrar = "A quadra vinculada não está disponível: vincule de novo para ler o placar."
        elif not placar["mesma_partida"]:
            motivo_encerrar = (
                "O placar está com outra partida: a chamada foi trocada na quadra."
            )
        elif not placar["encerrada"]:
            motivo_encerrar = (
                f"Em jogo no placar ({placar['a']} × {placar['b']}): "
                "encerre quando terminar."
            )
    return {
        "fase": situacao.fase,
        "em_quadra": em_quadra,
        "partida": partida,
        "fila": [vista(t) for t in situacao.fila],
        "reis": [
            {**vista(t), "ordem": i} for i, t in enumerate(situacao.reis, start=1)
        ],
        # Quem foi escalado e joga por outro time não está eliminado agora.
        "eliminados": [
            {**j, "time": por_id[t]["fila"]}
            for t in situacao.eliminados
            for j in por_id[t]["jogadores"]
            if j["id"] not in em_time_ativo
        ],
        "escalacao": escalacao,
        "saldos": saldos(
            {t: v["jogadores"] for t, v in por_id.items()},
            [dict(r) for r in linhas],
        ),
        "partidas_encerradas": encerradas,
        "historico": historico,
        "pode_encerrar": bool(chamada) and motivo_encerrar is None,
        "motivo_encerrar": motivo_encerrar,
        "finalista": (
            vista(situacao.desafiante)
            if situacao.fase == "fim_da_fila" and situacao.desafiante
            else None
        ),
        "mata_mata": (
            {
                "iniciado": situacao.fase in ("mata_mata", "campeao"),
                "desafiante": vista(situacao.desafiante),
                "rivais": [vista(t) for t in situacao.rivais],
                "campeao": vista(situacao.campeao) if situacao.campeao else None,
            }
            if situacao.desafiante
            else None
        ),
        "pode_iniciar_mata_mata": situacao.fase == "fim_da_fila",
        "substituicao": (
            None
            if chamada or situacao.fase == "campeao"
            else _opcoes_substituicao(rodada, por_id, linhas, situacao)
        ),
        "pode_chamar": motivo is None,
        "motivo": motivo,
    }


def escalar_parceiro(conn, jogador_id) -> None:
    """Completa o time incompleto que está em quadra com um jogador da lista
    de escalação (RN-05/06/07). Revalida tudo na transação."""
    sessao = exigir_sessao_aberta(conn)
    rodada = montar(conn, sessao["id"])
    if rodada is None or rodada["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não está em andamento", "sem_rodada")
    chamada = conn.execute(
        "SELECT 1 FROM partidas_rodada WHERE rodada_id = ? AND estado = 'chamada'",
        (rodada["id"],),
    ).fetchone()
    if chamada:
        raise erro_de_campo(
            409,
            "rodada",
            "tem uma partida chamada: escolha o parceiro antes de chamar",
            "partida_chamada",
        )
    por_id, linhas, situacao = _contexto(conn, rodada)
    incompleto = next(
        (por_id[t] for t in situacao.em_quadra if por_id[t]["incompleto"]),
        None,
    )
    if situacao.fase != "fila" or incompleto is None:
        raise erro_de_campo(
            409, "rodada", "não há time incompleto esperando parceiro", "sem_incompleto"
        )
    lista = _escalacao(rodada, por_id, linhas, situacao, incompleto)
    permitidos = {c.id for g in lista["grupos"] for c in g["jogadores"]}
    if not isinstance(jogador_id, str) or jogador_id not in permitidos:
        if isinstance(jogador_id, str) and jogador_id in {
            c.id for c in lista["recusados_hh"]
        }:
            raise erro_de_campo(
                409,
                "jogador",
                "formaria dupla H+H havendo mulher elegível: escolha uma delas",
                "hh_com_alternativa",
            )
        raise erro_de_campo(
            409, "jogador", "não está na lista de escalação", "fora_da_lista"
        )
    ja = next(
        j for t in por_id.values() for j in t["jogadores"] if j["id"] == jogador_id
    )
    conn.execute(
        "INSERT INTO time_jogadores (time_id, jogador_id, nota, ordem_chegada, escalado) "
        "VALUES (?, ?, ?, ?, 1)",
        (incompleto["id"], jogador_id, ja["nota"], ja["ordem_chegada"]),
    )
    conn.execute("UPDATE times SET incompleto = 0 WHERE id = ?", (incompleto["id"],))


def registrar_campeao(conn, sessao_id: str) -> bool:
    """Se o mata-mata já definiu o campeão, grava-o e encerra a rodada, o que
    libera o próximo sorteio (CA5). Devolve se encerrou."""
    rodada = montar(conn, sessao_id)
    if rodada is None or rodada["estado"] != "em_andamento":
        return False
    _, _, situacao = _contexto(conn, rodada)
    if situacao.fase != "campeao":
        return False
    conn.execute(
        "UPDATE rodadas SET estado = 'encerrada', campeao_time_id = ? WHERE id = ?",
        (situacao.campeao, rodada["id"]),
    )
    return True


def iniciar_mata_mata(conn) -> None:
    """Fecha a fase de fila e começa o mata-mata (RN-04): daqui em diante
    ninguém entra. Sem reis a rodada já tem campeão e se encerra."""
    sessao = exigir_sessao_aberta(conn)
    rodada = montar(conn, sessao["id"])
    if rodada is None or rodada["estado"] != "em_andamento":
        raise erro_de_campo(409, "rodada", "não está em andamento", "sem_rodada")
    _, _, situacao = _contexto(conn, rodada)
    if situacao.fase != "fim_da_fila":
        raise erro_de_campo(
            409, "rodada", "ainda não está no fim da fila", "fora_do_fim_da_fila"
        )
    conn.execute(
        "UPDATE rodadas SET mata_mata_em = ? WHERE id = ?", (agora(), rodada["id"])
    )
    registrar_campeao(conn, sessao["id"])


def ultimo_campeao(conn, sessao_id: str) -> dict | None:
    """O campeão da rodada mais recente da sessão, se ela terminou em mata-mata."""
    r = conn.execute(
        "SELECT r.numero, t.fila, t.id AS time_id FROM rodadas r "
        "JOIN times t ON t.id = r.campeao_time_id "
        "WHERE r.sessao_id = ? AND r.estado = 'encerrada' "
        "ORDER BY r.numero DESC LIMIT 1",
        (sessao_id,),
    ).fetchone()
    if r is None:
        return None
    nomes = [
        j["nome"]
        for j in conn.execute(
            "SELECT j.nome FROM time_jogadores tj JOIN jogadores j "
            "ON j.id = tj.jogador_id WHERE tj.time_id = ? ORDER BY tj.ordem_chegada",
            (r["time_id"],),
        )
    ]
    return {"rodada": r["numero"], "time": r["fila"], "jogadores": nomes}
