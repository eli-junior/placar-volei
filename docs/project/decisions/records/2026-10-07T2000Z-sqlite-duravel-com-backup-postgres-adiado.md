---
id: sqlite-duravel-com-backup-postgres-adiado
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.TS1
  - base-de-jogadores-duravel-e-protegida
  - debt-sem-backup-do-volume-de-jogadores
---

# SQLite Durável com Backup; Postgres Adiado

## Question

A base de jogadores (agora com notas e fotos) precisa de mais resiliência. Migrar para Postgres?

## Decision

- **Seguir com SQLite** (`gerenciador.db`, WAL, volume nomeado `gerenciador-dados`) como armazenamento durável do gerenciador.
- **A resiliência vem de backup**, não de troca de motor: história **CV8.TS1** (cópia consistente com a API de backup do SQLite, fora do volume, com retenção, verificação e restauração testada). Quita a dívida `sem-backup-do-volume-de-jogadores`.
- **Postgres fica adiado.** Reabrir esta decisão quando ocorrer qualquer um dos gatilhos:
  1. mais de um escritor simultâneo de verdade (vários servidores ou processos gravando);
  2. sessões, rodadas e partidas (DS2–DS4) crescerem a ponto de o arquivo ou as consultas de ranking pesarem;
  3. a necessidade de replicação, ou de o banco ficar fora do Mini PC.
- **A troca futura continua barata:** o `gerenciador.db` é isolado do banco das quadras e só `app/jogadores.py` fala com ele.

## Rationale

- O uso é de uma pelada: um escritor, dezenas de jogadores. O SQLite em WAL atende, e o risco real é perder o volume sem cópia — problema que o Postgres sem backup também teria.
- Postgres traria um contêiner a mais no Mini PC, credenciais, driver novo, migração dos dados e testes fora do SQLite, sem ganho hoje.

## Options Considered

- **Postgres agora:** custo operacional e de código sem necessidade presente.
- **Só confiar no volume:** mantém a dívida; qualquer perda do volume apaga o cadastro.
- **Backup na nuvem de imediato:** fora do escopo da TS1; pode ser história própria.
