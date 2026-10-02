// @ts-check
/**
 * Casca Android (CV7.TS1). O APK abre a interface embarcada em
 * `https://localhost`; a quadra online é o próprio servidor, aberto pelo
 * WebView na mesma origem (cookies e WebSocket iguais ao navegador).
 */

const CHAVE_SERVIDOR = 'placar.servidor';

/**
 * Verdadeiro só na interface embarcada do APK, não nas páginas do servidor
 * que o WebView abre depois.
 * @param {any} [janela]
 */
export function emCascaEmbarcada(janela = globalThis.window) {
  try {
    return Boolean(janela?.Capacitor?.isNativePlatform?.()) && janela.location.hostname === 'localhost';
  } catch {
    return false;
  }
}

/**
 * Aceita `placar.exemplo.com`, `https://placar.exemplo.com/` ou com caminho;
 * devolve a origem `https://…` ou `null` se não for um endereço válido.
 * HTTP só é aceito para rede local (IP privado ou `.local`), útil em teste.
 * @param {string} texto
 */
export function normalizarServidor(texto) {
  const bruto = String(texto ?? '').trim();
  if (!bruto) return null;
  let url;
  try {
    url = new URL(/^[a-z]+:\/\//i.test(bruto) ? bruto : `https://${bruto}`);
  } catch {
    return null;
  }
  if (url.protocol === 'https:') return url.origin;
  if (url.protocol === 'http:' && enderecoLocal(url.hostname)) return url.origin;
  return null;
}

/** @param {string} host */
function enderecoLocal(host) {
  return /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|127\.)/.test(host) || host.endsWith('.local');
}

/**
 * Testa se o servidor responde. Do WebView embarcado a chamada é de outra
 * origem, então `no-cors`: só importa se a rede chegou lá (resposta opaca) ou
 * não (rejeição, tempo esgotado).
 * @param {string} origem
 * @param {{ fetchFn?: typeof fetch, tempoMs?: number }} [opcoes]
 */
export async function servidorDisponivel(origem, { fetchFn = globalThis.fetch, tempoMs = 5000 } = {}) {
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), tempoMs);
  try {
    await fetchFn(`${origem}/health`, { mode: 'no-cors', cache: 'no-store', signal: controle.signal });
    return true;
  } catch {
    return false;
  } finally {
    clearTimeout(limite);
  }
}
