---
code: CV4.DS1.US1
level: User Story
status: Validation
status_reason: Implementação concluída; verificações automatizadas e validação do Navigator em preparação
updated: 2026-09-26
effort: 6
---

# CV4.DS1.US1 — Home esportiva e entrada responsiva

## Intent / Scope

Entrega E1 — seção 6 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 6/10. Não equivale a prazo em dias.

## Dependências

Conferir origin/fix/entrar-na-quadra-pela-home; plano aprovado.

## Acceptance / Done Condition

Given Home em cliente novo ou com apelido salvo; When criar ou entrar; Then concluir ou informar erro visível junto à ação, nos dois temas e tamanhos suportados.

## Validation Route

Executar V1 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `codex/cv4-ds1-us1-home`, base `33534a5` (`origin/master`, versão 0.12.0).
- Último checkpoint aprovado: Checkpoint 1, pelo Navigator em 2026-09-26.
- Implementação: concluída, aguardando validação manual do Navigator no Checkpoint 2.
- Dependência conferida: `origin/fix/entrar-na-quadra-pela-home` registra o diagnóstico, sem patch de aplicação; a dívida na master será tratada nesta US.
- Próxima ação: seguir a rota de validação do Checkpoint 2 e registrar o retorno do Navigator.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
