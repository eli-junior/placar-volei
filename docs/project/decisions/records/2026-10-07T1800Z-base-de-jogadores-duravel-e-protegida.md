---
id: base-de-jogadores-duravel-e-protegida
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS1.US1
  - apk-capacitor-e-quadra-local
---

# Base de Jogadores Durável e Protegida pelo OWNER_SECRET

## Question

Onde guardar o cadastro de jogadores (CA3: persistir entre reinícios) se o banco das quadras é efêmero por decisão de 2026-09-27, e quem pode escrever nele?

## Decision

- **Arquivo próprio:** a base mora em `gerenciador.db` (`GERENCIADOR_DB_PATH`), separado do banco das quadras. Nem `RESET_DB_ON_STARTUP` nem a mudança de schema das quadras o tocam; mudanças de schema nele são migrações aditivas (`PRAGMA user_version`).
- **Volume:** o compose monta o volume nomeado `gerenciador-dados` em `/data-gerenciador`. É o primeiro dado durável do projeto; o banco das quadras segue efêmero.
- **Acesso:** leitura e escrita exigem o `OWNER_SECRET` (cabeçalho `x-owner-secret`, com o rate limit existente). A tela guarda o segredo no aparelho, digitado uma vez.
- **APK:** a tela de jogadores não aparece em nenhuma página aberta dentro do APK (a base mora no servidor).
- **Nome único** só entre ativos, sem diferenciar caixa nem acento; inativar libera o nome; não há exclusão definitiva.

## Rationale

- Acoplar dados duráveis ao ciclo de dados descartáveis faria qualquer mudança de DDL das quadras ameaçar o cadastro.
- O `OWNER_SECRET` é a única proteção existente, e a base é persistente e exposta pelo túnel.

## Options Considered

- Mesmo banco das quadras poupando a tabela no reset: acopla os ciclos de vida.
- Tirar o reset do compose: reverte a decisão de 2026-09-27 e afeta quadras e relógio.
- Persistir no navegador: não sincroniza entre dispositivos (RN-12).
- Escrita aberta a quem tiver o link: coerente com a RN-12, mas expõe a base.
