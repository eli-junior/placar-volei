// @ts-check
/** @typedef {import('./lib/tipos.js').Snapshot} Snapshot */

// Uma resposta HTTP atrasada nunca pode substituir um snapshot mais novo.
/**
 * @param {Snapshot | null} atual
 * @param {Snapshot | null | undefined} recebido
 * @param {string | null | undefined} partidaId
 */
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

/**
 * Corpo JSON da resposta, ou null quando não é JSON (CV5.DS3.US1). Um 502 do
 * túnel chega como HTML e, lido direto, vira "Unexpected token <" na tela.
 */
export async function lerJson(res) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

/** Sem mensagem do servidor por mais que isto, a conexão é tida como morta. */
export const SILENCIO_MAXIMO_MS = 45000;

/** O servidor manda PING a cada 20 s: silêncio longo é conexão meio aberta. */
export function conexaoSilenciosa(ultimaMensagem, agora = Date.now(), limite = SILENCIO_MAXIMO_MS) {
  return agora - ultimaMensagem > limite;
}
