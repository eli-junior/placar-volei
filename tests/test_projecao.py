from app.eventos import Evento, TipoEvento
from app.projecao import projetar_estado


def make_evento(
    seq: int,
    tipo: str,
    payload: dict,
    partida_id: str = "partida-1",
    quadra_id: str = "quadra-1",
    autor_id: str = "autor-1",
) -> Evento:
    return Evento(
        id=f"evt-{seq}",
        quadra_id=quadra_id,
        partida_id=partida_id,
        seq=seq,
        tipo=tipo,
        payload=payload,
        autor_id=autor_id,
        criado_em="2026-09-13T12:00:00Z",
    )


def test_sequencia_simples():
    """Dez pontos alternados produzem o placar esperado (5x5)."""
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12, "vantagem": True}),
    ]
    for i in range(2, 12):
        equipe = "A" if i % 2 == 0 else "B"
        eventos.append(make_evento(i, TipoEvento.PONTO_MARCADO, {"equipe": equipe}))

    estado = projetar_estado(eventos)
    assert estado.pontos_a == 5
    assert estado.pontos_b == 5
    assert not estado.encerrada
    assert estado.vencedor is None


def test_desfazer_intercalado():
    """Pontos e desfazimentos misturados produzem o placar correto."""
    # A marca (seq 2), A marca (seq 3), B marca (seq 4),
    # anula seq 3 (A), B marca (seq 6)
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12}),
        make_evento(2, TipoEvento.PONTO_MARCADO, {"equipe": "A"}),
        make_evento(3, TipoEvento.PONTO_MARCADO, {"equipe": "A"}),
        make_evento(4, TipoEvento.PONTO_MARCADO, {"equipe": "B"}),
        make_evento(5, TipoEvento.PONTO_DESFEITO, {"ref_seq": 3}),
        make_evento(6, TipoEvento.PONTO_MARCADO, {"equipe": "B"}),
    ]
    estado = projetar_estado(eventos)
    assert estado.pontos_a == 1
    assert estado.pontos_b == 2
    assert 3 in estado.pontos_desfeitos


def test_desfazer_ate_zerar():
    """Desfazer todos os pontos leva a 0x0 sem erro."""
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12}),
        make_evento(2, TipoEvento.PONTO_MARCADO, {"equipe": "A"}),
        make_evento(3, TipoEvento.PONTO_MARCADO, {"equipe": "B"}),
        make_evento(4, TipoEvento.PONTO_DESFEITO, {"ref_seq": 2}),
        make_evento(5, TipoEvento.PONTO_DESFEITO, {"ref_seq": 3}),
    ]
    estado = projetar_estado(eventos)
    assert estado.pontos_a == 0
    assert estado.pontos_b == 0
    assert not estado.encerrada
    assert estado.vencedor is None


def test_desfazer_ponto_da_vitoria():
    """Partida encerrada volta ao estado não encerrado ao desfazer o ponto da vitória."""
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12, "vantagem": True}),
    ]
    seq = 2
    # Equipe A faz 11 pontos
    for _ in range(11):
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"}))
        seq += 1
    # Equipe B faz 10 pontos
    for _ in range(10):
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "B"}))
        seq += 1

    # Equipe A faz o 12º ponto (12x10 com alvo 12 e vantagem 2 -> vitória)
    ponto_vitoria_seq = seq
    eventos.append(
        make_evento(ponto_vitoria_seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"})
    )
    seq += 1

    estado_encerrado = projetar_estado(eventos)
    assert estado_encerrado.pontos_a == 12
    assert estado_encerrado.pontos_b == 10
    assert estado_encerrado.encerrada is True
    assert estado_encerrado.vencedor == "A"

    # Agora desfaz o ponto da vitória
    eventos.append(
        make_evento(seq, TipoEvento.PONTO_DESFEITO, {"ref_seq": ponto_vitoria_seq})
    )
    estado_reaberto = projetar_estado(eventos)
    assert estado_reaberto.pontos_a == 11
    assert estado_reaberto.pontos_b == 10
    assert estado_reaberto.encerrada is False
    assert estado_reaberto.vencedor is None


def test_regra_alterada_no_meio():
    """Desligar a vantagem em 11x11 faz o próximo ponto encerrar."""
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12, "vantagem": True}),
    ]
    seq = 2
    # 11 pontos para cada (11x11)
    for _ in range(11):
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"}))
        seq += 1
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "B"}))
        seq += 1

    # Em 11x11, com vantagem ligada, se A pontuasse iria para 12x11 e NÃO encerraria
    # Altera a regra desligando a vantagem
    eventos.append(make_evento(seq, TipoEvento.REGRA_ALTERADA, {"vantagem": False}))
    seq += 1

    # Próximo ponto da equipe A (12x11)
    eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"}))

    estado = projetar_estado(eventos)
    assert estado.pontos_a == 12
    assert estado.pontos_b == 11
    assert estado.vantagem is False
    assert estado.encerrada is True
    assert estado.vencedor == "A"


def test_teto_da_vantagem():
    """Com alvo 12 e teto 15, encerra em 15x14 mesmo com diferença de apenas 1 ponto."""
    eventos = [
        make_evento(
            1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12, "vantagem": True, "teto": 15}
        ),
    ]
    seq = 2
    # Empate até 14x14
    for _ in range(14):
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"}))
        seq += 1
        eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "B"}))
        seq += 1

    estado_14x14 = projetar_estado(eventos)
    assert estado_14x14.pontos_a == 14
    assert estado_14x14.pontos_b == 14
    assert estado_14x14.encerrada is False

    # Equipe A marca o 15º ponto atingindo o teto
    eventos.append(make_evento(seq, TipoEvento.PONTO_MARCADO, {"equipe": "A"}))
    estado_15x14 = projetar_estado(eventos)
    assert estado_15x14.pontos_a == 15
    assert estado_15x14.pontos_b == 14
    assert estado_15x14.encerrada is True
    assert estado_15x14.vencedor == "A"


def test_determinismo():
    """Executar a projeção duas vezes sobre o mesmo log produz estado idêntico."""
    eventos = [
        make_evento(1, TipoEvento.PARTIDA_INICIADA, {"alvo": 12, "vantagem": True}),
        make_evento(2, TipoEvento.PONTO_MARCADO, {"equipe": "A"}),
        make_evento(3, TipoEvento.PONTO_MARCADO, {"equipe": "B"}),
        make_evento(4, TipoEvento.PONTO_MARCADO, {"equipe": "A"}),
        make_evento(5, TipoEvento.PONTO_DESFEITO, {"ref_seq": 2}),
        make_evento(6, TipoEvento.REGRA_ALTERADA, {"alvo": 15}),
        make_evento(7, TipoEvento.PONTO_MARCADO, {"equipe": "B"}),
    ]

    estado1 = projetar_estado(eventos)
    estado2 = projetar_estado(eventos)

    assert estado1 == estado2
    assert hash(estado1) == hash(estado2)


def test_log_vazio():
    """Projeção de partida sem eventos retorna 0x0 não encerrada."""
    estado = projetar_estado([])
    assert estado.partida_id is None
    assert estado.pontos_a == 0
    assert estado.pontos_b == 0
    assert estado.encerrada is False
    assert estado.vencedor is None
    assert estado.pontos_desfeitos == ()
    assert estado.eventos_ativos_seq == ()
