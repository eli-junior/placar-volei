// @ts-check
/**
 * Ponte entre a quadra local e o relógio (CV7.TS3). O plugin nativo
 * `PlacarRelogio` só leva bytes pelo Data Layer; as regras ficam em
 * `QuadraLocal`. Cada lance do relógio vira um `aplicarComandoRelogio`, com a
 * resposta de volta ao relógio que o enviou, e o estado sai como DataItem a cada
 * mudança (inclusive as do próprio celular).
 *
 * Só vale com o JS vivo, isto é, com a tela do celular acesa (spike da TS3).
 */
import { ErroGravacao } from './quadraLocal.js';

/**
 * @typedef {Object} PluginRelogio
 * @property {(evento: 'comando' | 'ping', ouvinte: (e: any) => void) => Promise<{ remove: () => Promise<void> }>} addListener
 * @property {() => Promise<void>} iniciar
 * @property {() => Promise<void>} parar
 * @property {(args: { no: string, json: string }) => Promise<void>} responder
 * @property {(args: { json: string }) => Promise<void>} publicarEstado
 */

/** @type {PluginRelogio | null} */
let instancia = null;

/**
 * O plugin nativo dentro de `{ plugin }`, ou null fora do APK (navegador,
 * testes). Nunca devolva o proxy do plugin direto de uma função `async`: a
 * resolução da promessa chama `.then()` nele e o Capacitor responde "not
 * implemented". E `registerPlugin` só pode rodar uma vez por página.
 * @returns {Promise<{ plugin: PluginRelogio } | null>}
 */
export async function pluginRelogio() {
  const janela = /** @type {any} */ (globalThis.window);
  if (janela?.Capacitor?.getPlatform?.() !== 'android') return null;
  if (!instancia) {
    const { registerPlugin } = await import('@capacitor/core');
    instancia = /** @type {PluginRelogio} */ (registerPlugin('PlacarRelogio'));
  }
  return { plugin: instancia };
}

/**
 * @param {{ plugin: PluginRelogio, quadra: import('./quadraLocal.js').QuadraLocal, aoMudar?: (snapshot: any) => void }} opcoes
 */
/** Sinal de vida: o relógio trata a sala como fechada se ficar tanto tempo sem notícia (CV7.US2). */
export const INTERVALO_SINAL_MS = 20_000;

export function criarPonteRelogio({ plugin, quadra, aoMudar }) {
  /** @type {Array<{ remove: () => Promise<void> }>} */
  let ouvintes = [];
  /** @type {ReturnType<typeof setInterval> | null} */
  let sinal = null;
  let aberta = false;

  /** @param {string | null} [comandoId] */
  async function publicar(comandoId = null) {
    try {
      await plugin.publicarEstado({ json: JSON.stringify(quadra.snapshotParaRelogio(comandoId, aberta)) });
    } catch {
      // Sem relógio ao alcance: ele pega o último estado ao reconectar.
    }
  }

  /** @param {{ no: string, corpo: string }} lance */
  async function tratar({ no, corpo }) {
    /** @type {any} */
    let comando = null;
    try {
      comando = JSON.parse(corpo);
    } catch {}
    /** @type {object} */
    let resposta;
    try {
      resposta = comando ? await quadra.aplicarComandoRelogio(comando) : { status: 400, detail: 'Comando ilegível.' };
    } catch (e) {
      // 5xx: o relógio guarda o lance na fila e tenta de novo, sem descartar.
      resposta = e instanceof ErroGravacao ? { status: 503, detail: e.message } : { status: 400, detail: 'Comando ilegível.' };
    }
    try {
      // O `id` do lance vai em toda resposta: é por ele que o relógio a casa com o que enviou.
      await plugin.responder({ no, json: JSON.stringify({ id: typeof comando?.id === 'string' ? comando.id : null, ...resposta }) });
    } catch {
      // Relógio saiu do alcance: reenvia pelo mesmo id e recebe o mesmo recibo.
    }
    aoMudar?.(quadra.snapshot());
    await publicar();
  }

  return {
    publicar: () => publicar(),
    async iniciar() {
      aberta = true;
      ouvintes = [
        await plugin.addListener('comando', tratar),
        // O relógio que acabou de abrir pergunta pelo estado em vez de esperar o sinal de vida.
        await plugin.addListener('ping', () => { publicar(); }),
      ];
      await plugin.iniciar();
      await publicar();
      sinal = setInterval(() => { publicar(); }, INTERVALO_SINAL_MS);
      // Nos testes (Node) o intervalo não pode segurar o processo; no navegador não existe.
      /** @type {any} */ (sinal).unref?.();
    },
    async parar() {
      if (sinal) clearInterval(sinal);
      sinal = null;
      // Avisa o relógio de que a sala fechou, para ele voltar ao servidor já.
      aberta = false;
      await publicar();
      await Promise.all(ouvintes.map((o) => o.remove()));
      ouvintes = [];
      await plugin.parar();
    },
  };
}
