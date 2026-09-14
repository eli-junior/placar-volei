---
code: CV1.DS1.US3
kind: test-guide
status: Active
updated: 2026-09-13
---

# Guia de Teste e Validação — CV1.DS1.US3 Desfazer ponto a ponto

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo para a história `CV1.DS1.US3`.

## 1. Verificação Automatizada

### Testes de Backend (`pytest`)
- `tests/test_desfazer.py`:
  - `test_desfazer_ponto_sucesso`:
    - Marca pontos para Equipe A e Equipe B (ex: 2x1).
    - Executa `POST /api/quadras/{id}/desfazer`.
    - Verifica que o placar volta para 2x0.
    - Executa novo desfazer -> volta para 1x0.
    - Executa novo desfazer -> volta para 0x0.
    - Verifica que nenhum evento foi apagado: o banco agora contém `PONTO_MARCADO` e `PONTO_DESFEITO` com `ref_seq` correspondente.
  - `test_desfazer_quando_zerado`:
    - Em um placar 0x0, tentar desfazer retorna HTTP 400 ("Nenhum ponto para desfazer").
  - `test_desfazer_reverte_fim_de_jogo`:
    - Marca 12 pontos para Time A (partida encerra com vitória de A).
    - Executa desfazer -> placar volta para 11x0, `encerrada` torna-se `False` e `vencedor` torna-se `None`.
  - `test_desfazer_sem_autenticacao`:
    - Chamada sem cookie ou sem participante registrado retorna 401/403.
  - `test_websocket_broadcast_desfazer`:
    - Conexão WebSocket recebe mensagem `PLACAR_ATUALIZADO` em tempo real ao desfazer um ponto.

### Testes de Frontend
- `npm run build` em `web/`: compilação limpa do Svelte 5.

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo)

### Preparação
1. Abra dois clientes (Navegador normal e aba anônima ou celular) na mesma quadra.
2. Ambos conectados e com status verde "Ao vivo".

### Passos de Teste

#### Passo 1: Botão Inativo em 0x0
- **Observação:** Com o placar em `0 × 0`, observe o botão "↺ Desfazer".
- **Condição de Aprovação:** O botão está visualmente desabilitado / inativo.

#### Passo 2: Desfazer Ponto Alternado
- **Ação:**
  1. No Cliente 1, marque ponto para Equipe A (`1 × 0`). O botão Desfazer torna-se ativo.
  2. Marque ponto para Equipe B (`1 × 1`).
  3. Toque em "Desfazer".
- **Observação esperada:**
  - Ambas as telas sincronizam instantaneamente de `1 × 1` para `1 × 0`.
  - O dígito da Equipe B reverte suavemente.
- **Condição de Aprovação:** Placar volta para `1 × 0` em ambas as telas.

#### Passo 3: Desfazer até Zerar
- **Ação:** Toque em "Desfazer" mais uma vez.
- **Observação esperada:**
  - O placar volta para `0 × 0`.
  - O botão "Desfazer" fica inativo novamente.
- **Condição de Aprovação:** Placar zerado e botão desabilitado.

#### Passo 4: Reversão de Vitória
- **Ação:**
  1. Marque 12 pontos para a Equipe A até aparecer o banner "🏆 Vitória da Equipe A" e os botões "+1" desabilitarem.
  2. Toque no botão "Desfazer".
- **Observação esperada:**
  - O placar volta para `11 × 0`.
  - O banner de vitória desaparece.
  - Os botões "+1" voltam a ficar habilitados para marcar pontos.
- **Condição de Aprovação:** Fim de jogo revertido perfeitamente.
