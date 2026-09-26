---
code: CV4.DS3.US2
level: User Story
status: Active
status_reason: Passo 5 - Checkpoint 3 (revisão) aguardando Navigator; V5 validada
updated: 2026-09-26
effort: 5
---

# CV4.DS3.US2 — Superfícies auxiliares e estados coerentes

## Intent / Scope

Entrega E5 — seção 10 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 5/10. Não equivale a prazo em dias.

## Dependências

CV4.DS2.US2 e CV4.DS3.US1 aceitas e integradas.

## Acceptance / Done Condition

Given diálogo ou estado auxiliar; When abrir/fechar em qualquer tela; Then campos e ações ficam acessíveis e o foco retorna corretamente, preservando a partida.

## Validation Route

Executar V5 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `feature/cv4-ds3-us2-superficies`, criada de `master` `446282c`.
- Último checkpoint aprovado desta história: Checkpoint 2 (V5 validada, 2026-09-26).
- Implementação: concluída na branch; aguardando validação V5.
- Próxima ação: conferir dependências e apresentar/confirmar o Checkpoint 1 desta entrega.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
