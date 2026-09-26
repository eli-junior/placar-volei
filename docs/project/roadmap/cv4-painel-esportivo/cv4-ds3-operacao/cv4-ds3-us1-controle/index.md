---
code: CV4.DS3.US1
level: User Story
status: Done
status_reason: integrada em master como 0.17.0
updated: 2026-09-26
effort: 7
---

# CV4.DS3.US1 — Operação do admin e controlador

## Intent / Scope

Entrega E4 — seção 9 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 7/10. Não equivale a prazo em dias.

## Dependências

CV4.DS2.US1; sequência preferida após CV4.DS2.US2; composição do operador aprovada.

## Acceptance / Done Condition

Given posse do controle; When marcar ou desfazer; Then processar o comando uma vez e sincronizar; And participantes sem controle permanecem restritos pelo servidor.

## Validation Route

Executar V4 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `feature/cv4-ds3-us1-controle`, criada de `master` `446282c`.
- Último checkpoint aprovado desta história: Checkpoint 1 e composição do operador (E4.1, menu opção (a)) e Checkpoint 2 (V4), 2026-09-26.
- Implementação: concluída na branch; Checkpoints 1–3 aprovados em 2026-09-26.
- Checkpoint 4 aprovado; integrada pelo merge `8063c75` como 0.17.0.

## Resultado

- Composição aprovada: [proposta do operador](../../references/proposta-operador.html), menu ⋯ único (opção a).
- Barra compacta, faixa de posse separada do papel, +1 sob as equipes (laterais a partir de ~720 px) seguindo a inversão, Desfazer com o último ponto, presentes e passagem de controle no menu.
- Servidor inalterado; chamada forjada sem controle segue recusada (403).
- Dívida `representacao-classica-duplicada-na-operacao` paga.
- Selo de papel laranja na lista de presentes fica para a CV4.DS3.US2.
- Próxima ação: conferir dependências e apresentar/confirmar o Checkpoint 1 desta entrega.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
