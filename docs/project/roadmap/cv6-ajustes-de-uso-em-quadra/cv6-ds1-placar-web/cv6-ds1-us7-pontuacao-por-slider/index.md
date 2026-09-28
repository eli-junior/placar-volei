---
code: CV6.DS1.US7
level: User Story
status: Done
status_reason: validado e aceito pelo Navigator em 2026-09-28; entregue na 0.23.0
updated: 2026-09-28
---

# CV6.DS1.US7 — Pontuação por slider, topo curto e selo de papel

## Intent

Ajustar o alvo com um gesto só e liberar espaço no topo do operador, sem perder a informação da regra e do papel.

## Scope

- Alvo padrão 10 (API, projeção e web). Quadras existentes mantêm o alvo.
- Modal: slider de 6 a 20 com valor ao vivo; check **Personalizado** aceita inteiro de 1 a 100 e desabilita o slider. Alvo fora da faixa abre com Personalizado marcado.
- Topo: `10 pts · +2 · até 15` (alvo, vantagem, teto). Texto por extenso no `title` e no leitor de tela.
- Selo do papel vira caixinha igual à do ⚙ com Ⓐ (admin) ou Ⓒ (controlador); tocar mostra a dica. Espectador não tem faixa nem selo.

## Acceptance / Done Condition

Given sou admin numa quadra nova
When olho o topo
Then vejo `10 pts · +2` e a caixinha Ⓐ ao lado do ⚙
When toco na Ⓐ
Then aparece "Administrador da quadra" e some sozinho
When arrasto o slider até 15 e salvo
Then o topo mostra `15 pts · +2`
When marco Personalizado e digito 30
Then o slider fica desabilitado e o topo mostra `30 pts · +2` ao salvar

## Validation Route

`web/e2e/liberar-e-selo.spec.js` e `web/e2e/atalhos.spec.js`; Navigator validou no Fold.

## Out of Scope

Selo para o espectador; mudar o teto.
