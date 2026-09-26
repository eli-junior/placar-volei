---
code: CV4.DS1.US1
level: User Story
status: Done
status_reason: implementação, validação e revisão aprovadas pelo Navigator em 2026-09-26
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

## Resultado entregue

- Entrada por código é a ação inicial; criação permanece disponível na aba vizinha.
- Computador e Fold aberto aproveitam duas colunas; larguras menores empilham acesso e partidas.
- Cards ativos separam informações, placar central dominante e ação **Abrir** em coluna inteira.
- Tema claro/escuro é identificado por texto; fonte Teko local usa peso 600 nos números.
- Recusas de entrada aparecem no formulário com código preservado e foco devolvido ao apelido.
- Navigator aprovou a composição após validação iterativa em `http://localhost:5173/`.

## Evidência

- `uv run pytest`: 185 aprovados.
- `npm test`: 31 aprovados.
- `npm run check`: zero erros e zero advertências.
- `npm run build`: concluído.
- `uv run ruff check .` e `uv run ruff format --check .`: aprovados.
- Inspeção visual em 658, 904 e 1440 px, com dados reais isolados e sala ativa.

## Estado para retomada

- Branch de implementação: `codex/cv4-ds1-us1-home`, base `33534a5` (`origin/master`, versão 0.12.0).
- Último checkpoint aprovado: Checkpoint 1, pelo Navigator em 2026-09-26.
- Implementação, validação manual e revisão: concluídas; Checkpoints 2 e 3 aprovados pelo Navigator em 2026-09-26.
- Dependência conferida: `origin/fix/entrar-na-quadra-pela-home` registra o diagnóstico, sem patch de aplicação; a dívida na master será tratada nesta US.
- Checkpoint 4 aprovado em 2026-09-26; integração em `master` autorizada.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
