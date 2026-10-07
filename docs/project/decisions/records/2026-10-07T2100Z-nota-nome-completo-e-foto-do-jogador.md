---
id: nota-nome-completo-e-foto-do-jogador
status: Decided
raised: 2026-10-07
decided: 2026-10-07
deciders:
  - Eli (Navigator)
  - Claude Sonnet 5.5 (Driver)
related:
  - CV8.DS1.US15
  - base-de-jogadores-duravel-e-protegida
---

# Nota, Nome Completo e Foto do Jogador

## Question

Como registrar o nível, o sobrenome e a foto dos jogadores sem quebrar a base da 0.31.0?

## Decision

- **Nota:** inteiro de 1 a 100; vazio no cadastro vale 60; omitida na edição mantém a atual. Alimenta o sorteio equilibrado (RN-14).
- **Nome:** continua um campo só, mas exige ao menos 2 palavras (criar e editar). Nomes legados de uma palavra seguem válidos e listados; só a edição exige completar. Reativar não reescreve o nome.
- **Foto:** opcional, tirada na hora (`<input type=file capture=environment>`), reduzida no aparelho (lado maior 480 px, JPEG) e enviada por `PUT /api/jogadores/{id}/foto` com o corpo cru. O servidor aceita só JPEG de até 256 KB e a guarda como BLOB em `jogador_fotos`, no mesmo `gerenciador.db`. A tela baixa a foto por `fetch` com o segredo (o `<img>` não envia cabeçalho).
- **Migração:** aditiva (`user_version` 1→2, `ALTER TABLE ... ADD COLUMN nota ... DEFAULT 60`), idempotente, sem perda de dados.

## Rationale

- BLOB pequeno no mesmo SQLite é atômico e entra no mesmo backup; arquivos em disco criariam dois lugares para manter.
- Corpo cru evita a dependência de `multipart` para um único arquivo.
- Converter para JPEG no aparelho reduz a superfície de validação no servidor.

## Options Considered

- Fotos como arquivos em disco; `multipart/form-data`; câmera ao vivo com `getUserMedia`; aceitar PNG/WebP/HEIC no servidor; URL pública fixa das fotos (exporia rostos sem segredo).
