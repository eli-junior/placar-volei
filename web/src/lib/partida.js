// @ts-check
/**
 * Regras e projeção da partida em JS (CV7.TS2).
 *
 * Porte fiel de `app/projecao.py` e das ações `pontos`, `desfazer`, `configurar`
 * e `reiniciar` de `app/comandos.py`, para a quadra local do APK (CV7.US1).
 * O Python segue sendo a referência: `tests/test_paridade_fixtures.py` gera as
 * fixtures e `web/tests/paridade.test.js` confere que este módulo dá o mesmo
 * resultado. Mudou a regra de um lado, a paridade quebra e avisa.
 *
 * Tudo aqui é puro: relógio e identificadores entram pelo contexto.
 */

export const TipoEvento = Object.freeze({
  PARTIDA_INICIADA: 'PARTIDA_INICIADA',
  PONTO_MARCADO: 'PONTO_MARCADO',
  PONTO_DESFEITO: 'PONTO_DESFEITO',
  REGRA_ALTERADA: 'REGRA_ALTERADA',
  PARTIDA_ENCERRADA: 'PARTIDA_ENCERRADA',
  PAPEL_ALTERADO: 'PAPEL_ALTERADO',
  ADMIN_SUCEDIDO: 'ADMIN_SUCEDIDO',
  ADMIN_ASSUMIDO: 'ADMIN_ASSUMIDO',
  CONTROLE_ASSUMIDO: 'CONTROLE_ASSUMIDO',
  CONTROLE_TRANSFERIDO: 'CONTROLE_TRANSFERIDO',
  CONTROLE_DEVOLVIDO: 'CONTROLE_DEVOLVIDO',
});

export const MSG_ALVO_MUDOU = 'O placar mudou; este desfazer não foi aplicado.';

/**
 * @typedef {Object} Evento
 * @property {string} id
 * @property {string} quadra_id
 * @property {string} partida_id
 * @property {number} seq
 * @property {string} tipo
 * @property {Record<string, any>} payload
 * @property {string | null} autor_id
 * @property {string} criado_em
 */

/**
 * Recusa de uma regra, com o mesmo status HTTP que o servidor devolveria.
 */
export class ErroRegra extends Error {
  /** @param {number} status @param {string} detalhe */
  constructor(status, detalhe) {
    super(detalhe);
    this.name = 'ErroRegra';
    this.status = status;
  }
}

/**
 * @param {number} pontosA
 * @param {number} pontosB
 * @param {number} alvo
 * @param {boolean} vantagem
 * @param {number | null} teto
 * @returns {[boolean, 'A' | 'B' | null]}
 */
export function avaliarVitoria(pontosA, pontosB, alvo, vantagem, teto) {
  if (vantagem) {
    if (teto !== null && pontosA >= teto && pontosA > pontosB) return [true, 'A'];
    if (teto !== null && pontosB >= teto && pontosB > pontosA) return [true, 'B'];
    if (pontosA >= alvo && pontosA - pontosB >= 2) return [true, 'A'];
    if (pontosB >= alvo && pontosB - pontosA >= 2) return [true, 'B'];
  } else {
    if (pontosA >= alvo && pontosA > pontosB) return [true, 'A'];
    if (pontosB >= alvo && pontosB > pontosA) return [true, 'B'];
  }
  return [false, null];
}

/** @param {Evento[]} eventos */
function pontosDesfeitos(eventos) {
  /** @type {Set<number>} */
  const desfeitos = new Set();
  for (const evento of eventos) {
    if (evento.tipo === TipoEvento.PONTO_DESFEITO) {
      const ref = evento.payload.ref_seq;
      if (ref !== undefined && ref !== null) desfeitos.add(Number(ref));
    }
  }
  return desfeitos;
}

/** A chave existe no payload e não é nula (o `x in p and p[x] is not None` do Python). */
const presente = (/** @type {Record<string, any>} */ payload, /** @type {string} */ chave) =>
  chave in payload && payload[chave] !== null && payload[chave] !== undefined;

/** @param {any} valor */
const maiusculo = (valor) => String(valor ?? '').toUpperCase();

/**
 * @param {Evento[]} eventos
 */
export function projetarEstado(eventos) {
  /** @type {string | null} */
  let partidaId = null;
  let alvo = 10;
  let vantagem = true;
  /** @type {number | null} */
  let teto = null;
  let equipeA = 'Equipe A';
  let equipeB = 'Equipe B';
  /** @type {string[]} */
  let jogadoresA = [];
  /** @type {string[]} */
  let jogadoresB = [];

  const desfeitos = pontosDesfeitos(eventos);
  let pontosA = 0;
  let pontosB = 0;
  /** @type {number[]} */
  const ativosSeq = [];
  /** @type {string[]} */
  const equipesAtivas = [];

  for (const evento of eventos) {
    if (partidaId === null && evento.partida_id) partidaId = evento.partida_id;
    const payload = evento.payload;

    if (evento.tipo === TipoEvento.PARTIDA_INICIADA || evento.tipo === TipoEvento.REGRA_ALTERADA) {
      if (presente(payload, 'alvo')) alvo = Math.trunc(Number(payload.alvo));
      if (presente(payload, 'vantagem')) vantagem = Boolean(payload.vantagem);
      if ('teto' in payload) teto = presente(payload, 'teto') ? Math.trunc(Number(payload.teto)) : null;
      if (payload.equipe_a) equipeA = String(payload.equipe_a);
      if (payload.equipe_b) equipeB = String(payload.equipe_b);
      if (Array.isArray(payload.jogadores_a)) jogadoresA = payload.jogadores_a.map(String);
      if (Array.isArray(payload.jogadores_b)) jogadoresB = payload.jogadores_b.map(String);
    } else if (evento.tipo === TipoEvento.PONTO_MARCADO && !desfeitos.has(evento.seq)) {
      const equipe = maiusculo(payload.equipe);
      if (equipe === 'A') pontosA += 1;
      else if (equipe === 'B') pontosB += 1;
      if (equipe === 'A' || equipe === 'B') {
        ativosSeq.push(evento.seq);
        equipesAtivas.push(equipe);
      }
    }
  }

  const [encerrada, vencedor] = avaliarVitoria(pontosA, pontosB, alvo, vantagem, teto);
  return {
    partida_id: partidaId,
    pontos_a: pontosA,
    pontos_b: pontosB,
    equipe_a: equipeA,
    equipe_b: equipeB,
    alvo,
    vantagem,
    teto,
    encerrada,
    vencedor,
    pontos_desfeitos: [...desfeitos].sort((x, y) => x - y),
    eventos_ativos_seq: ativosSeq,
    jogadores_a: jogadoresA,
    jogadores_b: jogadoresB,
    equipes_ativas: equipesAtivas,
  };
}

/** @param {string} texto */
function capitalizar(texto) {
  return texto.charAt(0).toUpperCase() + texto.slice(1).toLowerCase();
}

/**
 * Narrativa cronológica da partida a partir do log.
 * @param {Evento[]} eventos
 * @param {Record<string, string>} [apelidosPorAutor]
 */
export function projetarLinhaDoTempo(eventos, apelidosPorAutor = {}) {
  /** @type {Map<number, Evento>} */
  const porSeq = new Map(eventos.map((e) => [e.seq, e]));
  const desfeitos = pontosDesfeitos(eventos);

  const itens = [];
  let equipeA = 'Equipe A';
  let equipeB = 'Equipe B';
  let alvo = 10;
  let vantagem = true;
  /** @type {number[]} */
  const ativosA = [];
  /** @type {number[]} */
  const ativosB = [];

  /** @param {string} equipe */
  const nomeDe = (equipe) => (equipe === 'A' ? equipeA : equipe === 'B' ? equipeB : equipe);

  for (const evento of eventos) {
    const autorApelido = evento.autor_id ? (apelidosPorAutor[evento.autor_id] ?? 'Participante') : 'Sistema';
    const payload = evento.payload;
    /** @type {string | null} */
    let equipe = null;
    /** @type {string | null} */
    let equipeNome = null;
    /** @type {number | null} */
    let refSeq = null;
    let anulado = false;
    let descricao = '';

    if (evento.tipo === TipoEvento.PARTIDA_INICIADA) {
      if (payload.equipe_a) equipeA = String(payload.equipe_a);
      if (payload.equipe_b) equipeB = String(payload.equipe_b);
      if (presente(payload, 'alvo')) alvo = Math.trunc(Number(payload.alvo));
      if (presente(payload, 'vantagem')) vantagem = Boolean(payload.vantagem);
      const teto = presente(payload, 'teto') ? Math.trunc(Number(payload.teto)) : null;
      const descVantagem = vantagem ? ' com vantagem de 2' : '';
      const descTeto = teto ? ` (teto ${teto})` : '';
      descricao = `Partida iniciada até ${alvo} pts${descVantagem}${descTeto}`;
    } else if (evento.tipo === TipoEvento.PONTO_MARCADO) {
      equipe = maiusculo(payload.equipe);
      equipeNome = nomeDe(equipe);
      descricao = `Ponto para ${equipeNome}`;
      if (desfeitos.has(evento.seq)) anulado = true;
      if (equipe === 'A') ativosA.push(evento.seq);
      else if (equipe === 'B') ativosB.push(evento.seq);
    } else if (evento.tipo === TipoEvento.PONTO_DESFEITO) {
      const ref = payload.ref_seq;
      if (ref !== undefined && ref !== null) {
        refSeq = Number(ref);
        const original = porSeq.get(refSeq);
        if (original) {
          const origEquipe = maiusculo(original.payload.equipe);
          equipe = origEquipe;
          equipeNome = nomeDe(origEquipe);
          descricao = `Ponto de ${equipeNome} anulado`;
          const lista = origEquipe === 'A' ? ativosA : origEquipe === 'B' ? ativosB : null;
          const posicao = lista ? lista.indexOf(refSeq) : -1;
          if (lista && posicao >= 0) lista.splice(posicao, 1);
        } else {
          descricao = `Ponto #${refSeq} anulado`;
        }
      } else {
        descricao = 'Ponto anulado';
      }
    } else if (evento.tipo === TipoEvento.REGRA_ALTERADA) {
      /** @type {string[]} */
      const partes = [];
      if (presente(payload, 'alvo')) {
        alvo = Math.trunc(Number(payload.alvo));
        partes.push(`alvo ${alvo} pts`);
      }
      if (payload.equipe_a) {
        equipeA = String(payload.equipe_a);
        partes.push(`Time A: ${equipeA}`);
      }
      if (payload.equipe_b) {
        equipeB = String(payload.equipe_b);
        partes.push(`Time B: ${equipeB}`);
      }
      descricao = partes.length ? `Configuração da partida: ${partes.join(', ')}` : `Regra alterada: alvo ${alvo} pts`;
    } else if (evento.tipo === TipoEvento.CONTROLE_ASSUMIDO) {
      descricao = `${autorApelido} assumiu o controle`;
    } else if (evento.tipo === TipoEvento.CONTROLE_TRANSFERIDO) {
      descricao = `${autorApelido} passou o controle para ${payload.apelido ?? 'outro participante'}`;
    } else if (evento.tipo === TipoEvento.CONTROLE_DEVOLVIDO) {
      const ausente = payload.anterior_apelido ?? 'o controlador';
      const destino = payload.apelido ?? 'o admin';
      if (payload.motivo === 'relogio_trocou_de_quadra') {
        descricao = `Controle devolvido para ${destino}: relógio foi para outra quadra`;
      } else if (payload.motivo === 'relogio_revogado' || payload.motivo === 'relogio_desabilitado') {
        descricao = `Controle devolvido para ${destino}: relógio desvinculado`;
      } else {
        descricao = `Controle devolvido para ${destino} por ausência de ${ausente}`;
      }
    } else if (evento.tipo === TipoEvento.PAPEL_ALTERADO) {
      const novoPapel = payload.papel;
      const alvoNome = payload.apelido ?? 'participante';
      if (novoPapel === 'CONTROLADOR') descricao = `${autorApelido} promoveu ${alvoNome} a controlador`;
      else if (novoPapel === 'ESPECTADOR') descricao = `${autorApelido} revogou controlador de ${alvoNome}`;
      else if (novoPapel === 'ADMIN') descricao = `${autorApelido} autorizou ${alvoNome} como admin`;
      else descricao = `${autorApelido} alterou papel de ${alvoNome} para ${novoPapel}`;
    } else if (evento.tipo === TipoEvento.ADMIN_SUCEDIDO) {
      const novoAdmin = payload.novo_admin_apelido;
      const antigoAdmin = payload.antigo_admin_apelido;
      descricao = novoAdmin
        ? `${novoAdmin} assumiu a administração por sucessão (ausência de ${antigoAdmin})`
        : `Administração vaga por ausência de ${antigoAdmin}`;
    } else if (evento.tipo === TipoEvento.PARTIDA_ENCERRADA) {
      const vencedor = payload.vencedor;
      descricao = `Partida encerrada. Vitória de ${vencedor === 'A' ? equipeA : vencedor === 'B' ? equipeB : vencedor}!`;
    } else {
      descricao = capitalizar(evento.tipo.replaceAll('_', ' '));
    }

    itens.push({
      id: evento.id,
      seq: evento.seq,
      tipo: evento.tipo,
      equipe,
      equipe_nome: equipeNome,
      autor_id: evento.autor_id,
      autor_apelido: autorApelido,
      criado_em: evento.criado_em,
      pontos_a: ativosA.length,
      pontos_b: ativosB.length,
      anulado,
      ref_seq: refSeq,
      descricao,
    });
  }
  return itens;
}

/**
 * Recorte do snapshot que depende só do log da partida.
 * @param {Evento[]} eventos
 * @param {Record<string, string>} [apelidosPorAutor]
 */
export function projetarPartida(eventos, apelidosPorAutor = {}) {
  const estado = projetarEstado(eventos);
  return {
    partida_id: estado.partida_id,
    seq: eventos.length ? eventos[eventos.length - 1].seq : 0,
    estado_partida: estado,
    linha_do_tempo: projetarLinhaDoTempo(eventos, apelidosPorAutor),
  };
}

// --- Entrada de dados -------------------------------------------------------

const LIMITE_JOGADOR = 30;
const LIMITE_EQUIPE = 60;

/**
 * Nome da equipe a partir dos jogadores ou do nome direto.
 * @param {string | null | undefined} j1
 * @param {string | null | undefined} j2
 * @param {string | null | undefined} equipeDireta
 * @param {string} padrao
 * @returns {[string, string[]]}
 */
export function formatarNomeEquipe(j1, j2, equipeDireta, padrao) {
  /** @type {string[]} */
  const jogadores = [];
  if (j1 && j1.trim()) jogadores.push(j1.trim());
  if (j2 && j2.trim()) jogadores.push(j2.trim());
  if (jogadores.length) return [jogadores.join(' / '), jogadores];
  if (equipeDireta && equipeDireta.trim()) return [equipeDireta.trim(), jogadores];
  return [padrao, jogadores];
}

/**
 * @typedef {Object} CamposPartida
 * @property {string | null} [time_a_jogador1]
 * @property {string | null} [time_a_jogador2]
 * @property {string | null} [time_b_jogador1]
 * @property {string | null} [time_b_jogador2]
 * @property {string | null} [equipe_a]
 * @property {string | null} [equipe_b]
 * @property {number | null} [alvo]
 * @property {boolean | null} [vantagem]
 * @property {number | null} [teto]
 */

/**
 * Mesmas validações dos corpos HTTP (Pydantic): 422 como no servidor.
 * @param {CamposPartida} campos
 */
function validarCampos(campos) {
  const invalido = (/** @type {string} */ detalhe) => new ErroRegra(422, detalhe);
  for (const campo of /** @type {const} */ (['time_a_jogador1', 'time_a_jogador2', 'time_b_jogador1', 'time_b_jogador2'])) {
    const valor = campos[campo];
    if (valor != null && valor.length > LIMITE_JOGADOR) throw invalido(`${campo} longo demais`);
  }
  for (const campo of /** @type {const} */ (['equipe_a', 'equipe_b'])) {
    const valor = campos[campo];
    if (valor != null && valor.length > LIMITE_EQUIPE) throw invalido(`${campo} longo demais`);
  }
  const { alvo, teto } = campos;
  if (alvo != null && (!Number.isInteger(alvo) || alvo < 1 || alvo > 100)) throw invalido('alvo fora do limite');
  if (teto != null && (!Number.isInteger(teto) || teto < 1 || teto > 200)) throw invalido('teto fora do limite');
}

/**
 * @typedef {Object} Contexto
 * @property {string} quadraId
 * @property {string | null} autorId
 * @property {() => string} agora   ISO 8601
 * @property {() => string} novoId
 */

/**
 * Próximos eventos do log, já numerados, para anexar a `eventos`.
 * @param {Contexto} ctx
 * @param {string} partidaId
 * @param {number} ultimoSeq
 * @param {Array<[string, Record<string, any>]>} novos
 * @returns {Evento[]}
 */
function criarEventos(ctx, partidaId, ultimoSeq, novos) {
  return novos.map(([tipo, payload], i) => ({
    id: ctx.novoId(),
    quadra_id: ctx.quadraId,
    partida_id: partidaId,
    seq: ultimoSeq + 1 + i,
    tipo,
    payload,
    autor_id: ctx.autorId,
    criado_em: ctx.agora(),
  }));
}

/** @param {Evento[]} eventos */
const ultimoSeqDe = (eventos) => (eventos.length ? eventos[eventos.length - 1].seq : 0);

/**
 * Quadra nova: o evento inicial da primeira partida (como `POST /quadras`).
 * @param {Contexto} ctx
 * @param {string} partidaId
 * @param {CamposPartida} [campos]
 * @returns {Evento[]}
 */
export function iniciarPartida(ctx, partidaId, campos = {}) {
  validarCampos(campos);
  const alvo = campos.alvo ?? 10;
  const teto = campos.teto ?? null;
  if (teto !== null && teto < alvo) {
    throw new ErroRegra(422, 'O teto da vantagem não pode ser menor que a pontuação-alvo.');
  }
  const [nomeA, jogadoresA] = formatarNomeEquipe(campos.time_a_jogador1, campos.time_a_jogador2, campos.equipe_a, 'Equipe A');
  const [nomeB, jogadoresB] = formatarNomeEquipe(campos.time_b_jogador1, campos.time_b_jogador2, campos.equipe_b, 'Equipe B');
  return criarEventos(ctx, partidaId, 0, [
    [
      TipoEvento.PARTIDA_INICIADA,
      {
        alvo,
        vantagem: campos.vantagem ?? true,
        teto,
        equipe_a: nomeA || 'Equipe A',
        equipe_b: nomeB || 'Equipe B',
        jogadores_a: jogadoresA,
        jogadores_b: jogadoresB,
      },
    ],
  ]);
}

/**
 * Ponto da equipe. Devolve os eventos novos (o ponto e, se fechou a partida,
 * o encerramento).
 * @param {Evento[]} eventos
 * @param {string} equipeBruta
 * @param {Contexto} ctx
 * @returns {Evento[]}
 */
export function marcarPonto(eventos, equipeBruta, ctx) {
  const estado = projetarEstado(eventos);
  const equipe = String(equipeBruta).trim().toUpperCase();
  if (equipe !== 'A' && equipe !== 'B') throw new ErroRegra(422, "Equipe deve ser 'A' ou 'B'.");
  if (estado.encerrada) throw new ErroRegra(400, 'A partida já está encerrada.');
  const partidaId = /** @type {string} */ (estado.partida_id);
  const ponto = criarEventos(ctx, partidaId, ultimoSeqDe(eventos), [[TipoEvento.PONTO_MARCADO, { equipe }]]);
  const depois = projetarEstado([...eventos, ...ponto]);
  if (!depois.encerrada) return ponto;
  return [
    ...ponto,
    ...criarEventos(ctx, partidaId, ponto[0].seq, [
      [
        TipoEvento.PARTIDA_ENCERRADA,
        {
          vencedor: depois.vencedor,
          pontos_a: depois.pontos_a,
          pontos_b: depois.pontos_b,
          alvo: depois.alvo,
          vantagem: depois.vantagem,
          teto: depois.teto,
        },
      ],
    ]),
  ];
}

/**
 * Desfaz o último ponto ativo. `alvoSeq` é o ponto que quem pediu viu no topo.
 * @param {Evento[]} eventos
 * @param {number | null} alvoSeq
 * @param {Contexto} ctx
 * @returns {Evento[]}
 */
export function desfazerPonto(eventos, alvoSeq, ctx) {
  const estado = projetarEstado(eventos);
  if (!estado.eventos_ativos_seq.length) throw new ErroRegra(400, 'Nenhum ponto para desfazer.');
  const ultimo = estado.eventos_ativos_seq[estado.eventos_ativos_seq.length - 1];
  if (alvoSeq !== null && alvoSeq !== undefined && alvoSeq !== ultimo) throw new ErroRegra(409, MSG_ALVO_MUDOU);
  return criarEventos(ctx, /** @type {string} */ (estado.partida_id), ultimoSeqDe(eventos), [
    [TipoEvento.PONTO_DESFEITO, { ref_seq: ultimo }],
  ]);
}

const CAMPOS_REGRA = /** @type {const} */ (['equipe_a', 'equipe_b', 'jogadores_a', 'jogadores_b', 'alvo', 'vantagem', 'teto']);

/**
 * Valores da configuração a partir dos campos do formulário.
 * @param {CamposPartida} campos
 * @returns {Record<string, any>}
 */
function regrasDosCampos(campos) {
  /** @type {Record<string, any>} */
  const regras = {};
  const [nomeA, jogadoresA] = formatarNomeEquipe(campos.time_a_jogador1, campos.time_a_jogador2, campos.equipe_a, '');
  const [nomeB, jogadoresB] = formatarNomeEquipe(campos.time_b_jogador1, campos.time_b_jogador2, campos.equipe_b, '');
  if (nomeA) {
    regras.equipe_a = nomeA;
    regras.jogadores_a = jogadoresA;
  }
  if (nomeB) {
    regras.equipe_b = nomeB;
    regras.jogadores_b = jogadoresB;
  }
  if (campos.alvo != null) regras.alvo = campos.alvo;
  if (campos.vantagem != null) regras.vantagem = campos.vantagem;
  if (campos.teto != null) regras.teto = campos.teto;
  return regras;
}

/**
 * Ajusta regras e nomes no meio da partida. Sem mudança, não há evento.
 * @param {Evento[]} eventos
 * @param {CamposPartida} campos
 * @param {Contexto} ctx
 * @returns {Evento[]}
 */
export function configurarPartida(eventos, campos, ctx) {
  validarCampos(campos);
  const regras = regrasDosCampos(campos);
  const payload = Object.fromEntries(CAMPOS_REGRA.filter((k) => k in regras).map((k) => [k, regras[k]]));
  if (!Object.keys(payload).length) return [];
  const estado = projetarEstado(eventos);
  return criarEventos(ctx, /** @type {string} */ (estado.partida_id), ultimoSeqDe(eventos), [[TipoEvento.REGRA_ALTERADA, payload]]);
}

/**
 * Nova partida depois de uma encerrada, herdando regras e nomes do estado
 * quando o formulário não os traz.
 * @param {Evento[]} eventos
 * @param {CamposPartida} campos
 * @param {Contexto} ctx
 * @param {string} novaPartidaId
 * @returns {Evento[]}
 */
export function reiniciarPartida(eventos, campos, ctx, novaPartidaId) {
  validarCampos(campos);
  const estado = projetarEstado(eventos);
  if (!estado.encerrada) throw new ErroRegra(400, 'A partida atual ainda não foi encerrada.');
  const regras = regrasDosCampos(campos);
  return criarEventos(ctx, novaPartidaId, 0, [
    [
      TipoEvento.PARTIDA_INICIADA,
      {
        alvo: regras.alvo ?? estado.alvo,
        vantagem: regras.vantagem ?? estado.vantagem,
        teto: 'teto' in regras ? regras.teto : estado.teto,
        equipe_a: regras.equipe_a || estado.equipe_a || 'Equipe A',
        equipe_b: regras.equipe_b || estado.equipe_b || 'Equipe B',
        jogadores_a: regras.jogadores_a ?? estado.jogadores_a ?? [],
        jogadores_b: regras.jogadores_b ?? estado.jogadores_b ?? [],
      },
    ],
  ]);
}
