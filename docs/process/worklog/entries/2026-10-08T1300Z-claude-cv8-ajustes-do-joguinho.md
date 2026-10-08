---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8
---

# Ajustes da tela "Novo joguinho" (0.46.0)

- **Pedido do Navigator:** slider de pontos 6–25, mensagem de mínimo por formato, "Gerenciar jogadores" no lugar do cadastro rápido e arrastar para ordenar a chegada. Validado no celular.
- **Migração schema 10:** o SQLite não altera CHECK; `_liberar_alvo_da_rodada` cria `rodadas_nova`, copia as colunas em comum, recria o índice `idx_rodada_ativa` e renomeia, numa transação. As chaves estrangeiras não estão ativas na conexão, então o drop é seguro.
- **Arrastar:** eventos de ponteiro na alça (`touch-action: none`); os centros dos itens são medidos ao começar o arrasto, para a lista não tremer. Grava ao soltar com `PUT /api/sessao/ordem`.
- **Armadilha:** o app abre a página do servidor, então o nome novo só aparece depois que o Mini PC atualiza e o cache do WebView renova.
- **Dívida:** endpoint `/presencas/rapido` sem uso; arrastar sem rolagem automática.
