---
code: CV7.TS2
level: Technical Story
status: Validated
status_reason: paridade validada pelo Navigator em 2026-10-02 (testes verdes e quebra proposital de regra nos dois lados)
updated: 2026-10-02
---

# CV7.TS2 — Regras e projeção em JS

## Intent

Ter em JS as regras da partida que hoje só existem no backend, com a garantia automática de que dão o mesmo resultado, para a quadra local do APK (CV7.US1) jogar sem servidor.

## Scope

- `web/src/lib/partida.js`: `avaliarVitoria`, `projetarEstado`, `projetarLinhaDoTempo`, `projetarPartida` e os comandos puros `iniciarPartida`, `marcarPonto`, `desfazerPonto`, `configurarPartida`, `reiniciarPartida`, com as mesmas recusas e status HTTP do servidor. Relógio e ids entram por um contexto, sem efeito colateral.
- `tests/paridade_fixtures.py` roda 9 logs montados à mão (inclusive governança e bordas) e 18 cenários pelo backend de verdade (10 fixos e 8 aleatórios com semente fixa) e grava `web/tests/fixtures/paridade.json`.
- `web/tests/paridade.test.js` refaz tudo em JS e exige estado, linha do tempo e recusa iguais.
- `tests/test_paridade_fixtures.py` falha se o JSON versionado não bate com o que o Python gera hoje.

## Acceptance / Done Condition

Given um log de eventos ou uma sequência de comandos
When o Python e o JS projetam o estado, a linha do tempo e o resultado de cada comando
Then os resultados são idênticos em todas as fixtures
And o JS recusa o que o servidor recusa, com o mesmo status

## Validation Route

`cd web && npm test` e `uv run pytest`. Para ver a paridade proteger: mude uma regra em um dos lados (por exemplo, a vantagem de 2 pontos em `partida.js`) e o teste correspondente falha; no Python, `test_paridade_fixtures` pede para regerar as fixtures e portar a mudança.

## Out of Scope

Papéis, versão de controle, presença, tema do placar, persistência e interface da quadra local (CV7.US1); ponte com o relógio (CV7.TS3). O `alvo_seq` do desfazer é coberto por um teste de unidade no JS, não pelas fixtures (a rota HTTP do site não o envia; só o relógio).

## Known Limits

Em payload malformado (por exemplo `alvo: "abc"`), o Python levanta erro e o JS produz `NaN`. Não ocorre, pois os eventos saem sempre dos comandos validados. Cerca de 25% dos passos dos cenários aleatórios esbarram em partida já encerrada; revisitar se uma regra nova passar sem o teste notar.
