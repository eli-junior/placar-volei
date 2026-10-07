# Plano — CV8.DS1.US15 Nota, sobrenome e foto do jogador

Nível: User Story (estende a US1). Branch: `feature/cv8-ds1-us15-nota-sobrenome-e-foto`. Versão-alvo: **0.32.0** (minor; backend, web e APK por consistência de versão; Wear inalterado).

## Escopo

**Nota**
- Coluna `nota INTEGER NOT NULL DEFAULT 60` em `jogadores`, 1 a 100. Omitida no cadastro → 60.
- Fora da faixa, não inteira ou `true/false` → 422 no campo "Nota" ("deve ser um número de 1 a 100").
- Migração aditiva (`user_version` 1 → 2, `ALTER TABLE ... ADD COLUMN`): os jogadores da 0.31.0 ficam com 60, sem perder dados.

**Nome com ao menos 2 palavras**
- Mesmo campo `nome`; `"Ana"` → 422 "Nome deve ter nome e sobrenome". Vale para criar **e editar**.
- Quem já está na base com uma palavra continua listado e válido; só a edição exige completar. Reativar um inativo de uma palavra também é permitido (não reescreve o nome).
- Unicidade e limite de 40 caracteres como na US1.

**Foto**
- Botão **"Tirar foto"** no formulário: `<input type="file" accept="image/*" capture="environment">`. No celular abre a câmera traseira; no computador abre o seletor de arquivo. Sem permissão de câmera a tratar na página.
- O aparelho reduz a imagem (canvas, lado maior 480 px, JPEG qualidade 0,8, ~30–80 KB) e envia ao servidor. O servidor **aceita só JPEG** (confere os bytes iniciais) e até **256 KB**.
- Armazenamento: tabela `jogador_fotos (jogador_id PK, imagem BLOB, atualizado_em)` no **mesmo** `gerenciador.db` (volume já existente). Uma foto por jogador; trocar substitui; remover apaga.
- Rotas: `PUT /api/jogadores/{id}/foto` (corpo `image/jpeg` cru, sem dependência nova de multipart), `GET /api/jogadores/{id}/foto` (com `ETag`), `DELETE /api/jogadores/{id}/foto`. O JSON do jogador ganha `tem_foto`.
- Como o `<img>` não envia o cabeçalho `x-owner-secret`, a tela busca a foto com `fetch` e usa `URL.createObjectURL`.
- Cadastro novo: a foto tirada fica em pré-visualização; ao salvar, cria o jogador e então envia a foto. Se o envio falhar, o jogador fica criado e a tela avisa para tentar a foto de novo na edição.
- Lista: miniatura redonda (ou iniciais quando sem foto).

**Tela**: campo Nota (numérico, placeholder 60), botão de foto com pré-visualização e "Remover foto", nota e miniatura na lista. Continua protegida pelo `OWNER_SECRET` e oculta no APK.

## Aceite (BDD)

- Given o cadastro sem nota, When salvo "Ana Souza", Then a nota é 60.
- Given nota 0, 101, 7,5 ou "abc", When salvo, Then o campo Nota recusa e nada é gravado.
- Given o nome "Ana", When salvo (novo ou edição), Then é recusado por faltar sobrenome.
- Given jogadores da 0.31.0, When o servidor sobe com a 0.32.0, Then todos continuam com nota 60 e nenhum dado se perde.
- Given o botão de câmera, When tiro ou escolho uma foto e salvo, Then a miniatura aparece na lista e persiste após recarregar e após reiniciar o servidor.
- Given um arquivo que não é JPEG ou acima de 256 KB enviado direto à API, When envio, Then é recusado (422/413) e a foto anterior fica.
- Given a tela dentro do APK, Then continua oculta.

## Testes

- pytest: nota (padrão, limites, tipos), 2 palavras (criar, editar, legado), migração 1→2 com dados, foto (JPEG ok, não-JPEG, grande, ETag, trocar, remover, 404, sem segredo), persistência após reset.
- `npm test`: redução de imagem (cálculo de dimensões), cliente de foto.
- Playwright: cadastro com nota e foto (arquivo de teste via `setInputFiles`), erros de nota/nome, axe da tela.

## Alternativas rejeitadas

- **Arquivos em disco para as fotos:** dois lugares para fazer backup e manter coerentes; BLOB pequeno no mesmo SQLite é atômico e simples.
- **`multipart/form-data`:** exigiria `python-multipart` só para um arquivo; corpo cru basta.
- **Câmera ao vivo com `getUserMedia`:** mais código e permissões; o `capture` já resolve no celular.
- **Aceitar PNG/WebP/HEIC no servidor:** o aparelho já converte tudo para JPEG; menos superfície de validação.
- **Serviço público das fotos por URL fixa:** deixaria rostos acessíveis sem segredo.

## Fora do escopo

Uso da nota no sorteio (DS2), ajuste da nota pelo saldo (US-04), ordem de chegada (US-02), recorte/edição da foto, backup do volume (dívida já registrada).

## Riscos e observações

- **Foto é dado pessoal** guardado no servidor, atrás do segredo. Vale combinar com o grupo que as fotos ficam lá; não há exclusão em massa nesta história.
- **Câmera no navegador do celular exige HTTPS** (o túnel já fornece); em `http://` na LAN o `capture` ainda abre o seletor/câmera, mas pode variar por aparelho.
- Fotos aumentam o volume `gerenciador-dados` (centenas de KB no total para uma pelada).
