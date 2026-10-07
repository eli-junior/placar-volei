"""Situação do rei da quadra (RN-02/RN-03), derivada dos resultados. Módulo puro.

A partir da fila da rodada (os times na ordem do sorteio) e das partidas já
**encerradas**, calcula quem está em quadra, a fila, as vitórias seguidas, os
reis (na ordem em que viraram) e os eliminados. Registrar os resultados é da
US6; aqui só se lê. Sem resultados, é a situação inicial.

Regras: os dois primeiros da fila jogam; o perdedor sai (eliminado); o vencedor
fica e enfrenta o próximo; com 2 vitórias seguidas vira rei, sai da quadra e
entram os 2 próximos. Se a fila esvaziar com um time sozinho na quadra, ou com
a quadra vazia, a fase de fila termina (`fim_da_fila`). Quem enfrenta quem no
mata-mata (RN-04) fica para a US11; aqui só se informa o último vencedor.
"""

from collections import deque
from typing import NamedTuple


class TimeEntrada(NamedTuple):
    id: str
    fila: int  # posição original no sorteio (1 = primeiro)
    incompleto: bool


class ResultadoEntrada(NamedTuple):
    time_a_id: str
    time_b_id: str
    vencedor_id: str


class Situacao(NamedTuple):
    fase: str  # "fila" | "fim_da_fila"
    em_quadra: tuple[str, ...]  # ids, 0 a 2
    fila: tuple[str, ...]  # ids na ordem de entrada
    reis: tuple[str, ...]  # ids na ordem em que viraram rei
    eliminados: tuple[str, ...]  # ids de times, na ordem em que perderam
    vitorias: dict[str, int]  # vitórias seguidas de cada time
    ultimo_vencedor: str | None


def derivar(times: list[TimeEntrada], resultados: list[ResultadoEntrada]) -> Situacao:
    fila = deque(t.id for t in sorted(times, key=lambda t: t.fila))
    todos = set(fila)
    quadra: list[str] = []
    vitorias = {t: 0 for t in todos}
    reis: list[str] = []
    eliminados: list[str] = []
    ultimo: str | None = None

    def encher() -> None:
        while len(quadra) < 2 and fila:
            quadra.append(fila.popleft())

    encher()
    for r in resultados:
        if r.vencedor_id not in (r.time_a_id, r.time_b_id):
            raise ValueError("vencedor não disputou a partida")
        if sorted((r.time_a_id, r.time_b_id)) != sorted(quadra) or len(quadra) != 2:
            raise ValueError("resultado de uma partida que não estava em quadra")
        perdedor = r.time_b_id if r.vencedor_id == r.time_a_id else r.time_a_id
        quadra.remove(perdedor)
        eliminados.append(perdedor)
        vitorias[r.vencedor_id] += 1
        ultimo = r.vencedor_id
        if vitorias[r.vencedor_id] >= 2:
            quadra.remove(r.vencedor_id)
            reis.append(r.vencedor_id)
        encher()

    fase = "fila" if len(quadra) == 2 else "fim_da_fila"
    return Situacao(
        fase=fase,
        em_quadra=tuple(quadra),
        fila=tuple(fila),
        reis=tuple(reis),
        eliminados=tuple(eliminados),
        vitorias=vitorias,
        ultimo_vencedor=ultimo,
    )


def nomes_curtos(jogadores: list[dict]) -> dict[str, str]:
    """Nome de placar de cada jogador: primeiro nome, ou "Nome S." quando dois
    da rodada têm o mesmo primeiro nome (sem diferenciar caixa nem acento)."""

    def primeiro(nome: str) -> str:
        return nome.split()[0]

    def chave(nome: str) -> str:
        return primeiro(nome).casefold()

    contagem: dict[str, int] = {}
    for j in jogadores:
        contagem[chave(j["nome"])] = contagem.get(chave(j["nome"]), 0) + 1
    curtos: dict[str, str] = {}
    for j in jogadores:
        partes = j["nome"].split()
        if contagem[chave(j["nome"])] > 1 and len(partes) > 1:
            curtos[j["id"]] = f"{partes[0]} {partes[-1][0].upper()}."
        else:
            curtos[j["id"]] = partes[0]
    return curtos


def nome_da_equipe(curtos: list[str]) -> str:
    return " + ".join(curtos)


class Candidato(NamedTuple):
    id: str
    nome: str
    genero: str
    nota: int
    ordem_chegada: int


def _ordenar(candidatos: list[Candidato]) -> list[Candidato]:
    return sorted(candidatos, key=lambda c: (c.ordem_chegada, c.nome))


def lista_de_escalacao(
    *,
    genero_do_incompleto: str,
    origem: str,
    eliminados: list[Candidato],
    livres: list[Candidato],
) -> dict:
    """Quem pode ser parceiro do time incompleto (RN-05, RN-06, RN-07).

    `eliminados`: jogadores de times que perderam e hoje não jogam por nenhum
    time ativo. `livres`: jogadores da rodada que ainda não disputaram partida
    e não estão em time ativo (vazio na prática: o incompleto é o último da fila,
    então todos à frente dele já jogaram; existe para atrasados e substituições).

    - ímpar: primeiro "ainda não jogaram"; se vazio, a lista de escalação;
    - atrasado: sempre a lista de escalação.
    - gênero (RN-01): se o incompleto é homem, só mulheres, a menos que não haja
      nenhuma elegível; se é mulher, qualquer um. Dentro disso, por chegada.
    """
    if origem == "impar" and livres:
        rotulo, base = "Ainda não jogaram", livres
    else:
        rotulo, base = "Lista de escalação (eliminados)", eliminados
    base = _ordenar(base)
    evita = [c for c in base if not (genero_do_incompleto == "H" and c.genero == "H")]
    permitidos = evita or base
    aviso_hh = bool(base) and not evita and genero_do_incompleto == "H"
    return {
        "grupos": [{"rotulo": rotulo, "jogadores": permitidos}] if permitidos else [],
        "aviso_hh": aviso_hh,
        "recusados_hh": [c for c in base if c not in permitidos],
    }


def saldos(times: dict[str, list[dict]], partidas: list[dict]) -> list[dict]:
    """Saldo de cada jogador na rodada: pontos feitos − sofridos, somando todos
    os times em que atuou (o escalado joga por dois). `times` leva a lista de
    jogadores de cada time; `partidas` as encerradas com placar."""
    acumulado: dict[str, dict] = {}
    for p in partidas:
        for time_id, feitos, sofridos in (
            (p["time_a_id"], p["placar_a"], p["placar_b"]),
            (p["time_b_id"], p["placar_b"], p["placar_a"]),
        ):
            for j in times[time_id]:
                linha = acumulado.setdefault(
                    j["id"],
                    {"id": j["id"], "nome": j["nome"], "partidas": 0, "saldo": 0},
                )
                linha["partidas"] += 1
                linha["saldo"] += feitos - sofridos
    return sorted(acumulado.values(), key=lambda x: (-x["saldo"], x["nome"]))
