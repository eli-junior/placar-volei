---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-07
related:
  - CV8.DS3.US5
---

# CV8.DS3.US5 — painel da condução, chamar partida e sincronia entregues (0.35.0)

- **Entrega:** vínculo da sessão com a quadra do placar (criar ou por código), **Chamar partida** (servidor age como admin da quadra, recusa com pontos, nomes curtos, registro desfeito se o placar falhar), painel da condução (quadra, partida, fila, reis, eliminados) e sincronia entre aparelhos por `/ws/gerenciador` com `revisao` contra estado velho. Esquema 5 do `gerenciador.db`.
- **Achado de teste:** o nome da quadra criada ("Quadra da sessão") colidia com o botão "Sessão" nos seletores de navegador; virou "Quadra do dia" e os seletores passaram a ser exatos.
- **Achado de comportamento:** com a sincronia ao vivo a tela da sessão nunca fica desatualizada, então dois testes da US2 (aba desatualizada) foram reescritos; o recarregamento no 422 de reordenar fica só como reserva.
- **Achado de processo:** um `pkill -f` com o texto do próprio comando matou a minha shell (já havia nota de memória sobre isso); usar `ps | grep [p]attern` ou nada.
- **Evidência:** pytest 552 (33 novos), `npm test` 182, e2e 73 (axe incluído); validada pelo Navigator.
- **Dívidas abertas:** leitura do estado limpa quadras expiradas, difusão do estado completo, WebSocket não fecha ao trocar o segredo; agravadas: rotas da rodada em dois arquivos e `Sessao.svelte` com 346 linhas.
