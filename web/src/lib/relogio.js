/**
 * Regras de interface do relógio (CV3.DS1.US2).
 *
 * O relógio é pessoal do eli nesta fase. O filtro por nome decide só o que a
 * tela oferece: a permissão real é a habilitação no servidor (`watch_grants`).
 */

/** O participante é o eli, sem diferenciar maiúsculas nem espaços nas pontas. */
export function ehDonoDoRelogio(apelido) {
  return typeof apelido === 'string' && apelido.trim().toLowerCase() === 'eli';
}

/**
 * A chave "Controlar pelo Relógio" aparece para quem tem relógio vinculado e,
 * com ela ligada, também para o admin — que precisa poder desligá-la se o
 * relógio ficar sem bateria.
 */
export function mostrarChaveRelogio({ temRelogio, ligada, ehAdmin }) {
  return Boolean(temRelogio || (ligada && ehAdmin));
}
