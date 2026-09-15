# Plano de Implementação — CV1.DS3.US2: Nomes de jogadores nas equipes e inversão de lados

## 1. Contexto e Intenção

Na prática de vôlei ou beach tennis, os participantes preferem ver o nome dos jogadores reais que estão na disputa em vez de "Equipe A" e "Equipe B". Além disso, quem está operando o placar ou assistindo pode estar sentado do lado esquerdo ou direito da quadra, o que faz com que o placar na tela pareça invertido em relação à posição física dos atletas.

Esta história atende a essas duas necessidades:
1. No início do jogo, permite definir 1 ou 2 jogadores por time (sendo obrigatório pelo menos 1 jogador por equipe).
2. Fornece um botão de fácil acesso para inverter visualmente os lados da quadra na tela do usuário.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV1.DS3.US2` dentro de `CV1.DS3 — Regras da partida configuráveis pela quadra`).
- **Branch**: `feature/cv1-ds3-us2-jogadores-das-equipes-e-inversao-de-lados` criada a partir de `master`.

## 3. Escopo

1. **Backend**:
   - Atualização de `CriarQuadraBody` e `criar_quadra` para aceitar:
     - `time_a_jogador1` (str, opcional no schema para manter compatibilidade com testes legados, mas validado quando fornecido)
     - `time_a_jogador2` (str, opcional)
     - `time_b_jogador1` (str, opcional)
     - `time_b_jogador2` (str, opcional)
   - Lógica de composição de nomes:
     - Se `time_a_jogador1` for informado: `equipe_a = f"{j1} / {j2}"` se houver `j2`, senão `f"{j1}"`.
     - Caso não seja informado (fallback para testes antigos), mantém `"Equipe A"` e `"Equipe B"`.
     - Gravação no payload de `PARTIDA_INICIADA` dos campos `equipe_a`, `equipe_b`, `jogadores_a` e `jogadores_b`.
   - Suporte similar em `POST /api/quadras/{id}/reiniciar` com body opcional para atualizar os nomes dos atletas na nova partida se houver troca de time.
2. **Frontend**:
   - `HomePlacar.svelte`:
     - Na aba "Criar Placar":
       - Seção destacada: **Equipes e Atletas**.
       - Time 1: Campo "Jogador 1" (obrigatório) e "Jogador 2" (opcional).
       - Time 2: Campo "Jogador 1" (obrigatório) e "Jogador 2" (opcional).
       - Validação no frontend: impede a submissão se Jogador 1 de qualquer um dos times estiver vazio.
   - `SalaQuadra.svelte`, `Placar.svelte` e `PlacarManual.svelte`:
     - Botão `⇄ Inverter Lados` posicionado no cabeçalho/barra superior do placar.
     - Estado local reativo `ladosInvertidos` (persistido no `localStorage` por sala).
     - Quando `ladosInvertidos = true`:
       - No `Placar.svelte`: o time da esquerda e o time da direita trocam de posição visual, inclusive seus botões de marcar ponto (`+1`), permitindo marcar no time à esquerda física com o polegar esquerdo.
       - No `PlacarManual.svelte`: os cartões dobráveis trocam de lado de forma correspondente.
3. **Testes Automatizados**:
   - Criação de sala com jogadores individuais e duplas.
   - Validação da formação de nomes ("Eli / Beto" e "Carlos").
   - Teste de consistência na linha do tempo e anúncio de vitória.

## 4. Comportamento de Aceite (BDD)

```gherkin
Given o formulário de criação de placar
When o criador informa "Eli" e "Beto" no Time 1 e "Carlos" no Time 2
Then o placar inicia com as equipes denominadas "Eli / Beto" e "Carlos"
And os botões de ponto, banners e linha do tempo exibem esses nomes reais
And ao acionar o botão "⇄ Inverter Lados", a ordem visual das colunas inverte imediatamente
And a preferência de lado é mantida localmente para o dispositivo sem afetar outros participantes conectados.
```

## 5. Intenção de Versão

- **Minor**: nova capacidade funcional (`0.4.0` ou `0.3.2`).
