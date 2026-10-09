// @ts-check
/**
 * Regras de apresentação do Joguinho (CV8.DS7.US20), puras e sem DOM.
 */

/**
 * Joguinho aberto em dia anterior ao de hoje, pelo calendário do aparelho.
 * @param {string | null | undefined} abertaEm ISO de `sessao.aberta_em`
 * @param {Date} [agora]
 * @returns {{ dias: number, data: string, quando: string } | null} null se é de hoje ou a data é inválida
 */
export function joguinhoVelho(abertaEm, agora = new Date()) {
  if (!abertaEm) return null;
  const aberta = new Date(abertaEm);
  if (Number.isNaN(aberta.getTime())) return null;
  const dia = (/** @type {Date} */ d) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
  const dias = Math.round((dia(agora) - dia(aberta)) / 86_400_000);
  if (dias < 1) return null;
  const dd = String(aberta.getDate()).padStart(2, '0');
  const mm = String(aberta.getMonth() + 1).padStart(2, '0');
  return { dias, data: `${dd}/${mm}`, quando: dias === 1 ? 'ontem' : `há ${dias} dias` };
}

/** @param {number} n @param {string} um @param {string} varios */
const plural = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;

/**
 * O que se perde ao cancelar ou encerrar com a rodada ativa, em frases curtas
 * para a confirmação ("Perde-se: …").
 * @param {{ estado: string, numero: number }} rodada
 * @param {{ partidas_encerradas?: number, partida?: { time_a: number, time_b: number } | null, fila?: unknown[], reis?: unknown[] } | null | undefined} conducao
 * @returns {string[]}
 */
export function oQueSePerde(rodada, conducao) {
  if (rodada.estado === 'proposta') return [`a proposta ${rodada.numero} (os times sorteados)`];
  const itens = [];
  const registradas = conducao?.partidas_encerradas ?? 0;
  if (registradas > 0) itens.push(`${plural(registradas, 'partida registrada', 'partidas registradas')} (deixam de contar)`);
  if (conducao?.partida) itens.push(`a partida chamada, Time ${conducao.partida.time_a} × Time ${conducao.partida.time_b} (é anulada)`);
  const fila = conducao?.fila?.length ?? 0;
  if (fila > 0) itens.push(`a fila (${plural(fila, 'time', 'times')})`);
  const reis = conducao?.reis?.length ?? 0;
  if (reis > 0) itens.push(plural(reis, 'rei da quadra', 'reis da quadra'));
  return itens.length ? itens : [`a rodada ${rodada.numero}`];
}

/**
 * Efeito de retirar um jogador da rodada em andamento (CV8.DS7.US19), para a
 * confirmação: quais times ficam com vaga ou deixam de existir, e se ele está
 * em jogo (partida chamada), caso em que não pode sair.
 * @param {string} jogadorId
 * @param {{ em_quadra?: any[], fila?: any[], reis?: any[], eliminados?: any[], partida?: { time_a: number, time_b: number } | null } | null | undefined} conducao
 * @returns {{ emJogo: boolean, efeitos: string[] }}
 */
export function efeitoDaRetirada(jogadorId, conducao) {
  const times = [...(conducao?.em_quadra ?? []), ...(conducao?.fila ?? []), ...(conducao?.reis ?? [])];
  const vistos = new Set();
  const efeitos = [];
  let emJogo = false;
  for (const t of times) {
    if (vistos.has(t.fila) || !t.jogadores?.some((/** @type {{ id: string }} */ j) => j.id === jogadorId)) continue;
    vistos.add(t.fila);
    if (conducao?.partida && (conducao.partida.time_a === t.fila || conducao.partida.time_b === t.fila)) emJogo = true;
    efeitos.push(t.jogadores.length <= 1
      ? `o Time ${t.fila} deixa de existir`
      : `o Time ${t.fila} fica com a vaga aberta e escolhe o parceiro na vez dele`);
  }
  if (!efeitos.length && conducao?.eliminados?.some((/** @type {{ id: string }} */ j) => j.id === jogadorId)) {
    efeitos.push('ele sai da lista de escalação');
  }
  return { emJogo, efeitos };
}
