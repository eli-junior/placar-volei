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
 */

export const CHAVE_QUADRA_LOCAL = 'placar.quadra_local';
export const CHAVE_ILEGIVEL = 'placar.quadra_local.ilegivel';
export const ID_QUADRA_LOCAL = 'LOCAL';
export const ID_OPERADOR_LOCAL = 'local';
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

  get eu() {
    return { id: ID_OPERADOR_LOCAL, quadra_id: ID_QUADRA_LOCAL, apelido: this.apelido, papel: /** @type {const} */ ('ADMIN') };
  }

  /** Mesma forma do snapshot do servidor, para a `SalaQuadra` consumir sem mudar. */
  snapshot() {
    const partida = projetarPartida(this.eventosDaPartida, { [ID_OPERADOR_LOCAL]: this.apelido });
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
   */
  async confirmar(novos, quadra = {}) {
    /** @type {Registro} */
    const proximo = {
      ...this.registro,
      quadra: { ...this.registro.quadra, ...quadra },
      eventos: [...this.registro.eventos, ...novos],
    };
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
