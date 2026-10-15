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
