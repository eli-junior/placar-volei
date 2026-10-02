// @ts-check
/**
 * Casca Android (CV7.TS1). O APK abre a interface embarcada em
 * `https://localhost`; a quadra online é o próprio servidor, aberto pelo
 * WebView na mesma origem (cookies e WebSocket iguais ao navegador).
 */

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
 * Requisição de teste de conexão. No APK vai pela rede nativa (CapacitorHttp):
 * lê status e corpo sem depender de CORS, então distingue servidor no ar de um
 * 502 do túnel. Fora do APK (navegador, testes) usa `fetch`.
 * @param {string} url
 * @param {{ tempoMs: number }} opcoes
 * @returns {Promise<{ status: number, corpo: any }>}
 */
export async function requisitarPadrao(url, { tempoMs }) {
  const janela = /** @type {any} */ (globalThis.window);
  if (janela?.Capacitor?.getPlatform?.() === 'android') {
    const { CapacitorHttp } = await import('@capacitor/core');
    const resposta = await CapacitorHttp.get({ url, connectTimeout: tempoMs, readTimeout: tempoMs, headers: { 'Cache-Control': 'no-store' } });
    return { status: resposta.status, corpo: resposta.data };
  }
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), tempoMs);
  try {
    const resposta = await fetch(url, { cache: 'no-store', signal: controle.signal });
    return { status: resposta.status, corpo: await resposta.json().catch(() => null) };
  } finally {
    clearTimeout(limite);
  }
}

/**
 * O servidor está no ar? Só vale `200` com `status: ok` do `/health`: rede que
 * chega a um proxy com o backend fora (502) conta como indisponível, que é o
 * caso em que a quadra local entra em cena.
 * @param {string} origem
 * @param {{ requisitar?: typeof requisitarPadrao, tempoMs?: number }} [opcoes]
 */
export async function servidorDisponivel(origem, { requisitar = requisitarPadrao, tempoMs = 5000 } = {}) {
  let limite;
  try {
    const { status, corpo } = await Promise.race([
      requisitar(`${origem}/health`, { tempoMs }),
      new Promise((_, rejeitar) => { limite = setTimeout(() => rejeitar(new Error('tempo esgotado')), tempoMs + 500); }),
    ]);
    return status === 200 && corpo?.status === 'ok';
  } catch {
    return false;
  } finally {
    clearTimeout(limite);
  }
}

/**
 * O que a tela inicial do APK habilita (CV7.US1). A quadra local é o plano B
 * de quando não há comunicação com o servidor: só nasce sem ele. Uma quadra
 * local já existente e em andamento continua acessível, para a partida não
 * ficar presa no aparelho se a conexão voltar.
 * @param {{ servidor: 'testando' | 'disponivel' | 'indisponivel', configurado: boolean, local: { existe: boolean, emAndamento: boolean } }} entrada
 * @returns {{ online: boolean, local: boolean, acaoLocal: 'criar' | 'continuar', aviso: string | null }}
 */
export function modosDisponiveis({ servidor, configurado, local }) {
  const acaoLocal = local.existe ? 'continuar' : 'criar';
  const online = configurado && servidor === 'disponivel';
  const continuar = local.existe && local.emAndamento;
  // Testando: nada novo nasce ainda, mas a partida em andamento não espera o teste.
  if (servidor === 'testando' && configurado) return { online, local: continuar, acaoLocal, aviso: null };
  if (servidor === 'disponivel') {
    return {
      online,
      local: continuar,
      acaoLocal,
      aviso: continuar ? null : 'A quadra local só é usada quando não há conexão com o servidor.',
    };
  }
  return { online: false, local: true, acaoLocal, aviso: null };
}
