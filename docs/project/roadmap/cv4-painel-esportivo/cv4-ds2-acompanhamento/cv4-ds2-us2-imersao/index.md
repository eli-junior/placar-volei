---
code: CV4.DS2.US2
level: User Story
status: Validated
status_reason: validada no Fold pelo Navigator; Checkpoint 3 aprovado; aguardando merge (Checkpoint 4)
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
- Implementação: concluída na branch; Checkpoints 1–3 aprovados em 2026-09-26.
- Próxima ação: Checkpoint 4 (merge em `master` como 0.16.0).

## Resultado e limitações

- Tela cheia solicita a raiz do documento no gesto e só é exibida quando o navegador confirma; recusa/indisponibilidade informa e mantém o placar na aba.
- Controles do espectador sobrepõem o palco: posição do placar idêntica antes/depois de revelar (360×640, 390×780, 1066×600, Chromium headless).
- Validação física: Fold aprovado pelo Navigator. **Tablet pendente**, coberto pela matriz física da CV4.DS3.TS1.
- Em telas estreitas, cabeçalho e presentes cobrem boa parte do placar enquanto visíveis (3 s). Aceito; revisitar na CV4.DS3.US2.
- O sistema pode manter barras de navegação; o produto não garante ocultação irrestrita.
- Próxima ação: conferir dependências e apresentar/confirmar o Checkpoint 1 desta entrega.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
