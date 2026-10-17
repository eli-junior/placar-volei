"""Resenha do Joguinho (CV8.DS9.US25): estatísticas e prêmios da sessão.

Só lê o `gerenciador.db`: os eventos ponto a ponto das quadras expiram com a
sala, então nada aqui depende deles. O placar é do time, não da pessoa: todo
número de pontos é "da dupla (ou trio) em que o jogador estava".

Quem jogou cada partida vem de `ajustes_nota` (gravado no encerramento, como em
`reequilibrio.ultima_partida`), porque a substituição e a retirada reescrevem
`time_jogadores` depois. Sem esse registro (notas resetadas), vale o time atual.

`calcular` é pura e testável sem banco; `carregar` monta a entrada a partir do
banco. A sessão é a aberta ou, sem ela, a última encerrada.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Partida:
    numero: int  # 1..N, em ordem cronológica na sessão
    rodada: int
    alvo: int
    placar_a: int
    placar_b: int
    lado_a: tuple[str, ...]
    lado_b: tuple[str, ...]
    duracao_s: int | None = None

    @property
    def vencedores(self) -> tuple[str, ...]:
        return self.lado_a if self.placar_a > self.placar_b else self.lado_b

    @property
    def perdedores(self) -> tuple[str, ...]:
        return self.lado_b if self.placar_a > self.placar_b else self.lado_a

    @property
    def margem(self) -> int:
        return abs(self.placar_a - self.placar_b)

    def json(self) -> dict:
        return {
            "rodada": self.rodada,
            "placar_a": self.placar_a,
            "placar_b": self.placar_b,
            "lado_a": list(self.lado_a),
            "lado_b": list(self.lado_b),
        }


@dataclass(frozen=True)
class Jogador:
    id: str
    nome: str
    genero: str = "H"
    tem_foto: bool = False


@dataclass
class Linha:
    """Números de um jogador no dia."""

    jogos: int = 0
    vitorias: int = 0
    derrotas: int = 0
    pro: int = 0
    contra: int = 0
    delta_nota: int = 0
    seq_v: int = 0
    seq_d: int = 0
    _atual_v: int = 0
    _atual_d: int = 0
    contra_quem: dict[str, list[int]] = field(default_factory=dict)  # [ganhou, perdeu]

    @property
    def saldo(self) -> int:
        return self.pro - self.contra

    @property
    def aproveitamento(self) -> float:
        return self.vitorias / self.jogos if self.jogos else 0.0

    @property
    def media_contra(self) -> float:
        return self.contra / self.jogos if self.jogos else 0.0


def _g(jogador: Jogador, masculino: str, feminino: str) -> str:
    return feminino if jogador.genero == "M" else masculino


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def _decimal(x: float) -> str:
    """Uma casa, com vírgula: 6,5."""
    return f"{x:.1f}".replace(".", ",")


def _empatados(itens, chave):
    """Todos os itens com o melhor valor de `chave` (maior é melhor)."""
    if not itens:
        return []
    melhor = max(chave(i) for i in itens)
    return [i for i in itens if chave(i) == melhor]


def _linhas(partidas: list[Partida], deltas: dict[str, int]) -> dict[str, Linha]:
    linhas: dict[str, Linha] = {}
    for p in partidas:
        a_venceu = p.placar_a > p.placar_b
        for lado, rival, pro, contra, venceu in (
            (p.lado_a, p.lado_b, p.placar_a, p.placar_b, a_venceu),
            (p.lado_b, p.lado_a, p.placar_b, p.placar_a, not a_venceu),
        ):
            for jid in lado:
                lin = linhas.setdefault(jid, Linha())
                lin.jogos += 1
                lin.pro += pro
                lin.contra += contra
                if venceu:
                    lin.vitorias += 1
                    lin._atual_v += 1
                    lin._atual_d = 0
                else:
                    lin.derrotas += 1
                    lin._atual_d += 1
                    lin._atual_v = 0
                lin.seq_v = max(lin.seq_v, lin._atual_v)
                lin.seq_d = max(lin.seq_d, lin._atual_d)
                for outro in rival:
                    placar = lin.contra_quem.setdefault(outro, [0, 0])
                    placar[0 if venceu else 1] += 1
    for jid, d in deltas.items():
        linhas.setdefault(jid, Linha()).delta_nota = d
    return linhas


def _premio(id_, emoji, titulo, texto, tom, jogadores, partida=None) -> dict:
    premio = {
        "id": id_,
        "emoji": emoji,
        "titulo": titulo,
        "texto": texto,
        "tom": tom,
        "jogadores": list(jogadores),
    }
    if partida is not None:
        premio["partida"] = partida.json()
    return premio


def _titulo_unico(ids, jogadores, masculino, feminino, coletivo) -> str:
    if len(ids) == 1:
        return _g(jogadores[ids[0]], masculino, feminino)
    return coletivo


def _premios(
    partidas: list[Partida],
    linhas: dict[str, Linha],
    jogadores: dict[str, Jogador],
    primeiro_a_chegar: str | None,
) -> list[dict]:
    premios: list[dict] = []
    jogaram = [jid for jid, lin in linhas.items() if lin.jogos and jid in jogadores]

    def nomes(ids) -> list[str]:
        return sorted(ids, key=lambda j: jogadores[j].nome)

    def lin(j):
        return linhas[j]

    # 👑 Rei do dia: mais vitórias; aproveitamento e saldo desempatam.
    com_vitoria = [j for j in jogaram if lin(j).vitorias]
    reis = _empatados(
        com_vitoria, lambda j: (lin(j).vitorias, lin(j).aproveitamento, lin(j).saldo)
    )
    if reis:
        r = lin(reis[0])
        premios.append(
            _premio(
                "rei",
                "👑",
                _titulo_unico(
                    reis, jogadores, "Rei do dia", "Rainha do dia", "Realeza do dia"
                ),
                f"{_plural(r.vitorias, 'vitória', 'vitórias')} em "
                f"{_plural(r.jogos, 'jogo', 'jogos')}",
                "positivo",
                nomes(reis),
            )
        )

    # 🔥 Imparável: maior sequência de vitórias (3 ou mais).
    imparaveis = _empatados(
        [j for j in jogaram if lin(j).seq_v >= 3], lambda j: lin(j).seq_v
    )
    if imparaveis:
        premios.append(
            _premio(
                "imparavel",
                "🔥",
                _titulo_unico(
                    imparaveis, jogadores, "Imparável", "Imparável", "Imparáveis"
                ),
                f"{lin(imparaveis[0]).seq_v} vitórias seguidas",
                "positivo",
                nomes(imparaveis),
            )
        )

    # 🤝 Dupla (ou trio) de ouro: quem mais venceu junto (2 ou mais vitórias).
    juntos: dict[frozenset, list[int]] = {}
    for p in partidas:
        for lado, venceu in ((p.vencedores, True), (p.perdedores, False)):
            if len(lado) >= 2:
                placar = juntos.setdefault(frozenset(lado), [0, 0])
                placar[0 if venceu else 1] += 1
    candidatas = [g for g, (v, _) in juntos.items() if v >= 2]
    ouro = _empatados(candidatas, lambda g: (juntos[g][0], -juntos[g][1]))
    if len(ouro) == 1:
        grupo = ouro[0]
        v, d = juntos[grupo]
        premios.append(
            _premio(
                "dupla_de_ouro",
                "🤝",
                "Dupla de ouro" if len(grupo) == 2 else "Trio de ouro",
                f"{_plural(v, 'vitória', 'vitórias')} juntos"
                + (f" e {_plural(d, 'derrota', 'derrotas')}" if d else ", sem perder"),
                "positivo",
                nomes(grupo),
            )
        )

    # 🚜 Rolo compressor: maior saldo de pontos (positivo).
    rolos = _empatados([j for j in jogaram if lin(j).saldo > 0], lambda j: lin(j).saldo)
    if rolos:
        premios.append(
            _premio(
                "rolo",
                "🚜",
                "Rolo compressor",
                f"+{lin(rolos[0]).saldo} de saldo de pontos",
                "positivo",
                nomes(rolos),
            )
        )

    # 🧱 Muralha e 🕳️ Peneira: média de pontos sofridos, com jogos suficientes.
    maximo = max((lin(j).jogos for j in jogaram), default=0)
    minimo_jogos = max(2, math.ceil(maximo / 2))
    regulares = [j for j in jogaram if lin(j).jogos >= minimo_jogos]
    if len(regulares) >= 3:
        muralhas = _empatados(regulares, lambda j: -lin(j).media_contra)
        peneiras = _empatados(regulares, lambda j: lin(j).media_contra)
        if set(muralhas) != set(peneiras):
            premios.append(
                _premio(
                    "muralha",
                    "🧱",
                    "Muralha",
                    f"só {_decimal(lin(muralhas[0]).media_contra)} pontos sofridos por jogo",
                    "positivo",
                    nomes(muralhas),
                )
            )
            premios.append(
                _premio(
                    "peneira",
                    "🕳️",
                    "Peneira",
                    f"{_decimal(lin(peneiras[0]).media_contra)} pontos sofridos por jogo",
                    "negativo",
                    nomes(peneiras),
                )
            )

    # 🚀 Foguete e 🚨 Circuit breaker: maior alta e maior queda de nota.
    com_nota = [j for j in jogaram if lin(j).delta_nota]
    foguetes = _empatados(
        [j for j in com_nota if lin(j).delta_nota > 0], lambda j: lin(j).delta_nota
    )
    if foguetes:
        premios.append(
            _premio(
                "foguete",
                "🚀",
                "Foguete",
                f"nota subiu {lin(foguetes[0]).delta_nota} pontos no dia",
                "positivo",
                nomes(foguetes),
            )
        )
    quedas = _empatados(
        [j for j in com_nota if lin(j).delta_nota < 0], lambda j: -lin(j).delta_nota
    )
    if quedas:
        premios.append(
            _premio(
                "circuit_breaker",
                "🚨",
                "Circuit breaker",
                f"nota despencou {-lin(quedas[0]).delta_nota} pontos: pregão suspenso",
                "negativo",
                nomes(quedas),
            )
        )

    # 🔪 Carrasco e 🍩 Pneu do dia: a maior lavada (metade do alvo ou mais).
    lavadas = [p for p in partidas if p.margem * 2 >= p.alvo]
    if lavadas:
        lavada = max(lavadas, key=lambda p: (p.margem, -p.numero))
        placar = f"{max(lavada.placar_a, lavada.placar_b)} x {min(lavada.placar_a, lavada.placar_b)}"
        premios.append(
            _premio(
                "carrasco",
                "🔪",
                "Carrasco",
                f"aplicou o maior pneu do dia: {placar}",
                "positivo",
                nomes(lavada.vencedores),
                lavada,
            )
        )
        premios.append(
            _premio(
                "pneu",
                "🍩",
                "Pneu do dia",
                f"tomou {placar} e saiu de rosquinha",
                "negativo",
                nomes(lavada.perdedores),
                lavada,
            )
        )

    # 😰 Jogo de infarto: o mais apertado; passar do alvo pela vantagem pesa.
    if partidas:
        infarto = min(
            partidas, key=lambda p: (p.margem, -(p.placar_a + p.placar_b), p.numero)
        )
        prorrogou = max(infarto.placar_a, infarto.placar_b) > infarto.alvo
        if infarto.margem <= 2:
            premios.append(
                _premio(
                    "infarto",
                    "😰",
                    "Jogo de infarto",
                    "foi pra prorrogação e ninguém respirou"
                    if prorrogou
                    else "decidido no detalhe, com a torcida roendo as unhas",
                    "neutro",
                    nomes([*infarto.lado_a, *infarto.lado_b]),
                    infarto,
                )
            )

    # ⏱️ Maratona: a partida mais longa (só com 2 ou mais partidas).
    cronometradas = [p for p in partidas if p.duracao_s]
    if len(cronometradas) >= 2:
        longa = max(cronometradas, key=lambda p: (p.duracao_s, -p.numero))
        minutos = max(1, round(longa.duracao_s / 60))
        premios.append(
            _premio(
                "maratona",
                "⏱️",
                "Maratona",
                f"{minutos} min de jogo: deu tempo de pedir uma água de coco",
                "neutro",
                nomes([*longa.lado_a, *longa.lado_b]),
                longa,
            )
        )

    # 🥶 Pé-frio: mais derrotas (2 ou mais); o pior aproveitamento desempata.
    frios = _empatados(
        [j for j in jogaram if lin(j).derrotas >= 2],
        lambda j: (lin(j).derrotas, -lin(j).aproveitamento),
    )
    if frios:
        f = lin(frios[0])
        premios.append(
            _premio(
                "pe_frio",
                "🥶",
                "Pé-frio",
                f"{_plural(f.derrotas, 'derrota', 'derrotas')} em "
                f"{_plural(f.jogos, 'jogo', 'jogos')}",
                "negativo",
                nomes(frios),
            )
        )

    # 📉 Ladeira abaixo: maior sequência de derrotas (3 ou mais).
    ladeira = _empatados(
        [j for j in jogaram if lin(j).seq_d >= 3], lambda j: lin(j).seq_d
    )
    if ladeira:
        premios.append(
            _premio(
                "ladeira",
                "📉",
                "Ladeira abaixo",
                f"{lin(ladeira[0]).seq_d} derrotas seguidas",
                "negativo",
                nomes(ladeira),
            )
        )

    # 🛒 Freguês: perdeu 2 ou mais vezes para a mesma pessoa, sem vencê-la.
    fregueses = [
        (j, outro, perdeu)
        for j in jogaram
        for outro, (ganhou, perdeu) in lin(j).contra_quem.items()
        if perdeu >= 2 and ganhou == 0 and outro in jogadores
    ]
    if fregueses:
        j, dono, perdeu = min(
            fregueses, key=lambda f: (-f[2], jogadores[f[0]].nome, jogadores[f[1]].nome)
        )
        premios.append(
            _premio(
                "fregues",
                "🛒",
                _g(jogadores[j], "Freguês", "Freguesa"),
                f"perdeu {perdeu}x para {jogadores[dono].nome} e não ganhou nenhuma",
                "negativo",
                [j],
            )
        )

    # 🏖️ Turista: jogou bem menos que o máximo (2 ou mais a menos).
    if maximo >= 3:
        turistas = _empatados(
            [j for j in jogaram if maximo - lin(j).jogos >= 2], lambda j: -lin(j).jogos
        )
        if turistas:
            premios.append(
                _premio(
                    "turista",
                    "🏖️",
                    "Turista",
                    f"só {_plural(lin(turistas[0]).jogos, 'jogo', 'jogos')}; o resto foi na sombra",
                    "neutro",
                    nomes(turistas),
                )
            )

    # 🐓 Madrugador: primeiro a chegar.
    if primeiro_a_chegar in jogadores:
        premios.append(
            _premio(
                "madrugador",
                "🐓",
                _g(jogadores[primeiro_a_chegar], "Madrugador", "Madrugadora"),
                "primeiro a chegar na areia",
                "positivo",
                [primeiro_a_chegar],
            )
        )
    return premios


# Prioridade do título da galeria: o primeiro prêmio da lista vira o título
# principal do jogador; os outros viram selos.
PRIORIDADE = (
    "rei",
    "campeao",
    "imparavel",
    "dupla_de_ouro",
    "carrasco",
    "rolo",
    "muralha",
    "foguete",
    "pneu",
    "circuit_breaker",
    "fregues",
    "pe_frio",
    "ladeira",
    "peneira",
    "turista",
    "madrugador",
)

TITULOS_POR_PREMIO = {
    "rei": ("Rei do dia", "Rainha do dia"),
    "campeao": ("Campeão da rodada", "Campeã da rodada"),
    "imparavel": ("Imparável", "Imparável"),
    "dupla_de_ouro": ("Metade da dupla de ouro", "Metade da dupla de ouro"),
    "carrasco": ("Carrasco", "Carrasca"),
    "rolo": ("Rolo compressor", "Rolo compressor"),
    "muralha": ("Muralha", "Muralha"),
    "foguete": ("Foguete", "Foguete"),
    "pneu": ("Tomou pneu", "Tomou pneu"),
    "circuit_breaker": ("Circuit breaker", "Circuit breaker"),
    "fregues": ("Freguês", "Freguesa"),
    "pe_frio": ("Pé-frio", "Pé-frio"),
    "ladeira": ("Ladeira abaixo", "Ladeira abaixo"),
    "peneira": ("Peneira", "Peneira"),
    "turista": ("Turista", "Turista"),
    "madrugador": ("Madrugador", "Madrugadora"),
}


def _titulo_padrao(linha: Linha | None, jogador: Jogador) -> tuple[str, str, str]:
    """(emoji, título, tom) para quem não levou prêmio nenhum."""
    if linha is None or linha.jogos == 0:
        return "🍻", "Só veio pela resenha", "neutro"
    if linha.vitorias == linha.jogos:
        return "💎", _g(jogador, "Invicto", "Invicta"), "positivo"
    if linha.vitorias == 0:
        return "🎁", _g(jogador, "Doador de pontos", "Doadora de pontos"), "negativo"
    if linha.aproveitamento >= 0.6:
        return "😎", "Bom de areia", "positivo"
    if linha.aproveitamento >= 0.4:
        return "⚖️", "Meio a meio, sem compromisso", "neutro"
    return "🏝️", "Veio pelo bronzeado", "negativo"


def _galeria(premios, campeoes, linhas, jogadores, presentes) -> list[dict]:
    por_jogador: dict[str, list[tuple[str, str, str]]] = {}
    # Prêmios de partida (infarto, maratona) não viram título de ninguém.
    fontes = [
        (p["id"], p["emoji"], p["tom"], p["jogadores"])
        for p in premios
        if p["id"] in TITULOS_POR_PREMIO
    ]
    fontes += [("campeao", "🏆", "positivo", c["jogadores"]) for c in campeoes]
    for id_, emoji, tom, ids in fontes:
        for jid in ids:
            lista = por_jogador.setdefault(jid, [])
            if all(i != id_ for i, _, _ in lista):
                lista.append((id_, emoji, tom))
    ids = list(dict.fromkeys([*presentes, *(j for j in linhas if linhas[j].jogos)]))
    galeria = []
    for jid in ids:
        if jid not in jogadores:
            continue
        jogador, linha = jogadores[jid], linhas.get(jid)
        conquistas = sorted(
            por_jogador.get(jid, []), key=lambda c: PRIORIDADE.index(c[0])
        )
        if conquistas:
            id_, emoji, tom = conquistas[0]
            titulo = _g(jogador, *TITULOS_POR_PREMIO[id_])
            selos = [c[1] for c in conquistas[1:]]
        else:
            emoji, titulo, tom = _titulo_padrao(linha, jogador)
            selos = []
        galeria.append(
            {
                "jogador": jid,
                "emoji": emoji,
                "titulo": titulo,
                "tom": tom,
                "selos": selos,
                "vitorias": linha.vitorias if linha else 0,
                "derrotas": linha.derrotas if linha else 0,
                "saldo": linha.saldo if linha else 0,
            }
        )
    galeria.sort(
        key=lambda g: (
            -g["vitorias"],
            g["derrotas"],
            -g["saldo"],
            jogadores[g["jogador"]].nome,
        )
    )
    return galeria


def calcular(
    partidas: list[Partida],
    jogadores: dict[str, Jogador],
    *,
    presentes: list[str] = (),
    deltas: dict[str, int] | None = None,
    campeoes: list[dict] = (),
    rodadas: int = 0,
) -> dict:
    """Prêmios, galeria e tabela da sessão. `presentes` vem na ordem de chegada;
    `campeoes` é `[{"rodada": n, "jogadores": [ids]}]`."""
    partidas = [p for p in partidas if p.placar_a != p.placar_b]
    linhas = _linhas(partidas, deltas or {})
    premios = _premios(partidas, linhas, jogadores, presentes[0] if presentes else None)
    tabela = [
        {
            "jogador": jid,
            "jogos": lin.jogos,
            "vitorias": lin.vitorias,
            "derrotas": lin.derrotas,
            "aproveitamento": round(lin.aproveitamento * 100),
            "pro": lin.pro,
            "contra": lin.contra,
            "saldo": lin.saldo,
            "delta_nota": lin.delta_nota,
        }
        for jid, lin in linhas.items()
        if lin.jogos and jid in jogadores
    ]
    tabela.sort(
        key=lambda t: (
            -t["vitorias"],
            -t["aproveitamento"],
            -t["saldo"],
            jogadores[t["jogador"]].nome,
        )
    )
    return {
        "resumo": {
            "partidas": len(partidas),
            "pontos": sum(p.placar_a + p.placar_b for p in partidas),
            "jogadores": len(set(presentes) | {t["jogador"] for t in tabela}),
            "rodadas": rodadas,
        },
        "premios": premios,
        "campeoes": list(campeoes),
        "galeria": _galeria(
            premios, list(campeoes), linhas, jogadores, list(presentes)
        ),
        "tabela": tabela,
    }


# --- leitura do banco -------------------------------------------------------


def _segundos(inicio: str | None, fim: str | None) -> int | None:
    if not inicio or not fim:
        return None
    try:
        return int(
            (
                datetime.fromisoformat(fim) - datetime.fromisoformat(inicio)
            ).total_seconds()
        )
    except ValueError:
        return None


def nomes_curtos(nomes: dict[str, str]) -> dict[str, str]:
    """Primeiro nome, que cabe no print; quem divide o primeiro nome com outro
    jogador do dia ganha a inicial do sobrenome, e, se ainda empatar, o nome todo."""
    primeiro = {j: n.split()[0] for j, n in nomes.items()}
    com_inicial = {
        j: f"{primeiro[j]} {n.split()[-1][0]}." if len(n.split()) > 1 else n
        for j, n in nomes.items()
    }
    curtos = {}
    for j, n in nomes.items():
        if list(primeiro.values()).count(primeiro[j]) == 1:
            curtos[j] = primeiro[j]
        elif list(com_inicial.values()).count(com_inicial[j]) == 1:
            curtos[j] = com_inicial[j]
        else:
            curtos[j] = n
    return curtos


def _sessao_da_resenha(conn):
    return conn.execute(
        "SELECT * FROM sessoes ORDER BY encerrada_em IS NOT NULL, aberta_em DESC LIMIT 1"
    ).fetchone()


def _ids_do_time(conn, time_id: str) -> list[str]:
    return [
        r["jogador_id"]
        for r in conn.execute(
            "SELECT jogador_id FROM time_jogadores WHERE time_id = ? ORDER BY ordem_chegada",
            (time_id,),
        )
    ]


def _lados(conn, p) -> tuple[tuple[str, ...], tuple[str, ...], dict[str, int]]:
    """Quem jogou em cada lado. `ajustes_nota` diz quem jogou; o time atual diz
    o lado, e o sinal do ajuste resolve quem já saiu do time (substituição)."""
    time_a, time_b = (
        _ids_do_time(conn, p["time_a_id"]),
        _ids_do_time(conn, p["time_b_id"]),
    )
    ajustes = {
        r["jogador_id"]: r["delta"]
        for r in conn.execute(
            "SELECT jogador_id, delta FROM ajustes_nota WHERE partida_id = ?",
            (p["id"],),
        )
    }
    if not ajustes:
        return tuple(time_a), tuple(time_b), {}
    a_venceu = p["placar_a"] > p["placar_b"]
    lado_a, lado_b = [], []
    for jid, delta in ajustes.items():
        if jid in time_a and jid not in time_b:
            lado_a.append(jid)
        elif jid in time_b and jid not in time_a:
            lado_b.append(jid)
        elif delta:  # ganhou nota: estava no lado vencedor
            (lado_a if (delta > 0) == a_venceu else lado_b).append(jid)
    return tuple(lado_a), tuple(lado_b), ajustes


def carregar(conn) -> dict:
    """A resenha da sessão aberta ou, sem ela, da última encerrada."""
    sessao = _sessao_da_resenha(conn)
    if sessao is None:
        return {"sessao": None}
    sid = sessao["id"]
    cadastro = {
        r["id"]: r
        for r in conn.execute(
            "SELECT j.id, j.nome, j.genero, EXISTS(SELECT 1 FROM jogador_fotos f "
            "WHERE f.jogador_id = j.id) AS tem_foto FROM jogadores j"
        )
    }
    presentes = [
        r["jogador_id"]
        for r in conn.execute(
            "SELECT jogador_id FROM presencas WHERE sessao_id = ? ORDER BY ordem",
            (sid,),
        )
    ]
    partidas, deltas = [], {}
    linhas = conn.execute(
        "SELECT p.*, r.numero AS rodada, r.alvo FROM partidas_rodada p "
        "JOIN rodadas r ON r.id = p.rodada_id "
        "WHERE r.sessao_id = ? AND p.estado = 'encerrada' AND p.placar_a IS NOT NULL AND p.wo = 0 "
        "ORDER BY r.numero, p.ordem",
        (sid,),
    ).fetchall()
    for numero, p in enumerate(linhas, start=1):
        lado_a, lado_b, ajustes = _lados(conn, p)
        for jid, d in ajustes.items():
            deltas[jid] = deltas.get(jid, 0) + d
        partidas.append(
            Partida(
                numero,
                p["rodada"],
                p["alvo"],
                p["placar_a"],
                p["placar_b"],
                lado_a,
                lado_b,
                _segundos(p["chamada_em"], p["encerrada_em"]),
            )
        )
    campeoes = [
        {"rodada": r["numero"], "jogadores": _ids_do_time(conn, r["campeao_time_id"])}
        for r in conn.execute(
            "SELECT numero, campeao_time_id FROM rodadas WHERE sessao_id = ? "
            "AND estado = 'encerrada' AND campeao_time_id IS NOT NULL ORDER BY numero",
            (sid,),
        )
    ]
    rodadas = conn.execute(
        "SELECT COUNT(*) FROM rodadas WHERE sessao_id = ? AND estado IN "
        "('em_andamento', 'encerrada', 'cancelada')",
        (sid,),
    ).fetchone()[0]
    do_dia = {*presentes, *(j for p in partidas for j in (*p.lado_a, *p.lado_b))}
    curtos = nomes_curtos({j: cadastro[j]["nome"] for j in do_dia if j in cadastro})
    jogadores = {
        jid: Jogador(
            jid, curto, cadastro[jid]["genero"], bool(cadastro[jid]["tem_foto"])
        )
        for jid, curto in curtos.items()
    }
    resultado = calcular(
        partidas,
        jogadores,
        presentes=presentes,
        deltas=deltas,
        campeoes=campeoes,
        rodadas=rodadas,
    )
    usados = {t["jogador"] for t in resultado["galeria"]}
    for premio in resultado["premios"]:
        usados.update(premio["jogadores"])
        if "partida" in premio:
            usados.update(premio["partida"]["lado_a"] + premio["partida"]["lado_b"])
    for c in campeoes:
        usados.update(c["jogadores"])
    return {
        "sessao": {
            "id": sid,
            "aberta_em": sessao["aberta_em"],
            "encerrada_em": sessao["encerrada_em"],
        },
        **resultado,
        "jogadores": {
            jid: {
                "id": j.id,
                "nome": j.nome,
                "nome_completo": cadastro[jid]["nome"],
                "genero": j.genero,
                "tem_foto": j.tem_foto,
            }
            for jid, j in jogadores.items()
            if jid in usados
        },
    }
