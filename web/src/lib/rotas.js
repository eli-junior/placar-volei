// @ts-check
/**
 * Rotas de tela do app (CV8.DS7.US18). O servidor devolve o SPA para qualquer
 * caminho fora de `/api/*`; é aqui que se decide o que existe. Pura, sem DOM.
 */

/**
 * @typedef {{ tela: 'inicio' | 'quadra' | 'joguinho' | 'jogadores' | 'nao_encontrada', quadraId?: string, canonico?: string }} Rota
 */

/**
 * @param {string} caminho `window.location.pathname`
 * @param {{ apk?: boolean }} [opcoes] no APK o Joguinho e os Jogadores não existem
 * @returns {Rota}
 */
export function resolverRota(caminho, { apk = false } = {}) {
  const limpo = caminho.length > 1 ? caminho.replace(/\/+$/, '') : caminho;
  if (limpo === '' || limpo === '/' || limpo === '/index.html') return { tela: 'inicio' };
  const sala = limpo.match(/^\/quadra\/([a-zA-Z0-9_-]+)$/);
  if (sala) return { tela: 'quadra', quadraId: sala[1] };
  if (apk) return { tela: 'nao_encontrada' };
  if (limpo === '/jogadores') return { tela: 'jogadores' };
  if (limpo === '/joguinho') return { tela: 'joguinho' };
  // Endereço antigo da tela do Joguinho: segue valendo, mas o canônico é /joguinho.
  if (limpo === '/sessao') return { tela: 'joguinho', canonico: '/joguinho' };
  return { tela: 'nao_encontrada' };
}
