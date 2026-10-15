// @ts-check
/**
 * Barras do Android (status e navegação) escondidas no modo de exibição do
 * placar. Só vale no APK: a ponte `window.PlacarBarras` (página do servidor) ou o
 * plugin nativo `BarrasDoSistema` (interface embutida) aplicam; no
 * navegador e nos testes tudo aqui é no-op.
 *
 * As chamadas entram numa fila: esconder e mostrar são assíncronos e, soltos,
 * podiam chegar fora de ordem (a sala os dispara ao montar e ao trocar de papel).
 */

/** @type {{ esconder: () => Promise<void>, mostrar: () => Promise<void> } | null} */
let instancia = null;
/** @type {Promise<unknown>} */
let fila = Promise.resolve();

/** @param {boolean} esconder */
async function aplicar(esconder) {
  const janela = /** @type {any} */ (globalThis.window);
  // Ponte própria do APK: vale também na página do servidor (quadra online), onde
  // o Capacitor não leva a ponte dos plugins.
  const ponte = janela?.PlacarBarras;
  if (ponte) {
    try {
      esconder ? ponte.esconder() : ponte.mostrar();
      return true;
    } catch (erro) {
      console.warn('[barras] ponte própria falhou', erro);
      return false;
    }
  }
  if (janela?.Capacitor?.getPlatform?.() !== 'android') return false;
  try {
    if (!instancia) {
      const { registerPlugin } = await import('@capacitor/core');
      instancia = registerPlugin('BarrasDoSistema');
    }
    await (esconder ? instancia.esconder() : instancia.mostrar());
    return true;
  } catch (erro) {
    // Sem as barras escondidas o placar continua usável; o aviso vai ao logcat.
    console.warn('[barras] não deu para', esconder ? 'esconder' : 'mostrar', erro);
    return false;
  }
}

/**
 * Esconde (`true`) ou mostra (`false`) as barras. Devolve se o plugin atendeu.
 * Nunca rejeita.
 * @param {boolean} esconder
 * @returns {Promise<boolean>}
 */
export function definirBarrasEscondidas(esconder) {
  const vez = fila.then(() => aplicar(esconder));
  fila = vez;
  return vez;
}
