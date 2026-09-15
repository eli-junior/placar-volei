---
code: CV1.DS3.US2
level: User Story
status: Active
status_reason: puxada a pedido do Navigator para substituir nomes genéricos por jogadores e permitir inversão de perspectiva
updated: 2026-09-14
related:
  - CV1.DS3
  - CV1.DS1.US1
  - CV1.DS1.US2
---

# CV1.DS3.US2 — Nomes de jogadores nas equipes e inversão de lados na quadra

## Intent

Substituir os rótulos genéricos "Equipe A" e "Equipe B" pelos nomes reais dos atletas (1 ou 2 jogadores por time), e permitir que qualquer participante inverta os lados do placar para alinhar os cartões e botões com a perspectiva física de onde está posicionado na quadra.

## Scope

1. **Definição de Jogadores no Início da Partida**:
   - Campos na criação da quadra e no reinício de partida:
     - Time A: Jogador 1 (obrigatório), Jogador 2 (opcional).
     - Time B: Jogador 1 (obrigatório), Jogador 2 (opcional).
   - Formatação automática do nome da equipe: `"Jogador 1"` (dupla individual) ou `"Jogador 1 / Jogador 2"` (dupla completa).
   - Validação: pelo menos um jogador em cada equipe deve ser informado antes de iniciar.
   - Propagação no evento `PARTIDA_INICIADA` com os nomes reais das equipes e lista de jogadores.
2. **Inversão de Lados do Placar (Perspectiva Física do Usuário)**:
   - Botão `⇄ Inverter Lados` acessível diretamente na interface do placar (tanto no `Placar` do controlador quanto no `PlacarManual` do espectador).
   - Quando ativado: a equipe da esquerda vai para a direita e vice-versa, invertendo tanto os cartões de pontos quanto os botões de marcação `+1`.
   - Preferência mantida localmente (`localStorage`) por dispositivo para não afetar quem está assistindo do outro lado da rede.

## Acceptance / Done Condition

Given o formulário de criação de placar ou reinício de partida
When o criador informa "Eli" e "Beto" no Time 1 e "Carlos" no Time 2
Then a partida inicia com as equipes denominadas "Eli / Beto" e "Carlos"
And os botões de ponto, banners de vitória e registros na linha do tempo exibem esses nomes reais
And qualquer usuário pode clicar em "⇄ Inverter Lados" para que a coluna da esquerda e direita troquem de posição em sua tela, facilitando a operação conforme sua visão física da quadra
And a tentativa de criar uma sala sem preencher ao menos um jogador em cada equipe é bloqueada com mensagem clara.

## Validation Route

Criar partida informando jogadores em ambos os times. Conferir na tela do controlador e do espectador os nomes corretos. Marcar ponto e conferir linha do tempo. Clicar em "Inverter Lados" e conferir que cartões e botões trocam de lado perfeitamente.

## Out of Scope

Cadastro permanente de jogadores no banco, fotos de perfil, histórico estatístico por jogador entre salas.
