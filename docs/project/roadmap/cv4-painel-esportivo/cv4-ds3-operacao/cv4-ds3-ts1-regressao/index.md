---
code: CV4.DS3.TS1
level: Technical Story
status: Active
status_reason: Passo 5 - Checkpoint 3 (revisão) aguardando Navigator; V6 validada
updated: 2026-09-26
effort: 6
---

# CV4.DS3.TS1 — Regressão, acessibilidade e consolidação

## Intent / Scope

Entrega E6 — seção 11 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 6/10. Não equivale a prazo em dias.

## Dependências

Todas as US do CV4 aceitas; a cobertura incremental deve existir desde E1.

## Acceptance / Done Condition

Testes reproduzíveis e matriz física preenchida, sem falha crítica de corte, operação, contraste ou divergência; documentação e dívida coerentes com a evidência.

## Validation Route

Executar V6 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `feature/cv4-ds3-ts1-regressao`, criada de `master` `446282c`.
- Último checkpoint aprovado desta história: Checkpoint 2 (V6 validada; CI aprovado), 2026-09-26.
- Implementação: suíte de navegador concluída na branch; aguardando matriz física V6.
- Próxima ação: conferir dependências e apresentar/confirmar o Checkpoint 1 desta entrega.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.

## Decisões do Navigator (2026-09-26)

- Playwright e axe aprovados como ferramentas de teste de desenvolvimento, fora da imagem de runtime. Confirmar versões no início da implementação e registrar o comando definitivo em `web/package.json`, no guia de desenvolvimento e no test-guide.
- Validação física do tablet adiada da `CV4.DS2.US2` para a matriz desta história.
- Cenários de navegador já exercitados com scripts temporários nas US2 e DS3.US1 (ver dívida `fluxos-da-interface-sem-teste-de-ponta-a-ponta`) entram nesta suíte.
