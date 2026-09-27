// @ts-check
/**
 * Tema claro "Modo Sol" (CV5.DS5.TS1). Um lugar só para ler, aplicar e
 * guardar; `main.js` aplica antes de montar, então a tela não pisca escura
 * antes de ficar clara.
 */
export const CHAVE_TEMA = 'placar:tema';

/** @param {Storage | undefined} [armazenamento] */
export function lerTemaSol(armazenamento = globalThis.localStorage) {
  try {
    return armazenamento?.getItem(CHAVE_TEMA) === 'sol';
  } catch {
    return false;
  }
}

/** @param {boolean} sol @param {Document | undefined} [documento] */
export function aplicarTema(sol, documento = globalThis.document) {
  const raiz = documento?.documentElement;
  if (!raiz) return;
  if (sol) raiz.setAttribute('data-tema', 'sol');
  else raiz.removeAttribute('data-tema');
}

/** @param {boolean} sol @param {Storage | undefined} [armazenamento] */
export function guardarTema(sol, armazenamento = globalThis.localStorage) {
  try {
    armazenamento?.setItem(CHAVE_TEMA, sol ? 'sol' : 'padrao');
  } catch {
    /* navegação privada: vale só nesta visita */
  }
}
