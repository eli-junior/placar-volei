// Uma resposta HTTP atrasada nunca pode substituir um snapshot mais novo.
export function aceitarSnapshot(atual, recebido, partidaId) {
  if (!recebido || recebido.partida_id !== partidaId) return false;
  return !atual || recebido.seq >= atual.seq;
}
