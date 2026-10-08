---
id: quadra-da-rodada-renovada-pelo-servidor
status: Decided
raised: 2026-10-08
decided: 2026-10-08
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS7.TS2
  - ponte-com-o-placar-e-sincronia
  - docs/qa/2026-10-08-furos-de-logica-joguinho.md
---

# Quadra da rodada renovada pelo servidor

## Question

O joguinho é durável e guarda o código de uma quadra do placar, que é efêmera (TTL de 1 h, banco apagado a cada start). Como impedir que a quadra suma no meio de uma rodada sem rever a decisão de 2026-09-27 (banco das quadras efêmero)?

## Decision

- **Banco das quadras continua efêmero** (opção (a) da decisão B de 2026-10-08, Navigator). A opção (b), banco em volume, foi rejeitada.
- **Batimento:** o servidor renova o `atualizado_em` da quadra vinculada a uma rodada `em_andamento`, na subida e a cada ciclo da limpeza (`min(300 s, TTL/2)`). A regra do TTL não muda; é a única exceção e mora em `ponte.manter_quadras_da_rodada`.
- **Reconciliação:** todo estado do joguinho limpa o vínculo com uma quadra que não existe mais. Com partida chamada o código fica, a tela mostra "indisponível — anule a partida" e, depois de anular, o vínculo é limpo.

## Rationale

O TTL é aplicado em cerca de 6 lugares (limpeza, listagem, comandos, relógio). Uma exceção em cada um espalharia a regra e acoplaria `quadras.py` ao `gerenciador.db`; renovar o carimbo mantém tudo igual e protege também o pareamento do relógio.

## Consequences

- Uma quadra protegida sobe na ordem de `/api/quadras` (ordenada por `atualizado_em`) mesmo sem ninguém tocar nela.
- A limpeza do vínculo não é publicada: os outros aparelhos a percebem na próxima leitura.
- `GET /api/sessao` pode escrever no `gerenciador.db`, só quando há vínculo morto.
- Reiniciar o contêiner ainda apaga a quadra e a partida do placar: a saída é anular a partida (US16).

Revisitar se o Navigator quiser recriar a quadra com as mesmas duplas (sugestão do QA F3) ou rever o banco efêmero.
