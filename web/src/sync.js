// Uma resposta HTTP atrasada nunca pode substituir um snapshot mais novo.
export function aceitarSnapshot(atual, recebido, partidaId) {
  if (!recebido) return false;
  // Se for uma nova partida na mesma quadra/sala, aceita a transição
  if (
    atual?.quadra?.id &&
    recebido.quadra?.id &&
    atual.quadra.id === recebido.quadra.id &&
    recebido.partida_id !== partidaId
  ) {
    return true;
  }
  if (recebido.partida_id !== partidaId) return false;
  return !atual || recebido.seq >= atual.seq;
}
