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
