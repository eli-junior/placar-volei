---
code: CV2.DS1.TS2
level: Technical Story
status: Validated
status_reason: implementada e testada, aguardando validação do Navigator
updated: 2026-09-15
related:
  - CV1.DS1.US1
  - docs/project/debt/items/2026-09-15T2205Z-lotacao-fantasma-por-presenca-nao-confiavel.md
---

# CV2.DS1.TS2 — Capacidade da quadra contada por presença efetiva

## Intent

Fazer o limite de participantes por quadra refletir quem está de fato na sala, para que a rotatividade natural de uma pelada (entra, fecha o navegador, entra de novo com outra sessão) pare de esgotar as vagas com gente que já foi embora.

## Scope

- `app/config.py`: nova configuração `presenca_ttl_seconds` (padrão 120), a janela de inatividade depois da qual um participante sem conexão ativa deixa de ocupar vaga.
- `app/quadras.py`: `contar_presentes()` e `limite_de_presenca()`; a checagem de capacidade em `registrar_participante_sync` passa a contar apenas quem tem conexão ativa no hub **ou** `ultimo_visto_em` dentro da janela.
- `app/quadras.py`: `registrar_participante()` recebe `ids_online` como parâmetro, injetado por quem chama.
- `app/api.py`: a rota `POST /api/quadras/{id}/entrar` lê `hub.participantes_online()` antes de entrar na transação e passa o conjunto adiante.
- Testes cobrindo sala genuinamente cheia, liberação após expiração dos fantasmas e prevalência da conexão ativa sobre um `ultimo_visto_em` velho.

## Acceptance / Done Condition

- Uma sala no limite volta a aceitar participantes assim que os ausentes saem da janela de presença.
- Uma sala com todo mundo presente continua recusando entrada com HTTP 400 e mensagem clara.
- Um participante com WebSocket aberto ocupa vaga mesmo que seu `ultimo_visto_em` esteja velho.
- O papel inicial (`ADMIN` para a sala vazia) continua decidido pelo total de registros, não pela presença: um fantasma expirado libera vaga, mas não promove o recém-chegado a administrador.
- Nenhum deadlock e nenhuma dependência do módulo de persistência para o módulo de transporte.

## Validation Route

1. Rodar o backend com `MAX_PARTICIPANTES_POR_QUADRA=2` e `PRESENCA_TTL_SECONDS=30` no `.env`.
2. Ocupar a sala com dois clientes e confirmar que um terceiro é recusado com mensagem legível.
3. Fechar as abas dos dois primeiros, esperar 30 segundos e confirmar que o terceiro entra.
4. Repetir com uma das abas aberta o tempo todo e confirmar que a vaga dela **não** é liberada.
5. `uv run pytest tests/test_blindagem_e_confiabilidade.py -k "fantasma or cheia or conexao_ativa"`.

## Out of Scope

- Expulsão automática ou remoção de registros de participantes ausentes do banco. A vaga é liberada; o histórico permanece, porque a linha do tempo referencia o autor dos eventos pelo `id`.
- Lista de presentes da UI: ela já distingue online de offline pelo hub e não mudou nesta story.
- Limite global de quadras (`max_quadras`), que continua por contagem de linhas — uma quadra expira por TTL próprio, não por presença.

## Notes

Classificada como Technical Story: o fluxo de entrada na sala é exatamente o mesmo para quem usa, e a mudança é a regra interna que decide se há vaga. A validação do Navigator existe, mas depende de baixar o limite por configuração — não é uma superfície nova.

A decisão de desenho que merece atenção está no `plan.md`: a presença é lida na borda assíncrona e injetada como valor na transação síncrona, em vez de a transação chamar o hub.
