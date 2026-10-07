---
id: debt-corpo-da-foto-sem-teto-na-leitura
status: Carried
kind: security
severity: low
source: CV8.DS1.US15
revisit_trigger: A rota de foto ficar acessível a mais gente que o dono, ou o app ir para fora do túnel
closure_condition: Ler o corpo em pedaços e abortar ao passar de 256 KB
---

# Corpo da Foto sem Teto na Leitura

## Description

O servidor recusa pelo `Content-Length` anunciado, mas com envio em pedaços lê o corpo todo antes de checar os 256 KB.

## Carrying Reason

A rota exige o `OWNER_SECRET`; o risco é baixo no uso atual.

## Notes

Decisão: `docs/project/decisions/records/2026-10-07T2100Z-nota-nome-completo-e-foto-do-jogador.md`.
