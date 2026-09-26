---
code: CV4.DS2.US2
level: User Story
status: Active
status_reason: Passo 5 - Checkpoint 3 (revisão) aguardando Navigator; validado no Fold
updated: 2026-09-26
effort: 8
---

# CV4.DS2.US2 — Imersão estável e tela cheia real

## Intent / Scope

Entrega E3 — seção 8 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 8/10. Não equivale a prazo em dias.

## Dependências

CV4.DS2.US1 aceita e integrada.

## Acceptance / Done Condition

Given espectador; When solicitar tela cheia por toque; Then refletir o estado real do navegador, mantendo controles acessíveis e alternativa em caso de recusa.

## Validation Route

Executar V3 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `feature/cv4-ds2-us2-imersao`, criada de `master` `446282c`.
- Último checkpoint aprovado desta história: Checkpoint 2 (validado no Fold, 2026-09-26).
- Implementação: concluída na branch; aguardando validação física V3.
- Próxima ação: conferir dependências e apresentar/confirmar o Checkpoint 1 desta entrega.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
