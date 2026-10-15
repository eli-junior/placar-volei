// @ts-check
/**
 * Resenha do Joguinho (CV8.DS9.US25): textos da tela de estatísticas. Os
 * prêmios e números vêm prontos do servidor; aqui só se monta o que aparece.
 * Pura, sem DOM.
 */

/** @typedef {{ id: string, nome: string, genero?: string, tem_foto?: boolean }} JogadorResenha */

/**
 * "Ana", "Ana & Beto", "Ana, Beto e Caio".
 * @param {string[]} ids
 * @param {Record<string, JogadorResenha>} jogadores
 */
export function nomesDe(ids, jogadores) {
  const nomes = (ids ?? []).map((id) => jogadores?.[id]?.nome ?? '?');
  if (nomes.length <= 1) return nomes.join('');
  if (nomes.length === 2) return `${nomes[0]} & ${nomes[1]}`;
  return `${nomes.slice(0, -1).join(', ')} e ${nomes[nomes.length - 1]}`;
}

/**
 * Data do joguinho no fuso da quadra: "quarta, 15/10".
 * @param {string | null | undefined} abertaEm ISO em UTC
 */
export function dataDaResenha(abertaEm) {
  if (!abertaEm) return '';
  const data = new Date(abertaEm);
  if (Number.isNaN(data.getTime())) return '';
  const fuso = { timeZone: 'America/Sao_Paulo' };
  const dia = new Intl.DateTimeFormat('pt-BR', { ...fuso, weekday: 'long' }).format(data).replace('-feira', '');
  const ddmm = new Intl.DateTimeFormat('pt-BR', { ...fuso, day: '2-digit', month: '2-digit' }).format(data);
  return `${dia}, ${ddmm}`;
}

/**
 * A partida de um prêmio contada do lado de quem venceu.
 * @param {{ placar_a: number, placar_b: number, lado_a: string[], lado_b: string[] }} partida
 * @param {Record<string, JogadorResenha>} jogadores
 */
export function contarPartida(partida, jogadores) {
  const aVenceu = partida.placar_a > partida.placar_b;
  return {
    vencedores: nomesDe(aVenceu ? partida.lado_a : partida.lado_b, jogadores),
    perdedores: nomesDe(aVenceu ? partida.lado_b : partida.lado_a, jogadores),
    placar: `${Math.max(partida.placar_a, partida.placar_b)} x ${Math.min(partida.placar_a, partida.placar_b)}`,
  };
}

/** Saldo com sinal: "+12", "-3", "0". @param {number} n */
export function comSinal(n) {
  return n > 0 ? `+${n}` : String(n);
}

/**
 * Recorde curto do jogador na galeria: "4V · 2D · +12".
 * @param {{ vitorias: number, derrotas: number, saldo: number }} g
 */
export function recorde(g) {
  if (!g.vitorias && !g.derrotas) return 'não entrou em quadra';
  return `${g.vitorias}V · ${g.derrotas}D · ${comSinal(g.saldo)}`;
}

/** Quantos itens cabem em cada cartão 4:5 da Resenha. */
export const POR_CARTAO = { premios: 5, galeria: 6, tabela: 12 };

/**
 * Divide a lista em pedaços de `tamanho`.
 * @template T @param {T[]} lista @param {number} tamanho @returns {T[][]}
 */
export function emPedacos(lista, tamanho) {
  const pedacos = [];
  for (let i = 0; i < (lista?.length ?? 0); i += tamanho) pedacos.push(lista.slice(i, i + tamanho));
  return pedacos;
}

/**
 * Os cartões de tamanho fixo da Resenha, na ordem do print: capa (com o rei),
 * prêmios, galeria e tabela. Cada cartão vira uma imagem para o grupo.
 * @param {{ premios?: { id: string }[], galeria?: unknown[], tabela?: unknown[] }} dados
 * @returns {{ tipo: 'capa' | 'premios' | 'galeria' | 'tabela', itens: any[], parte: number, partes: number, numero: number, total: number }[]}
 */
export function montarCartoes(dados) {
  /** @type {{ tipo: any, itens: any[], parte: number, partes: number }[]} */
  const cartoes = [{ tipo: 'capa', itens: [], parte: 1, partes: 1 }];
  const grupos = /** @type {const} */ ([
    ['premios', (dados.premios ?? []).filter((p) => p.id !== 'rei')],
    ['galeria', dados.galeria ?? []],
    ['tabela', dados.tabela ?? []],
  ]);
  for (const [tipo, lista] of grupos) {
    const pedacos = emPedacos(lista, POR_CARTAO[tipo]);
    pedacos.forEach((itens, i) => cartoes.push({ tipo, itens, parte: i + 1, partes: pedacos.length }));
  }
  return cartoes.map((c, i) => ({ ...c, numero: i + 1, total: cartoes.length }));
}

/**
 * Nome do arquivo de cada cartão: "resenha-2026-10-14-1.png", com a data no
 * fuso da quadra.
 * @param {string | null | undefined} abertaEm @param {number} numero
 */
export function nomeDoArquivo(abertaEm, numero) {
  const data = abertaEm ? new Date(abertaEm) : null;
  const dia = data && !Number.isNaN(data.getTime())
    ? new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(data)
    : 'joguinho';
  return `resenha-${dia}-${numero}.png`;
}
