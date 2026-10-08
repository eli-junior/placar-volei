"""Situação do rei da quadra (RN-02/RN-03), derivada dos resultados. Módulo puro.

A partir da fila da rodada (os times na ordem do sorteio) e das partidas já
**encerradas**, calcula quem está em quadra, a fila, as vitórias seguidas, os
reis (na ordem em que viraram) e os eliminados. Registrar os resultados é da
US6; aqui só se lê. Sem resultados, é a situação inicial.

Regras: os dois primeiros da fila jogam; o perdedor sai (eliminado); o vencedor
fica e enfrenta o próximo; com 2 vitórias seguidas vira rei, sai da quadra e
entram os 2 próximos. Se a fila esvaziar com um time sozinho na quadra, ou com
a quadra vazia, a fase de fila termina (`fim_da_fila`). Quem enfrenta quem no
mata-mata (RN-04, US11) é derivado aqui também: o desafiante (o time que
ficou na quadra, ou o último rei se a quadra esvaziou) enfrenta os reis em ordem
de coroação; ganhou ficou, perdeu saiu; quem sobra no fim é o campeão.
"""

from collections import defaultdict, deque
from collections.abc import Sequence
from typing import NamedTuple


class TimeEntrada(NamedTuple):
    id: str
    fila: int  # posição original no sorteio (1 = primeiro)
    incompleto: bool


class ResultadoEntrada(NamedTuple):
    time_a_id: str
    time_b_id: str
    vencedor_id: str
    fase: str = "fila"  # "fila" | "mata_mata"


class Ajuste(NamedTuple):
    """Mudança da fila no meio da rodada (CV8.DS7.TS3). `apos` é quantas partidas
    encerradas (fila e mata-mata, juntas) já existiam quando valeu: `derivar`
    aplica o ajuste logo depois dessa partida, para que os resultados já
    gravados continuem batendo com a quadra de então.

    - `remover`: o time ficou sem nenhum jogador e deixa de existir;
    - `pular`: o time vai para o fim da fila (ou do rol de reis/rivais).
    """

    apos: int
    tipo: str  # "remover" | "pular"
    time_id: str


class Situacao(NamedTuple):
    fase: str  # "fila" | "fim_da_fila"
    em_quadra: tuple[str, ...]  # ids, 0 a 2
    fila: tuple[str, ...]  # ids na ordem de entrada
    reis: tuple[str, ...]  # ids na ordem em que viraram rei
    eliminados: tuple[str, ...]  # ids de times, na ordem em que perderam
    vitorias: dict[str, int]  # vitórias seguidas de cada time
    ultimo_vencedor: str | None
    desafiante: str | None = None  # quem abre o mata-mata (só no fim da fila)
    rivais: tuple[str, ...] = ()  # reis ainda por enfrentar, na ordem
    campeao: str | None = None


def derivar(
    times: list[TimeEntrada],
    resultados: list[ResultadoEntrada],
    mata_mata_iniciado: bool = False,
    ajustes: Sequence[Ajuste] = (),
) -> Situacao:
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

    fila_res = [r for r in resultados if r.fase == "fila"]
    mata_res = [r for r in resultados if r.fase == "mata_mata"]
    total = len(fila_res) + len(mata_res)
    # Ajustes por momento; os de depois da última partida (um "desfazer" tirou
    # a partida que eles seguiam) valem no fim da sequência.
    por_momento: dict[int, list[Ajuste]] = defaultdict(list)
    for a in ajustes:
        por_momento[min(a.apos, total)].append(a)

    def ajustar_fila(k: int) -> None:
        nonlocal ultimo
        for a in por_momento.get(k, ()):
            if a.tipo == "remover":
                for lugar in (quadra, fila, reis, eliminados):
                    if a.time_id in lugar:
                        lugar.remove(a.time_id)
                if ultimo == a.time_id:
                    ultimo = None
            elif a.tipo == "pular":
                for lugar in (fila, reis):
                    if a.time_id in lugar:
                        lugar.remove(a.time_id)
                        lugar.append(a.time_id)
                if a.time_id in quadra:
                    quadra.remove(a.time_id)
                    fila.append(a.time_id)
        encher()

    encher()
    ajustar_fila(0)
    for i, r in enumerate(fila_res, start=1):
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
        ajustar_fila(i)

    fase = "fila" if len(quadra) == 2 else "fim_da_fila"
    desafiante: str | None = None
    rivais: tuple[str, ...] = ()
    campeao: str | None = None
    saidos: set[str] = set()  # removidos durante o mata-mata
    if fase == "fila":
        if mata_res or mata_mata_iniciado:
            raise ValueError("mata-mata antes do fim da fila")
    else:
        # Quadra vazia: o último vencedor acabou de virar rei e é o desafiante
        # (se ele deixou de existir, o último rei que sobrou).
        desafiante = quadra[0] if quadra else (ultimo or (reis[-1] if reis else None))
        restantes = deque(t for t in reis if t != desafiante)
        if mata_res and not mata_mata_iniciado:
            raise ValueError("resultado do mata-mata sem o mata-mata iniciado")
        if mata_mata_iniciado:
            atual = desafiante
            for j, r in enumerate(mata_res, start=1):
                if (
                    atual is None
                    or not restantes
                    or sorted((r.time_a_id, r.time_b_id))
                    != sorted((atual, restantes[0]))
                ):
                    raise ValueError(
                        "resultado de uma partida fora da ordem do mata-mata"
                    )
                if r.vencedor_id not in (r.time_a_id, r.time_b_id):
                    raise ValueError("vencedor não disputou a partida")
                restantes.popleft()
                atual = r.vencedor_id
                atual = _ajustar_mata(
                    por_momento.get(len(fila_res) + j, ()), atual, restantes, saidos
                )
            if atual is None and restantes:  # o campeão de então deixou de existir
                atual = restantes.popleft()
            if atual is None:
                fase, quadra = "fim_da_fila", []
            elif restantes:
                fase = "mata_mata"
                quadra = [atual, restantes[0]]
            else:
                fase = "campeao"
                campeao = atual
                quadra = []
            desafiante = atual
        rivais = tuple(restantes)
    return Situacao(
        fase=fase,
        em_quadra=tuple(quadra),
        fila=tuple(fila),
        reis=tuple(t for t in reis if t not in saidos),
        eliminados=tuple(t for t in eliminados if t not in saidos),
        vitorias=vitorias,
        ultimo_vencedor=ultimo,
        desafiante=desafiante,
        rivais=rivais,
        campeao=campeao,
    )


def _ajustar_mata(
    ajustes: Sequence[Ajuste], atual: str | None, restantes: deque, saidos: set[str]
):
    """Aplica ajustes durante o mata-mata e devolve quem está no lugar do
    campeão de então: se ele deixou de existir, o próximo rival ocupa o lugar."""
    for a in ajustes:
        if a.tipo == "remover":
            saidos.add(a.time_id)
            if a.time_id == atual:
                atual = restantes.popleft() if restantes else None
            elif a.time_id in restantes:
                restantes.remove(a.time_id)
        elif a.tipo == "pular" and a.time_id in restantes:
            restantes.remove(a.time_id)
            restantes.append(a.time_id)
    return atual


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


def time_ruim(generos: list[str], tamanho: int) -> bool:
    """Composição que a regra de gênero evita: dupla H+H (RN-01) ou, no trio,
    três do mesmo sexo (RN-16)."""
    if len(generos) < tamanho:
        return False
    if tamanho == 2:
        return all(g == "H" for g in generos)
    return len(set(generos)) == 1


def _completavel(atuais: list[str], base: list[Candidato], tamanho: int) -> bool:
    """Se o time (com `atuais` já escolhidos) ainda pode ser completado sem
    cair numa composição ruim, escolhendo entre `base`."""
    faltam = tamanho - len(atuais)
    if faltam <= 0:
        return not time_ruim(atuais, tamanho)
    if faltam == 1:
        return any(not time_ruim([*atuais, c.genero], tamanho) for c in base)
    return True


def lista_de_escalacao(
    *,
    genero_do_incompleto: str,
    origem: str,
    eliminados: list[Candidato],
    livres: list[Candidato],
    atuais: list[str] | None = None,
    tamanho: int = 2,
) -> dict:
    """Quem pode ser parceiro do time incompleto (RN-05, RN-06, RN-07, RN-16).

    `eliminados`: jogadores de times que perderam e hoje não jogam por nenhum
    time ativo. `livres`: jogadores da rodada que ainda não disputaram partida
    e não estão em time ativo (vazio na prática: o incompleto é o último da fila,
    então todos à frente dele já jogaram; existe para atrasados e substituições).

    - ímpar: primeiro "ainda não jogaram"; se vazio, a lista de escalação;
    - atrasado: sempre a lista de escalação.
    - gênero: dupla, se o incompleto é homem, só mulheres, a menos que não haja
      nenhuma elegível; trio, nunca fecha com os três do mesmo sexo havendo
      alternativa. Dentro disso, por chegada.

    `atuais` são os gêneros já no time (padrão: só o `genero_do_incompleto`).
    """
    atuais = atuais or [genero_do_incompleto]
    if origem == "impar" and livres:
        rotulo, base = "Ainda não jogaram", livres
    else:
        rotulo, base = "Lista de escalação (eliminados)", eliminados
    base = _ordenar(base)
    evita = [
        c
        for c in base
        if _completavel([*atuais, c.genero], [o for o in base if o.id != c.id], tamanho)
    ]
    permitidos = evita or base
    aviso_hh = bool(base) and not evita and time_ruim_possivel(atuais, base, tamanho)
    return {
        "grupos": [{"rotulo": rotulo, "jogadores": permitidos}] if permitidos else [],
        "aviso_hh": aviso_hh,
        "recusados_hh": [c for c in base if c not in permitidos],
    }


def time_ruim_possivel(atuais: list[str], base: list[Candidato], tamanho: int) -> bool:
    """Não há como evitar a composição ruim: o time fechará assim por falta de
    alternativa (o aviso da tela)."""
    if tamanho == 2:
        return atuais[0] == "H"
    return len(set(atuais)) == 1 and all(c.genero == atuais[0] for c in base)


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
