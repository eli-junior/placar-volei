// @ts-check
/**
 * Quadra local do APK (CV7.US1): a única quadra do aparelho, usada quando não
 * há comunicação com o servidor. O log de eventos fica no aparelho e as regras
 * são as de `partida.js` (paridade com o backend, CV7.TS2).
 *
 * Todo comando segue a mesma ordem: calcula os eventos novos, grava e só então
 * muda o estado em memória. Se a gravação falha, o ponto não vale.
 */
import {
  ErroRegra,
  MSG_ALVO_MUDOU,
  configurarPartida,
  desfazerPonto,
  iniciarPartida,
  marcarPonto,
  projetarPartida,
  reiniciarPartida,
} from './partida.js';

/** @typedef {import('./partida.js').Evento} Evento */
/** @typedef {import('./partida.js').CamposPartida} CamposPartida */
/**
 * @typedef {Object} Armazenamento
 * @property {(chave: string) => Promise<string | null>} ler
 * @property {(chave: string, valor: string) => Promise<void>} gravar
 * @property {(chave: string) => Promise<void>} apagar
 */
/**
 * @typedef {Object} Registro
 * @property {number} versao
 * @property {{ id: string, nome: string, criado_em: string, tema_placar: string }} quadra
 * @property {Evento[]} eventos   todas as partidas, em ordem (o `seq` recomeça a cada partida)
 * @property {ReciboRelogio[]} [recibos]   resultado de cada lance do relógio, para não aplicar duas vezes
 */
/**
 * @typedef {Object} ReciboRelogio
 * @property {string} id
 * @property {string} partida_id
 * @property {string} acao
 * @property {string | null} equipe
 * @property {string | null} alvo
 * @property {'APLICADO' | 'RECUSADO'} status
 * @property {string | null} detalhe
 * @property {number | null} evento_seq
 */

export const CHAVE_QUADRA_LOCAL = 'placar.quadra_local';
export const CHAVE_ILEGIVEL = 'placar.quadra_local.ilegivel';
export const ID_QUADRA_LOCAL = 'LOCAL';
export const ID_OPERADOR_LOCAL = 'local';
/** O relógio é um segundo operador da quadra local, com o controle sempre dele. */
export const ID_RELOGIO_LOCAL = 'relogio-local';
const MAX_RECIBOS = 500;
const UUID = /^[0-9a-fA-F-]{36}$/;
const VERSAO = 1;
const TEMAS_PLACAR = ['esportivo', 'classico'];

/** A gravação no aparelho falhou: o comando não foi aceito. */
export class ErroGravacao extends Error {
  constructor() {
    super('Não foi possível guardar o placar neste aparelho. O lance não foi registrado.');
    this.name = 'ErroGravacao';
  }
}

/** Armazenamento do navegador, usado fora do APK e nos testes. */
export function armazenamentoDoNavegador(armazem = globalThis.localStorage) {
  /** @type {Armazenamento} */
  return {
    async ler(chave) {
      try {
        return armazem.getItem(chave);
      } catch {
        return null;
      }
    },
    async gravar(chave, valor) {
      armazem.setItem(chave, valor);
    },
    async apagar(chave) {
      armazem.removeItem(chave);
    },
  };
}

/**
 * SharedPreferences do Android no APK; `localStorage` no resto. O WebView pode
 * limpar `localStorage` sob pressão de armazenamento, e o log não pode sumir.
 * @returns {Promise<Armazenamento>}
 */
export async function armazenamentoPadrao() {
  const janela = /** @type {any} */ (globalThis.window);
  if (janela?.Capacitor?.getPlatform?.() !== 'android') return armazenamentoDoNavegador();
  const { Preferences } = await import('@capacitor/preferences');
  return {
    async ler(chave) {
      return (await Preferences.get({ key: chave })).value;
    },
    async gravar(chave, valor) {
      await Preferences.set({ key: chave, value: valor });
    },
    async apagar(chave) {
      await Preferences.remove({ key: chave });
    },
  };
}

const uuid = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;

/** Registro lido do aparelho é confiável? Forma, numeração e primeiro evento de cada partida. */
function registroValido(/** @type {any} */ r) {
  if (!r || r.versao !== VERSAO || !Array.isArray(r.eventos) || !r.eventos.length) return false;
  const q = r.quadra;
  if (!q || typeof q.nome !== 'string' || typeof q.criado_em !== 'string' || !TEMAS_PLACAR.includes(q.tema_placar)) return false;
  /** @type {string | null} */
  let partida = null;
  let seq = 0;
  for (const e of r.eventos) {
    if (!e || typeof e.id !== 'string' || typeof e.tipo !== 'string' || typeof e.partida_id !== 'string' || !e.payload || typeof e.payload !== 'object') return false;
    if (e.partida_id !== partida) {
      if (e.tipo !== 'PARTIDA_INICIADA' || e.seq !== 1) return false;
      partida = e.partida_id;
    } else if (e.seq !== seq + 1) {
      return false;
    }
    seq = e.seq;
  }
  return true;
}

export class QuadraLocal {
  /**
   * @param {Armazenamento} armazenamento
   * @param {Registro} registro
   * @param {{ apelido?: string | null, agora?: () => string, novoId?: () => string }} [opcoes]
   */
  constructor(armazenamento, registro, opcoes = {}) {
    this.armazenamento = armazenamento;
    /** @type {Registro} */
    this.registro = registro;
    this.apelido = opcoes.apelido || 'Você';
    this.agora = opcoes.agora ?? (() => new Date().toISOString());
    this.novoId = opcoes.novoId ?? uuid;
    /** @type {Promise<any>} */
    this.fila = Promise.resolve();
  }

  /**
   * Lê a quadra do aparelho. `ilegivel` avisa que havia dados que não deu para
   * usar (eles ficam guardados à parte até a pessoa decidir). Erro de leitura
   * do armazenamento sobe para quem chamou.
   * @param {Armazenamento} armazenamento
   * @param {{ apelido?: string | null, agora?: () => string, novoId?: () => string }} [opcoes]
   * @returns {Promise<{ quadra: QuadraLocal | null, ilegivel: boolean }>}
   */
  static async abrir(armazenamento, opcoes = {}) {
    // Falha ao ler não é dado ilegível: propaga, para ninguém descartar uma
    // quadra boa só porque o aparelho engasgou.
    const bruto = await armazenamento.ler(CHAVE_QUADRA_LOCAL);
    if (bruto === null) return { quadra: null, ilegivel: false };
    let registro = null;
    try {
      registro = JSON.parse(bruto);
    } catch {}
    if (!registroValido(registro)) {
      // Cópia para diagnóstico; falhar aqui não impede o app de abrir.
      try {
        await armazenamento.gravar(CHAVE_ILEGIVEL, bruto);
      } catch {}
      return { quadra: null, ilegivel: true };
    }
    return { quadra: new QuadraLocal(armazenamento, registro, opcoes), ilegivel: false };
  }

  /**
   * Cria a quadra local, com o mesmo padrão do servidor (10 pontos, vantagem).
   * @param {Armazenamento} armazenamento
   * @param {{ apelido?: string | null, agora?: () => string, novoId?: () => string }} [opcoes]
   * @param {CamposPartida} [campos]
   */
  static async criar(armazenamento, opcoes = {}, campos = {}) {
    const agora = opcoes.agora ?? (() => new Date().toISOString());
    const novoId = opcoes.novoId ?? uuid;
    const ctx = { quadraId: ID_QUADRA_LOCAL, autorId: ID_OPERADOR_LOCAL, agora, novoId };
    const eventos = iniciarPartida(ctx, novoId(), campos);
    /** @type {Registro} */
    const registro = {
      versao: VERSAO,
      quadra: { id: ID_QUADRA_LOCAL, nome: 'Quadra local', criado_em: agora(), tema_placar: 'esportivo' },
      eventos,
    };
    try {
      await armazenamento.gravar(CHAVE_QUADRA_LOCAL, JSON.stringify(registro));
    } catch {
      throw new ErroGravacao();
    }
    return new QuadraLocal(armazenamento, registro, opcoes);
  }

  /** Descarta os dados ilegíveis e a cópia de diagnóstico, para começar do zero. */
  static async descartarIlegivel(/** @type {Armazenamento} */ armazenamento) {
    await armazenamento.apagar(CHAVE_QUADRA_LOCAL);
    await armazenamento.apagar(CHAVE_ILEGIVEL);
  }

  get eventosDaPartida() {
    const atual = this.registro.eventos[this.registro.eventos.length - 1].partida_id;
    return this.registro.eventos.filter((e) => e.partida_id === atual);
  }

  /** Há partida em andamento (não encerrada): a quadra local segue acessível. */
  get emAndamento() {
    return !this.snapshot().estado_partida.encerrada;
  }

  get contexto() {
    return { quadraId: ID_QUADRA_LOCAL, autorId: ID_OPERADOR_LOCAL, agora: this.agora, novoId: this.novoId };
  }

  get contextoRelogio() {
    return { ...this.contexto, autorId: ID_RELOGIO_LOCAL };
  }

  get eu() {
    return { id: ID_OPERADOR_LOCAL, quadra_id: ID_QUADRA_LOCAL, apelido: this.apelido, papel: /** @type {const} */ ('ADMIN') };
  }

  /** Mesma forma do snapshot do servidor, para a `SalaQuadra` consumir sem mudar. */
  snapshot() {
    const partida = projetarPartida(this.eventosDaPartida, { [ID_OPERADOR_LOCAL]: this.apelido, [ID_RELOGIO_LOCAL]: 'Relógio' });
    const eventos = this.registro.eventos;
    const q = this.registro.quadra;
    return {
      quadra: {
        id: q.id,
        nome: q.nome,
        criado_em: q.criado_em,
        atualizado_em: eventos[eventos.length - 1].criado_em,
        controle_id: ID_OPERADOR_LOCAL,
        controle_versao: 1,
        tema_placar: q.tema_placar,
        partida_id: partida.partida_id,
      },
      ...partida,
      participantes: [{ ...this.eu, criado_em: q.criado_em }],
    };
  }

  /**
   * O que o relógio precisa do placar, sem a linha do tempo (o Data Layer limita
   * cada mensagem a ~100 KB). O controle é sempre dele: na quadra local celular
   * e relógio operam juntos, sem passar o comando de um para o outro.
   * @param {string | null} [comandoId]  lance do relógio que este estado confirma
   */
  snapshotParaRelogio(comandoId = null) {
    const { quadra, partida_id, seq, estado_partida } = this.snapshot();
    return {
      quadra: { id: quadra.id, nome: quadra.nome, controle_id: ID_RELOGIO_LOCAL, controle_versao: 1 },
      partida_id,
      seq,
      estado_partida,
      participantes: [
        { id: ID_RELOGIO_LOCAL, apelido: 'Relógio', papel: 'ADMIN' },
        { id: ID_OPERADOR_LOCAL, apelido: this.apelido, papel: 'ADMIN' },
      ],
      ...(comandoId ? { comando_id: comandoId } : {}),
    };
  }

  /**
   * Lance do relógio (mesmo corpo do `POST /api/watch/comandos`). Aplica uma
   * vez só: o reenvio do mesmo id devolve o mesmo resultado. Devolve o que o
   * relógio espera: `{ status, recibo, estado }`, ou `{ status, detail }` quando
   * o corpo nem é um lance válido.
   * @param {any} corpo
   * @returns {Promise<{ status: number, recibo?: object, estado?: object, detail?: string }>}
   */
  aplicarComandoRelogio(corpo) {
    return this.enfileirar(async () => {
      const invalido = corpoInvalido(corpo);
      if (invalido) return { status: 422, detail: invalido };
      const alvo = corpo.alvo_seq != null ? `seq:${corpo.alvo_seq}` : corpo.alvo_comando != null ? `comando:${corpo.alvo_comando}` : null;
      const equipe = corpo.equipe ?? null;
      const recibos = this.registro.recibos ?? [];

      const anterior = recibos.find((r) => r.id === corpo.id);
      if (anterior) {
        const igual = anterior.partida_id === corpo.partida_id && anterior.acao === corpo.acao && anterior.equipe === equipe && anterior.alvo === alvo;
        if (!igual) return { status: 409, detail: 'Este lance já foi usado com outro conteúdo.' };
        return { status: 200, recibo: paraRecibo(anterior), estado: this.snapshotParaRelogio() };
      }

      /** @type {Evento[]} */
      let novos = [];
      /** @type {string | null} */
      let recusa = null;
      try {
        if (corpo.partida_id !== this.snapshot().partida_id) {
          throw new ErroRegra(409, 'Uma nova partida começou. Este lance não vale para ela.');
        }
        let alvoSeq = corpo.alvo_seq ?? null;
        if (corpo.alvo_comando != null) {
          const alvoRecibo = recibos.find((r) => r.id === corpo.alvo_comando);
          if (!alvoRecibo || alvoRecibo.acao !== 'ponto' || alvoRecibo.status !== 'APLICADO' || alvoRecibo.partida_id !== corpo.partida_id) {
            throw new ErroRegra(409, MSG_ALVO_MUDOU);
          }
          alvoSeq = alvoRecibo.evento_seq;
        }
        const eventos = this.eventosDaPartida;
        if (corpo.acao === 'ponto') novos = marcarPonto(eventos, corpo.equipe, this.contextoRelogio);
        else if (corpo.acao === 'desfazer') novos = desfazerPonto(eventos, alvoSeq, this.contextoRelogio);
        else novos = reiniciarPartida(eventos, {}, this.contextoRelogio, this.novoId());
      } catch (e) {
        if (!(e instanceof ErroRegra)) throw e;
        recusa = e.message;
      }

      /** @type {ReciboRelogio} */
      const recibo = {
        id: corpo.id,
        partida_id: corpo.partida_id,
        acao: corpo.acao,
        equipe,
        alvo,
        status: recusa === null ? 'APLICADO' : 'RECUSADO',
        detalhe: recusa,
        evento_seq: recusa === null ? novos[0].seq : null,
      };
      await this.confirmar(novos, {}, recibo);
      return {
        status: recusa === null ? 201 : 200,
        recibo: paraRecibo(recibo),
        estado: this.snapshotParaRelogio(recusa === null ? corpo.id : null),
      };
    });
  }

  /**
   * Um comando por vez, na ordem do toque: o quinto toque em dois segundos
   * vira o quinto ponto, e nunca dois gravam por cima um do outro.
   * @template T
   * @param {() => Promise<T>} tarefa
   * @returns {Promise<T>}
   */
  enfileirar(tarefa) {
    const proxima = this.fila.catch(() => {}).then(tarefa);
    this.fila = proxima;
    return proxima;
  }

  /**
   * @param {Evento[]} novos
   * @param {Partial<Registro['quadra']>} [quadra]
   * @param {ReciboRelogio | null} [recibo]
   */
  async confirmar(novos, quadra = {}, recibo = null) {
    /** @type {Registro} */
    const proximo = {
      ...this.registro,
      quadra: { ...this.registro.quadra, ...quadra },
      eventos: [...this.registro.eventos, ...novos],
    };
    if (recibo) proximo.recibos = [...(this.registro.recibos ?? []), recibo].slice(-MAX_RECIBOS);
    try {
      await this.armazenamento.gravar(CHAVE_QUADRA_LOCAL, JSON.stringify(proximo));
    } catch {
      throw new ErroGravacao();
    }
    this.registro = proximo;
    return this.snapshot();
  }

  /** @param {string} equipe */
  marcarPonto(equipe) {
    return this.enfileirar(() => this.confirmar(marcarPonto(this.eventosDaPartida, equipe, this.contexto)));
  }

  desfazer() {
    return this.enfileirar(() => this.confirmar(desfazerPonto(this.eventosDaPartida, null, this.contexto)));
  }

  /** @param {CamposPartida & { tema_placar?: string | null }} campos */
  configurar(campos) {
    return this.enfileirar(() => {
      const tema = this.#tema(campos);
      const novos = configurarPartida(this.eventosDaPartida, campos, this.contexto);
      if (!novos.length && tema === this.registro.quadra.tema_placar) return Promise.resolve(this.snapshot());
      return this.confirmar(novos, { tema_placar: tema });
    });
  }

  /** @param {CamposPartida & { tema_placar?: string | null }} [campos] */
  reiniciar(campos = {}) {
    return this.enfileirar(() => {
      // Como no servidor, "ainda não encerrada" vem antes do tema inválido.
      const novos = reiniciarPartida(this.eventosDaPartida, campos, this.contexto, this.novoId());
      return this.confirmar(novos, { tema_placar: this.#tema(campos) });
    });
  }

  /** Apaga a quadra do aparelho (a única do APK). */
  apagar() {
    return this.enfileirar(async () => {
      try {
        await this.armazenamento.apagar(CHAVE_QUADRA_LOCAL);
      } catch {
        throw new ErroGravacao();
      }
    });
  }

  /** @param {{ tema_placar?: string | null }} campos */
  #tema(campos) {
    const tema = campos.tema_placar;
    if (tema == null) return this.registro.quadra.tema_placar;
    if (!TEMAS_PLACAR.includes(tema)) throw new ErroRegra(422, 'Tema de placar inválido.');
    return tema;
  }
}

/** @param {ReciboRelogio} r */
const paraRecibo = (r) => ({ id: r.id, status: r.status, detalhe: r.detalhe, evento_seq: r.evento_seq });

/**
 * As mesmas regras de forma do `CommandBody` do servidor. Devolve o motivo ou null.
 * @param {any} c
 */
function corpoInvalido(c) {
  if (!c || typeof c !== 'object') return 'Comando inválido.';
  if (typeof c.id !== 'string' || !UUID.test(c.id)) return 'id inválido.';
  if (typeof c.partida_id !== 'string' || !c.partida_id || c.partida_id.length > 64) return 'partida_id inválido.';
  if (!Number.isInteger(c.controle_versao) || c.controle_versao < 0) return 'controle_versao inválido.';
  const acao = c.acao ?? 'ponto';
  if (!['ponto', 'desfazer', 'nova_partida'].includes(acao)) return 'acao inválida.';
  c.acao = acao;
  if (c.equipe != null && c.equipe !== 'A' && c.equipe !== 'B') return 'equipe inválida.';
  if (c.alvo_seq != null && (!Number.isInteger(c.alvo_seq) || c.alvo_seq < 1)) return 'alvo_seq inválido.';
  if (c.alvo_comando != null && !(typeof c.alvo_comando === 'string' && UUID.test(c.alvo_comando))) return 'alvo_comando inválido.';
  const alvos = (c.alvo_seq != null ? 1 : 0) + (c.alvo_comando != null ? 1 : 0);
  if (acao === 'ponto' && (c.equipe == null || alvos)) return 'Ponto leva a equipe e nenhum alvo.';
  if (acao === 'desfazer' && (c.equipe != null || alvos !== 1)) return 'Desfazer leva exatamente um alvo e nenhuma equipe.';
  if (acao === 'nova_partida' && (c.equipe != null || alvos)) return 'Nova partida não leva equipe nem alvo.';
  return null;
}
