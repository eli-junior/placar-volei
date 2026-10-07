# Plano — CV8.DS4.US11 Conduzir o mata-mata

Nível: User Story. Branch: `feature/cv8-ds4-us11-conduzir-o-mata-mata`. Versão-alvo: **0.38.0** (minor; backend, web e APK; Wear OS inalterado).

## Decisões do Navigator (Checkpoint 1, 2026-10-07)

1. **Quadra vazia no fim da fila** (último vencedor virou rei com a fila vazia): esse time é o **desafiante** e não entra na lista de rivais; enfrenta os outros reis na ordem de coroação. Se só ele for rei, é o campeão direto.
2. **Iniciar o mata-mata é manual** (botão); a partir dele ninguém mais entra.
3. **Partida única por confronto:** ganhou ficou, perdeu saiu (sem a regra de 2 vitórias virar rei).

## O que entra

- `app/conducao.py`: `derivar` ganha as fases `mata_mata` e `campeao`, o `desafiante`, os `rivais` e o `campeao`. Puro e determinístico; resultados do mata-mata vêm marcados com `fase`.
- Schema 7 (aditivo): `rodadas.mata_mata_em`, `rodadas.campeao_time_id`, `partidas_rodada.fase`.
- `POST /api/rodada/iniciar-mata-mata`: só no `fim_da_fila`; grava o início. Sem rivais, a rodada já tem campeão e se encerra.
- Chamar/encerrar partida reaproveitam o fluxo (em quadra = [vencedor atual, próximo rei]). Ao encerrar a última, `registrar_campeao` fecha a rodada (`encerrada`), o que libera o sorteio da próxima.
- Estado da sessão: `conducao.mata_mata`, `conducao.pode_iniciar_mata_mata`, `rodada.mata_mata_iniciado`, `ultimo_campeao`; histórico com `fase`.
- Painel: faixa do fim da fila com desafiante e rivais, botão **Iniciar mata-mata** (ou **Coroar campeão** sem reis), partidas do mata-mata marcadas no histórico, cartão **Campeões da rodada N**.

## Aceite (BDD)

- Dado o fim da fila, quando o operador inicia o mata-mata, então o desafiante joga contra o 1º rei, e quem vence segue contra o rei seguinte.
- Dado o fim da fila sem reis (ou só o desafiante-rei), então iniciar já coroa o campeão e encerra a rodada.
- Dado o fim da fila e o mata-mata não iniciado, então chamar partida é recusado; iniciado, ninguém mais entra (escalar parceiro é recusado).
- Dado o último confronto encerrado, então o campeão aparece nos dois aparelhos e o próximo sorteio é liberado.

## Fora do escopo

Desfazer partida (US7), atrasados (US9), substituição (US10), persistir sessão (US12), trio e histórico entre sessões.
