---
code: CV6.DS1.US1
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-27
updated: 2026-09-27
---

# CV6.DS1.US1 — Cabeçalho compacto e navegação visível

## Intent

Como participante, quero identificar a quadra e acessar as ações do topo rapidamente, para operar o placar sem ocupar espaço excessivo.

## Scope

- Reunir voltar, nome/número da quadra, configurações, inverter lados e status em uma linha.
- Tornar a seta de voltar visível e centralizada.
- Trocar a legenda “Ao vivo” por uma bolinha verde, amarela ou vermelha, mantendo descrição acessível do estado.

## Acceptance / Done Condition

- Dado tablet, Fold aberto ou fechado, quando abro a quadra, então o topo cabe sem sobreposição e a seta fica centralizada.
- Quando aciono inverter lados, então colunas e controles continuam associados à equipe correta.
- Quando muda a conexão, então o indicador representa o estado real e pode ser identificado por tecnologia assistiva.

## Validation Route

Comparar os três formatos nos dois temas; acionar voltar, ajustes e inversão; interromper a rede por 30 segundos e restaurar. Aprova se topo e comandos permanecem legíveis e o status acompanha a conexão; falha se houver cortes ou estado enganoso.

Aplicar também a [matriz comum](../../index.md#validação-comum). Este roteiro é para a futura implementação; não representa testes já executados.

## Out of Scope

Mudanças não descritas nesta HU, novas regras de jogo e alterações de permissões.

## Notes

Definir no planejamento a correspondência exata das três cores com os estados existentes; não reduzir alvos de toque para caber.

Origem: rodada de feedback do Navigator em 27/09/2026. Dependências técnicas, desenho final e versão serão definidos no checkpoint de planejamento da implementação.


## Entrega (2026-09-27)

- Topo em uma linha: ← · #código e nome · regras da partida · selo do papel · ⚙ (quem opera) · ⇄ · ⛶ (espectador) · ⋯ · status.
- Status em caixa de 44px no canto direito: verde pulsante (ao vivo), amarelo (reconectando), vermelho (aparelho sem rede, prevalece sobre o socket). Nome acessível "Conexão: …".
- Ajustes do Navigator na validação: status no canto e pulsante; "Você está no controle" substituído pelo resumo das regras (`resumirRegras`), antecipando a parte do operador da US4. A posse segue anunciada ao leitor de tela e o "Assumir" continua visível quando cabe.
- Abaixo de 600px a faixa de regras desce para a segunda linha e o nome da quadra some; os botões nunca encolhem.
- "Duplas e regras" saiu do menu ⋯ para o ⚙; ⇄ e ⋯ saíram de dentro do placar.
- Teste de axe passou a esperar animações finitas antes de medir contraste (falso positivo intermitente, também presente em `master`).
