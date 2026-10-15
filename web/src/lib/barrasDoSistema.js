// @ts-check
/**
 * Barras do Android (status e navegação) escondidas no modo de exibição do
 * placar. Só vale no APK: o plugin nativo `BarrasDoSistema` aplica; no
 * navegador e nos testes tudo aqui é no-op.
 */

/** @type {{ esconder: () => Promise<void>, mostrar: () => Promise<void> } | null} */
let instancia = null;

/**
 * Esconde (`true`) ou mostra (`false`) as barras. Devolve se havia plugin.
 * Nunca falha: sem as barras escondidas o placar continua usável.
 * @param {boolean} esconder
 * @returns {Promise<boolean>}
 */
export async function definirBarrasEscondidas(esconder) {
  const janela = /** @type {any} */ (globalThis.window);
  if (janela?.Capacitor?.getPlatform?.() !== 'android') return false;
  try {
    if (!instancia) {
      const { registerPlugin } = await import('@capacitor/core');
      instancia = registerPlugin('BarrasDoSistema');
    }
    // `{ plugin }` evita resolver o proxy do Capacitor como thenable.
    const { plugin } = { plugin: instancia };
    await (esconder ? plugin.esconder() : plugin.mostrar());
    return true;
  } catch {
    return false;
  }
}
