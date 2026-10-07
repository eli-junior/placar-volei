"""Sorteio da primeira rodada (CV8.DS2.US3). Módulo puro: sem banco, sem relógio.

Regras (ver `docs/project/roadmap/cv8-gerenciador-de-times/regras-de-negocio.md`):

- RN-11: no mínimo 4 jogadores.
- RN-05: número ímpar → o **último a chegar** fica sozinho num time incompleto,
  por último na fila.
- RN-01: o número de duplas H+H é o mínimo possível, `max(0, (H − M) / 2)`
  entre os que formam dupla. O gênero prevalece sobre o equilíbrio.
- RN-14: duplas equilibradas pela nota (somas de nota o mais parecidas
  possível), sem aleatoriedade na combinação-base.
- RN-13: a fila ordena os times pela menor ordem de chegada entre seus
  jogadores; o time incompleto vai ao fim.

O resultado é determinístico. "Resortear" percorre outras combinações
igualmente equilibradas (amplitude até `TOLERANCIA` pontos pior que a melhor).
"""

import random
from functools import lru_cache
from typing import NamedTuple

MINIMO_JOGADORES = 4
# Resortear aceita combinações cuja amplitude (maior soma − menor soma) seja,
# no máximo, esta quantidade de pontos pior que a da melhor combinação.
TOLERANCIA = 3
_PARTIDAS_ALEATORIAS = 16
_PASSOS_MAXIMOS = 8
_MAXIMO_CANDIDATAS = 60


# NamedTuple em vez de dataclass: imutável e hasheável do mesmo jeito, e o acesso
# aos campos é por tupla. (Em laços longos, instâncias de dataclass derrubaram o
# interpretador deste ambiente de desenvolvimento de forma intermitente.)
class Participante(NamedTuple):
    id: str
    genero: str  # "H" ou "M"
    nota: int
    ordem: int  # ordem de chegada (1 = primeiro)


class Time(NamedTuple):
    jogadores: tuple[Participante, ...]
    fila: int  # 1 = joga primeiro
    incompleto: bool

    @property
    def soma(self) -> int:
        return sum(p.nota for p in self.jogadores)


class Sorteio(NamedTuple):
    times: tuple[Time, ...]  # já na ordem da fila
    amplitude: int  # maior soma − menor soma entre os times completos
    duplas_hh: int
    tentativa: int
    distintas: int  # quantas combinações equivalentes existem (≥ 1)


class JogadoresInsuficientes(ValueError):
    def __init__(self, presentes: int) -> None:
        self.presentes = presentes
        self.faltam = MINIMO_JOGADORES - presentes
        super().__init__(f"faltam {self.faltam} para o mínimo de {MINIMO_JOGADORES}")


def _hh(dupla) -> int:
    return int(dupla[0].genero == "H" and dupla[1].genero == "H")


def _quadrado(dupla) -> int:
    return (dupla[0].nota + dupla[1].nota) ** 2


def _objetivo(duplas) -> int:
    """Soma dos quadrados das somas: menor = duplas mais parecidas entre si."""
    return sum(_quadrado(d) for d in duplas)


def _amplitude(duplas) -> int:
    somas = [d[0].nota + d[1].nota for d in duplas]
    return max(somas) - min(somas)


def _chave(duplas) -> tuple:
    return tuple(sorted(tuple(sorted(p.id for p in d)) for d in duplas))


def _serpentina(grupo: list[Participante]) -> list[list[Participante]]:
    """Mais forte com mais fraco, o segundo com o penúltimo..."""
    ordenado = sorted(grupo, key=lambda p: (-p.nota, p.ordem))
    n = len(ordenado)
    return [[ordenado[i], ordenado[n - 1 - i]] for i in range(n // 2)]


def _inicial(pares: list[Participante]) -> list[list[Participante]]:
    """Pareamento já com o número mínimo de duplas H+H (RN-01)."""
    homens = sorted(
        (p for p in pares if p.genero == "H"), key=lambda p: (-p.nota, p.ordem)
    )
    mulheres = sorted(
        (p for p in pares if p.genero == "M"), key=lambda p: (-p.nota, p.ordem)
    )
    duplas: list[list[Participante]] = []
    if len(homens) >= len(mulheres):
        k = (len(homens) - len(mulheres)) // 2
        extra = homens[len(homens) - 2 * k :] if k else []  # os mais fracos entre si
        mistos_h = homens[: len(homens) - 2 * k]
        duplas += _serpentina(extra) if extra else []
        misto_m = mulheres
    else:
        j = (len(mulheres) - len(homens)) // 2
        extra = mulheres[len(mulheres) - 2 * j :] if j else []
        misto_m = mulheres[: len(mulheres) - 2 * j]
        duplas += _serpentina(extra) if extra else []
        mistos_h = homens
    # Forte com fraca: o homem mais forte com a mulher mais fraca, e assim por diante.
    for h, m in zip(mistos_h, reversed(misto_m), strict=True):
        duplas.append([h, m])
    return duplas


def _trocas(duplas) -> list[tuple[int, int, int, int]]:
    """Todas as trocas de um jogador entre duas duplas distintas."""
    trocas = []
    n = len(duplas)
    for a in range(n):
        for b in range(a + 1, n):
            for i in (0, 1):
                for j in (0, 1):
                    trocas.append((a, i, b, j))
    return trocas


def _aplicar(duplas, troca):
    a, i, b, j = troca
    novo = [list(d) for d in duplas]
    novo[a][i], novo[b][j] = novo[b][j], novo[a][i]
    return novo


def _delta(duplas, troca) -> int | None:
    """Variação do objetivo, ou None se a troca mudaria o nº de duplas H+H."""
    a, i, b, j = troca
    da, db = duplas[a], duplas[b]
    na = [da[0], da[1]]
    nb = [db[0], db[1]]
    na[i], nb[j] = db[j], da[i]
    if _hh(na) + _hh(nb) != _hh(da) + _hh(db):
        return None
    return _quadrado(na) + _quadrado(nb) - _quadrado(da) - _quadrado(db)


def _descer(duplas) -> list[list[Participante]]:
    """Troca a melhor possível até não haver troca que melhore (determinístico)."""
    atual = [list(d) for d in duplas]
    while True:
        melhor, melhor_delta = None, 0
        for troca in _trocas(atual):
            d = _delta(atual, troca)
            if d is not None and d < melhor_delta:
                melhor, melhor_delta = troca, d
        if melhor is None:
            return atual
        atual = _aplicar(atual, melhor)


def _perturbar(duplas, rng: random.Random, passos: int):
    atual = [list(d) for d in duplas]
    for _passo in range(passos):
        possiveis = []
        for troca in _trocas(atual):
            if _delta(atual, troca) is not None:
                possiveis.append(troca)
        if not possiveis:
            break
        atual = _aplicar(atual, rng.choice(possiveis))
    return atual


@lru_cache(maxsize=64)
def _candidatas(pares: tuple[Participante, ...]) -> list[list[list[Participante]]]:
    """Combinações equivalentes, da melhor para a pior, sem repetição."""
    base = _descer(_inicial(pares))
    achadas = {_chave(base): base}
    rng = random.Random(len(pares) * 100003 + sum(p.nota for p in pares))
    for _ in range(_PARTIDAS_ALEATORIAS):
        passos = rng.randint(1, min(len(pares), _PASSOS_MAXIMOS))
        candidata = _descer(_perturbar(base, rng, passos))
        achadas.setdefault(_chave(candidata), candidata)
    melhor_amp = min(_amplitude(c) for c in achadas.values())
    # Vizinhas imediatas de cada ótimo local também são equivalentes.
    for c in list(achadas.values()):
        for troca in _trocas(c):
            if _delta(c, troca) is None:
                continue
            vizinha = _aplicar(c, troca)
            if _amplitude(vizinha) <= melhor_amp + TOLERANCIA:
                achadas.setdefault(_chave(vizinha), vizinha)
    aceitas = [c for c in achadas.values() if _amplitude(c) <= melhor_amp + TOLERANCIA]
    aceitas.sort(key=lambda c: (_objetivo(c), _chave(c)))
    return aceitas[:_MAXIMO_CANDIDATAS]


def sortear(participantes: list[Participante], tentativa: int = 0) -> Sorteio:
    """Monta a proposta. `tentativa` 0 é a melhor combinação; as seguintes
    percorrem as equivalentes (e voltam ao início ao esgotá-las)."""
    if len(participantes) < MINIMO_JOGADORES:
        raise JogadoresInsuficientes(len(participantes))
    if len({p.id for p in participantes}) != len(participantes):
        raise ValueError("jogadores repetidos")

    ordenados = sorted(participantes, key=lambda p: p.ordem)
    impar = ordenados[-1] if len(ordenados) % 2 else None
    pares = [p for p in ordenados if p is not impar]

    candidatas = _candidatas(tuple(pares))
    escolhida = candidatas[tentativa % len(candidatas)]

    completos = sorted(escolhida, key=lambda d: min(p.ordem for p in d))
    times = [
        Time(tuple(sorted(d, key=lambda p: p.ordem)), fila=i, incompleto=False)
        for i, d in enumerate(completos, start=1)
    ]
    if impar is not None:
        times.append(Time((impar,), fila=len(times) + 1, incompleto=True))
    return Sorteio(
        times=tuple(times),
        amplitude=_amplitude(escolhida),
        duplas_hh=sum(_hh(d) for d in escolhida),
        tentativa=tentativa,
        distintas=len(candidatas),
    )
