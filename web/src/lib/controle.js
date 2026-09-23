/**
 * Passar o controle do placar (CV2.DS2.US5 no servidor; botão na CV3.DS1.US2).
 *
 * Só o admin passa, só para quem já é controlador ou admin, nunca para quem já
 * tem o controle, e só para quem está online — o servidor recusa o resto, e o
 * botão não oferece o que vai ser recusado.
 */
export function podePassarControle(participante, { euId, controleId, ehAdmin }) {
  return Boolean(
    ehAdmin &&
      participante &&
      participante.id !== euId &&
      participante.id !== controleId &&
      (participante.papel === 'CONTROLADOR' || participante.papel === 'ADMIN'),
  );
}
