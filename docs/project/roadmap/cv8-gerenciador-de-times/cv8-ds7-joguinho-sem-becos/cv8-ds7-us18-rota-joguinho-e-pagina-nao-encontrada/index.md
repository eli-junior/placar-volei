---
code: CV8.DS7.US18
level: User Story
status: Planned
status_reason: Maintenance curta; pode ir junto de outra história
updated: 2026-10-08
---

# Rota `/joguinho` e página não encontrada

## Intent

**Como** usuário, **quero** que o endereço da tela tenha o nome do produto e que um endereço errado diga que não existe, **para** não cair na home sem entender por quê (QA P3/P4).

## Acceptance

- **Dado** o botão "Joguinho" do topo **quando** tocado **então** a URL é `/joguinho`.
- **Dado** um favorito antigo `/sessao` **quando** aberto **então** vai para `/joguinho` (`replaceState`), sem quebrar.
- **Dado** um endereço que não existe (ex.: `/rota-inexistente`) **então** aparece "Página não encontrada" com um link para o início; o servidor segue devolvendo o SPA.
- **E** a API continua em `/api/sessao/*`.

## Onde

`web/src/App.svelte` (`carregarRota`, linhas da `telaSessao` e do `pushState('/sessao')`); e2e que abrem o Joguinho.
