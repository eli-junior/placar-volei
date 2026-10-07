// @ts-check
/**
 * Cliente da base de jogadores (CV8.DS1.US1). O servidor responde 404 para
 * segredo errado (mascara o endpoint); aqui isso vira "segredo recusado".
 */

export class ErroJogadores extends Error {
  /** @param {string} mensagem @param {number} status @param {string} [campo] */
  constructor(mensagem, status, campo) {
    super(mensagem);
    this.status = status;
    this.campo = campo;
  }
}

/**
 * @param {string} segredo
 * @param {string} caminho
 * @param {{ metodo?: string, corpo?: object }} [opcoes]
 * @param {typeof fetch} [buscar]
 */
export async function chamarJogadores(segredo, caminho, opcoes = {}, buscar = globalThis.fetch) {
  const { metodo = 'GET', corpo } = opcoes;
  const resposta = await buscar(`/api/jogadores${caminho}`, {
    method: metodo,
    headers: { 'x-owner-secret': segredo, ...(corpo ? { 'content-type': 'application/json' } : {}) },
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  if (resposta.ok) return resposta.json();
  if (resposta.status === 404) throw new ErroJogadores('Segredo recusado. Confira e tente de novo.', 404);
  if (resposta.status === 429) throw new ErroJogadores('Muitas tentativas incorretas. Aguarde um pouco.', 429);
  const dados = await resposta.json().catch(() => null);
  const detalhe = typeof dados?.detail === 'string' ? dados.detail : 'Não foi possível concluir.';
  throw new ErroJogadores(detalhe, resposta.status, dados?.erros?.[0]?.campo);
}

/** Ativos primeiro, depois inativos, em ordem alfabética sem acento. */
export function ordenarJogadores(lista) {
  const chave = (/** @type {string} */ n) => n.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  return [...lista].sort((a, b) => Number(b.ativo) - Number(a.ativo) || chave(a.nome).localeCompare(chave(b.nome)));
}
