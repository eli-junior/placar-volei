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
 * @property {(evento: 'comando', ouvinte: (e: { no: string, corpo: string }) => void) => Promise<{ remove: () => Promise<void> }>} addListener
 * @property {() => Promise<void>} iniciar
 * @property {() => Promise<void>} parar
 * @property {(args: { no: string, json: string }) => Promise<void>} responder
 * @property {(args: { json: string }) => Promise<void>} publicarEstado
 */

/** O plugin nativo, ou null fora do APK (navegador, testes). */
export async function pluginRelogio() {
  const janela = /** @type {any} */ (globalThis.window);
  if (janela?.Capacitor?.getPlatform?.() !== 'android') return null;
  const { registerPlugin } = await import('@capacitor/core');
  return /** @type {PluginRelogio} */ (registerPlugin('PlacarRelogio'));
}

/**
 * @param {{ plugin: PluginRelogio, quadra: import('./quadraLocal.js').QuadraLocal, aoMudar?: (snapshot: any) => void }} opcoes
 */
export function criarPonteRelogio({ plugin, quadra, aoMudar }) {
  /** @type {{ remove: () => Promise<void> } | null} */
  let ouvinte = null;

  async function publicar() {
    try {
      await plugin.publicarEstado({ json: JSON.stringify(quadra.snapshotParaRelogio()) });
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
    publicar,
    async iniciar() {
      ouvinte = await plugin.addListener('comando', tratar);
      await plugin.iniciar();
      await publicar();
    },
    async parar() {
      await ouvinte?.remove();
      ouvinte = null;
      await plugin.parar();
    },
  };
}
