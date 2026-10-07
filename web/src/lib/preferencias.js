// @ts-check
/**
 * Apelido lembrado entre a Home e a entrada por link (CV5.DS4.US3). Antes,
 * cada tela usava uma chave e uma não enxergava o que a outra guardou.
 */
export const CHAVE_APELIDO = 'placar:apelido';
const CHAVE_APELIDO_ANTIGA = 'placar_ultimo_apelido';

export function lerApelido(armazenamento = globalThis.localStorage) {
  try {
    const atual = armazenamento?.getItem(CHAVE_APELIDO);
    if (atual) return atual;
    const antigo = armazenamento?.getItem(CHAVE_APELIDO_ANTIGA);
    if (antigo) {
      armazenamento.setItem(CHAVE_APELIDO, antigo);
      armazenamento.removeItem(CHAVE_APELIDO_ANTIGA);
    }
    return antigo || '';
  } catch {
    return '';
  }
}

export function guardarApelido(apelido, armazenamento = globalThis.localStorage) {
  try {
    armazenamento?.setItem(CHAVE_APELIDO, apelido);
  } catch {
    /* navegação privada: segue sem lembrar */
  }
}

const PAPEIS = { ADMIN: 'Admin', CONTROLADOR: 'Controlador', ESPECTADOR: 'Espectador' };

/** Papel legível no selo da sala, em vez do código cru do servidor. */
export function nomeDoPapel(papel) {
  return PAPEIS[papel] || '';
}

const SELOS = {
  ADMIN: { letra: 'A', dica: 'Administrador da quadra' },
  CONTROLADOR: { letra: 'C', dica: 'Controlador do placar' },
};

/** Selo curto do topo (CV6.DS1.US7): letra circulada e a dica ao tocar. */
export function seloDoPapel(papel) {
  return SELOS[papel] || null;
}

/**
 * Tamanho dos números do placar, só neste aparelho (CV6.DS1.US3).
 */
export const CHAVE_TAMANHO_NUMEROS = 'placar:tamanho_numeros';
// P é o tamanho de antes da US3; M e G crescem até o limite da coluna.
export const TAMANHOS_NUMEROS = { P: 1, M: 1.25, G: 1.5 };

export function lerTamanhoNumeros(armazenamento = globalThis.localStorage) {
  try {
    const valor = armazenamento?.getItem(CHAVE_TAMANHO_NUMEROS);
    return valor && valor in TAMANHOS_NUMEROS ? valor : 'M';
  } catch {
    return 'M';
  }
}

export function guardarTamanhoNumeros(tamanho, armazenamento = globalThis.localStorage) {
  try {
    armazenamento?.setItem(CHAVE_TAMANHO_NUMEROS, tamanho);
  } catch {
    /* navegação privada: vale só até recarregar */
  }
}

/** Próximo da sequência P → M → G → P, para o item do menu. */
export function proximoTamanhoNumeros(atual) {
  return { P: 'M', M: 'G', G: 'P' }[atual] || 'M';
}

/** Segredo do dono, digitado uma vez neste aparelho (CV8.DS1.US1). */
export const CHAVE_SEGREDO_DONO = 'placar:segredo_dono';

export function lerSegredoDono(armazenamento = globalThis.localStorage) {
  try {
    return armazenamento?.getItem(CHAVE_SEGREDO_DONO) || '';
  } catch {
    return '';
  }
}

export function guardarSegredoDono(segredo, armazenamento = globalThis.localStorage) {
  try {
    if (segredo) armazenamento?.setItem(CHAVE_SEGREDO_DONO, segredo);
    else armazenamento?.removeItem(CHAVE_SEGREDO_DONO);
  } catch {
    /* navegação privada: vale só até recarregar */
  }
}
