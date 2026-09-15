---
id: debt-modais-ad-hoc-e-reconexao
status: Paying
kind: architecture
severity: low
source: CV1.DS4.US1
revisit_trigger: Criação de qualquer novo diálogo, ou queda de rede prolongada em uso real
closure_condition: Todos os diálogos sob a tag nativa <dialog> e reconexão de WebSocket com backoff exponencial e jitter
---

# Modais Ad-hoc Sem `<dialog>` e Reconexão de WebSocket Sem Backoff

## Description

Dois padrões de infraestrutura de interface replicados por cópia ao longo da `CV1`:

1. **Modais ad-hoc:** linha do tempo, criação de sala e entrada implementam sobreposição própria com `div` e `z-index`. Nenhum tem retenção de foco (focus trap), fechamento padronizado por `Esc` ou clique de backdrop. Cada novo diálogo recria o comportamento do zero, com variações.
2. **Reconexão sem disciplina:** a reconexão do WebSocket no frontend não aplica backoff exponencial nem jitter, e não há indicação visual discreta de restabelecimento da conexão.

## Carrying Reason

Ambos funcionam no caminho feliz e em rede local. O custo só aparece em escala (mais diálogos a manter) e em rede de quadra instável (tempestade de reconexão).

## Revisit Trigger

Novo diálogo na aplicação ou relato de reconexão agressiva em 4G.

## Closure Condition

Componente único de diálogo baseado em `<dialog>` nativo adotado por todos os modais, e cliente de socket com backoff exponencial, jitter e indicador de reconexão.

## Notes

Modais pagos por `CV2.DS4.US2`; reconexão paga por `CV2.DS2.TS1`.
