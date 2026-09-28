// @ts-check
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

/**
 * Equipe do ponto que o próximo "Desfazer" vai anular (CV4.DS3.US1).
 *
 * A linha do tempo é cronológica e pode atravessar partidas; o servidor só
 * desfaz pontos ativos da partida atual. Devolve `null` quando não há o que
 * desfazer, e o botão cai para o rótulo simples.
 */
export function ultimoPontoDesfazivel(itens = []) {
  for (let i = itens.length - 1; i >= 0; i -= 1) {
    const item = itens[i];
    if (item?.tipo === 'PARTIDA_INICIADA') return null;
    if (item?.tipo === 'PONTO_MARCADO' && !item.anulado) {
      return item.equipe === 'A' || item.equipe === 'B' ? item.equipe : null;
    }
  }
  return null;
}

/**
 * Texto da faixa de posse. Papel (quem pode) e posse (quem opera agora) são
 * coisas diferentes: um admin sem o controle não pontua até assumir.
 */
export function descreverPosse({ temControle, ehAdmin, operador, conectado = true }) {
  if (temControle) {
    return {
      titulo: 'Você está no controle',
      detalhe: conectado ? 'Seus toques valem para todos' : 'Sem conexão — os botões voltam sozinhos',
      podeAssumir: false,
    };
  }
  return {
    titulo: operador ? `Controle com ${operador}` : 'Controle sem operador',
    detalhe: ehAdmin ? 'Você é admin: toque em Assumir para pontuar' : 'Você é controlador: toque em Assumir para pontuar',
    podeAssumir: true,
  };
}

/**
 * Resumo das regras no topo do operador (CV6.DS1.US1, pedido do Navigator):
 * alvo, vantagem e teto, com os mesmos padrões do placar.
 * @param {{ alvo?: number, vantagem?: boolean, teto?: number | null } | null | undefined} estado
 */
export function resumirRegras(estado) {
  const partes = [`${estado?.alvo ?? 10} pontos`, (estado?.vantagem ?? true) ? 'Vantagem' : 'Sem vantagem'];
  if (estado?.teto) partes.push(`Teto ${estado.teto}`);
  return partes.join(' · ');
}

/**
 * Versão curta para o topo (CV6.DS1.US7): alvo, vantagem e o teto. Com espaço,
 * `longo` escreve "com vantagem"; sem espaço, a vantagem sai do texto e vira
 * o selo Ⓥ desenhado pelo topo.
 * O texto por extenso fica no `title` e no leitor de tela, com `resumirRegras`.
 * @param {{ alvo?: number, vantagem?: boolean, teto?: number | null } | null | undefined} estado
 * @param {boolean} [longo]
 */
export function resumirRegrasCurto(estado, longo = false) {
  let texto = `${estado?.alvo ?? 10} pts`;
  if (longo && (estado?.vantagem ?? true)) texto += ' com vantagem';
  if (estado?.teto) texto += ` · até ${estado.teto}`;
  return texto;
}
