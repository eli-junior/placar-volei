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
