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

/**
 * Extrai texto legível de qualquer forma que o backend use para descrever erro.
 * Existe porque o 422 padrão do FastAPI chega como lista de objetos e, jogado
 * direto na tela, vira "[object Object]".
 */
function extrairTexto(valor) {
  if (valor === null || valor === undefined) return '';
  if (typeof valor === 'string') return valor.trim();
  if (typeof valor === 'number' || typeof valor === 'boolean') return String(valor);
  if (Array.isArray(valor)) return valor.map(extrairTexto).filter(Boolean).join(' ');
  if (typeof valor === 'object') {
    const rotulo =
      valor.rotulo ||
      valor.campo ||
      (Array.isArray(valor.loc) ? valor.loc.filter(p => p !== 'body').join('.') : '');
    const mensagem = extrairTexto(valor.mensagem ?? valor.msg ?? valor.detail ?? valor.message);
    if (rotulo && mensagem) return `${rotulo} ${mensagem}`.trim();
    return mensagem;
  }
  return '';
}

/** Mensagem de erro sempre legível para a interface, nunca "[object Object]". */
export function mensagemDeErro(dados, alternativa = 'Não foi possível concluir a ação.') {
  const texto = extrairTexto(dados?.detail ?? dados?.detalhe ?? dados);
  return texto || alternativa;
}
