---
date: 2026-09-14T18:15:00Z
author: Antigravity (Driver)
kind: milestone
related:
  - CV1.DS1.US4
  - CV1.DS1
verification:
  - pytest tests/test_encerramento_e_reinicio.py
  - docker build -t placar-volei-test .
  - validacao multi-dispositivo conforme test-guide.md
---

# Encerramento de Partida, Anúncio de Vitória e Reinício Sob Demanda (US4) e Fechamento da DS1

## What changed

- **Gravação Explícita do Evento `PARTIDA_ENCERRADA` no Log:**
  - O backend avalia a cada ponto a condição de vitória e grava atomicamente o evento append-only `PARTIDA_ENCERRADA` com identificação do vencedor, placar final e regras vigentes.
  - O registro da partida na tabela `partidas` é marcado como `status = 'ENCERRADA'` e `encerrado_em = <agora>`.
  - Novas tentativas de marcar pontos após o encerramento são bloqueadas com HTTP 400.

- **Reabertura por Desfazer Preservada:**
  - Caso o ponto da vitória tenha sido marcado por engano, acionar `desfazer` anula o match point via `PONTO_DESFEITO`, reabre a partida para 11x10 (`status = 'EM_ANDAMENTO'`, `encerrado_em = NULL`) e remove o anúncio de vitória, restaurando a capacidade de marcação de pontos.

- **Endpoint de Reinício Sob Demanda:**
  - Novo endpoint `POST /api/quadras/{quadra_id}/reiniciar`:
    - Permite ao controlador iniciar uma nova partida na mesma quadra quando a anterior for encerrada.
    - Preserva o histórico e o log auditável da partida encerrada.
    - Cria um novo registro em `partidas` (`status = 'EM_ANDAMENTO'`) e emite `PARTIDA_INICIADA` com a mesma configuração (alvo, vantagem, teto, equipes).
    - Propaga `PLACAR_ATUALIZADO` via WebSocket com o placar zerado em 0x0.

- **WebSocket Contínuo entre Partidas da Mesma Sala:**
  - O loop do WebSocket em `app/main.py` foi atualizado para não desconectar a conexão da sala quando `partida_id` for renovada, mantendo os participantes conectados e sincronizados para o próximo jogo.

- **Frontend Svelte 5:**
  - Anúncio de vitória em banner destacado com troféu, cores da equipe vencedora e mensagem clara de fim de jogo.
  - Botão destacado **"▶ Iniciar Nova Partida"** exibido para quem tem o controle da sala.
  - Para os espectadores, exibição de status informando que o jogo acabou e aguardando o início da próxima partida.
  - Botão *"↺ Desfazer Último Ponto"* acessível durante o anúncio para corrigir toques acidentais no match point.

- **Fechamento do Primeiro Arco de Entrega (`CV1.DS1`):**
  - Com a conclusão da `US4`, todas as histórias de `CV1.DS1` (`TS1`, `US1`, `US2`, `US3`, `US5`, `TS2`, `TS3`, `US4`) estão concluídas, validadas e testadas.

## Why it matters

- Permite conduzir uma rodada inteira de pelada (jogo após jogo) na mesma sala e com os mesmos participantes sem necessidade de criar novos links ou digitar novos PINs a cada fim de partida.
- Garante total rastreabilidade e histórico append-only de cada set jogado.
- Fecha o núcleo fundacional da partida em tempo real (`CV1.DS1`), habilitando o avanço para a gestão de permissões (`CV1.DS2`).

## Verification

- Suíte de testes automatizados com 71 testes passando (`uv run pytest`), incluindo 6 novos cenários cobrindo vitória direta, vantagem de 2, teto de 15 pontos, reversão por desfazer, reinício e WebSocket contínuo.
- Compilação Docker Multi-Stage validada com sucesso.
- Rota de validação multi-dispositivo executada e aprovada pelo Navigator no Checkpoint 2.
