/**
 * Tela cheia do navegador (CV4.DS2.US2).
 *
 * Imersão (esconder os controles do app) e tela cheia (esconder a interface
 * do navegador) são estados independentes. Este módulo cuida só do segundo e
 * nunca afirma que a tela cheia entrou sem que o navegador confirme: o estado
 * exibido vem de `fullscreenElement`, lido de novo a cada `fullscreenchange`.
 *
 * O documento é injetável para permitir testes sem navegador. Prefixo
 * `webkit` cobre Safari de iPad e WebViews antigos.
 */

function doc(documento) {
  return documento ?? (typeof document === 'undefined' ? null : document);
}

export function suportaTelaCheia(documento) {
  const d = doc(documento);
  if (!d) return false;
  const raiz = d.documentElement;
  const habilitada = d.fullscreenEnabled ?? d.webkitFullscreenEnabled ?? false;
  return Boolean(habilitada && (raiz?.requestFullscreen || raiz?.webkitRequestFullscreen));
}

export function estaEmTelaCheia(documento) {
  const d = doc(documento);
  return Boolean(d && (d.fullscreenElement ?? d.webkitFullscreenElement));
}

/**
 * Precisa ser chamada de dentro do gesto do usuário (toque/clique), sem
 * `await` antes, senão o navegador recusa por falta de ativação.
 *
 * Solicita a raiz do documento para que os `<dialog>` modais (top layer)
 * continuem visíveis e operáveis durante a tela cheia.
 *
 * @returns {Promise<{ ok: boolean, motivo?: 'indisponivel' | 'recusada' }>}
 */
export async function solicitarTelaCheia(documento) {
  const d = doc(documento);
  if (!suportaTelaCheia(d)) return { ok: false, motivo: 'indisponivel' };
  const raiz = d.documentElement;
  try {
    if (raiz.requestFullscreen) {
      await raiz.requestFullscreen({ navigationUI: 'hide' });
    } else {
      await raiz.webkitRequestFullscreen();
    }
  } catch {
    return { ok: false, motivo: 'recusada' };
  }
  // A promise pode resolver sem que o navegador tenha de fato entrado.
  return estaEmTelaCheia(d) ? { ok: true } : { ok: false, motivo: 'recusada' };
}

export async function sairDaTelaCheia(documento) {
  const d = doc(documento);
  if (!estaEmTelaCheia(d)) return;
  try {
    await (d.exitFullscreen ? d.exitFullscreen() : d.webkitExitFullscreen?.());
  } catch {
    // Saída pelo sistema ou Esc já em curso: o evento atualiza o estado.
  }
}

/**
 * Observa entrada e saída, inclusive as provocadas por Esc, botão Voltar do
 * Android ou troca de app. Devolve a função de limpeza dos listeners.
 */
export function observarTelaCheia(aoMudar, documento) {
  const d = doc(documento);
  if (!d) return () => {};
  const tratar = () => aoMudar(estaEmTelaCheia(d));
  const eventos = ['fullscreenchange', 'webkitfullscreenchange', 'fullscreenerror', 'webkitfullscreenerror'];
  for (const nome of eventos) d.addEventListener(nome, tratar);
  return () => {
    for (const nome of eventos) d.removeEventListener(nome, tratar);
  };
}

/**
 * Os controles só voltam a se esconder quando nada exige a atenção deles:
 * nenhum diálogo aberto, nenhum controle com foco de teclado e nenhum erro
 * pendente de ação.
 */
export function podeOcultarControles({ modalAberto = false, focoDeTeclado = false, erroPendente = false } = {}) {
  return !modalAberto && !focoDeTeclado && !erroPendente;
}

export const MENSAGEM_TELA_CHEIA = {
  indisponivel: 'Tela cheia indisponível neste navegador. O placar continua nesta aba.',
  recusada: 'O navegador não permitiu a tela cheia. O placar continua nesta aba.',
};
