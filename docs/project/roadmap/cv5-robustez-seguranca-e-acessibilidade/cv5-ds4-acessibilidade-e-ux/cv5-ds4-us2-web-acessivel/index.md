---
code: CV5.DS4.US2
level: User Story
status: Validated
status_reason: automode aprovado pelo Navigator em 2026-09-27; testes automatizados verdes
human_validation: pending
updated: 2026-09-27
---

# CV5.DS4.US2 — Web acessível

## Scope
- `@media (prefers-reduced-motion)` global em `app.css` para pulsos e giro.
- Regiões `aria-live` sempre montadas; o live da posse só em `.posse-texto` (`SalaQuadra.svelte:478,540`).
- Linha do Tempo migra para `Dialogo` (`LinhaDoTempo.svelte:48`).
- Erro do modal de apelido com `role="alert"` e `aria-describedby` (`ModalEntrar.svelte:71`).
- `aria-busy` só no botão que enviou; `aria-label` da próxima partida igual ao texto visível (`Placar.svelte:245,419`).
- Desfazer com pelo menos 48px em telas baixas (`Placar.svelte:692`).

## Acceptance
Com leitor de tela, a queda de conexão é anunciada; com movimento reduzido, nada pulsa; o foco não escapa da Linha do Tempo.

## Plano

[plan.md](plan.md) — branch `feature/cv5-ds4-us2-web-acessivel`.

## Revisão (Passo 5)

- **Feito:** a Linha do Tempo passou para o `Dialogo` (variante folha), sem o `svelte:window` do Esc. O `.controle-painel` fica sempre montado, com `.vazio`. A posse é anunciada num `sr-only` fora do `{#key}`, e o texto visual recebeu `aria-hidden`. `role="alert"`, `aria-invalid` e `aria-describedby` no apelido. `origemEnvio` para o `aria-busy`. O `aria-label` "Trocar Duplas" saiu. Desfazer com 48px. Bloco global de movimento reduzido em `app.css`. A bolinha de status ganhou `aria-hidden`.
- **Efeito visual:** o pulso de envio agora aparece só no botão tocado, não em todos.
- **Testes:** `svelte-check` sem erros nem avisos, testes `node --test` (5 novos em `acessibilidade.test.js`, 1 ajustado) e build verdes. O e2e com axe (Playwright) não rodou nesta sessão.
- **Débito novo:** nenhum.
- **Validação humana pendente:** com TalkBack ou NVDA, derrubar a rede e ouvir "Sem conexão"; passar o controle e ouvir só a posse. Com movimento reduzido no sistema, nada deve pulsar. Abrir a Linha do Tempo: o Tab fica dentro dela e, ao fechar, o foco volta ao botão.
