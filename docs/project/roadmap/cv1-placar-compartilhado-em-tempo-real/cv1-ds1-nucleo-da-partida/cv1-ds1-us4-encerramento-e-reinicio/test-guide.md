---
code: CV1.DS1.US4
kind: test-guide
status: Active
updated: 2026-09-14
---

# Guia de Teste e Validação — CV1.DS1.US4 Encerramento da partida e reinício sob demanda

Este guia estabelece os testes automatizados e o roteiro de validação do Navigator para a história `CV1.DS1.US4`.

## 1. Verificação Automatizada

### Testes de Backend (`uv run pytest`)
- `tests/test_encerramento_e_reinicio.py`:
  - `test_vitoria_direta_e_partida_encerrada`:
    - Chegada a 12x10 grava `PARTIDA_ENCERRADA` no log imutável com vencedor "A".
    - Marca `partidas.status = 'ENCERRADA'` e preenche `encerrado_em`.
    - Bloqueia novas marcações de ponto após o encerramento com HTTP 400 ("A partida já está encerrada").
  - `test_vantagem_apos_empate_e_encerramento`:
    - Em 11x11, 12x11 não encerra pela exigência de 2 pontos de vantagem.
    - Em 12x12 e 13x12 a partida continua aberta.
    - Ao atingir 14x12 (2 pontos de vantagem), a partida encerra formalmente.
  - `test_desfazer_ponto_da_vitoria_reabre_partida`:
    - Em 12x10, acionar `POST /api/quadras/{id}/desfazer` reabre a partida para 11x10.
    - `partidas.status` volta a ser `EM_ANDAMENTO`, `encerrado_em` é limpo.
    - Botões de marcação voltam a aceitar novos pontos.
  - `test_reiniciar_partida_sob_demanda`:
    - Tentar reiniciar com a partida em andamento é rejeitado com HTTP 400.
    - Com a partida encerrada, chamar `POST /api/quadras/{id}/reiniciar`:
      - Arquiva a partida 1 como `ENCERRADA`.
      - Abre a partida 2 como `EM_ANDAMENTO` com o mesmo alvo, vantagem, teto e equipes.
      - O placar da quadra zera imediatamente para 0x0.
      - Uma chamada subsequente de reiniciar com a nova partida já em andamento retorna HTTP 400.
  - `test_encerramento_com_teto_atingido`:
    - Com alvo 12, vantagem de 2 e teto em 15, em 14x14 o ponto 15x14 encerra imediatamente a partida pelo teto.
  - `test_websocket_continuidade_ao_reiniciar`:
    - A conexão WebSocket permanece aberta durante o encerramento e o reinício da partida, recebendo a transição para 0x0 sem desconectar.

### Testes de Frontend
- `web/tests/sync.test.js`:
  - `aceita transição para nova partida na mesma sala`.
- Compilação Docker Multi-Stage (`docker build -t placar-volei-test .`):
  - Frontend Svelte 5 compila perfeitamente no build do contêiner.

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo)

### Preparação
1. No terminal, suba o backend:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Abra dois navegadores ou abas:
   - **Dispositivo 1 (Admin/Controlador):** Janela normal em `http://localhost:8000`. Crie um novo placar com o apelido "Admin". Observe o código de 5 dígitos da sala no topo (ex: `12345`).
   - **Dispositivo 2 (Espectador):** Janela anônima ou celular na mesma rede em `http://localhost:8000`. Clique em "Acompanhar", digite o código da sala e o apelido "Espectador".

---

### Passos de Teste

#### Passo 1: Encerramento com Vitória Direta (12x10)
- **Ação:**
  1. No Dispositivo 1, marque pontos até o placar chegar em `11 × 10`. Observe que a partida segue aberta nos dois dispositivos.
  2. No Dispositivo 1, marque o 12º ponto para a Equipe A (`12 × 10`).
- **O que observar:**
  - **Em ambos os dispositivos:** O banner comemorativo de fim de jogo aparece instantaneamente:
    `🏆 FIM DE JOGO! Vitória da Equipe A`
  - Os botões `+1` de marcação desaparecem/desabilitam.
  - **No Dispositivo 1 (Admin):** O botão destacado **"▶ Iniciar Nova Partida"** é exibido logo abaixo do banner. O botão *"↺ Desfazer Último Ponto"* permanece visível.
  - **No Dispositivo 2 (Espectador):** É exibida a mensagem: *"Aguardando início da próxima partida…"*.
- **Condição de Aprovação:** Ambas as telas anunciam a vitória da Equipe A, o placar trava em 12x10 e o botão "Iniciar Nova Partida" aparece para o admin.
- **Condição de Falha:** Placar não encerrar, botões +1 continuarem marcando além de 12 ou o botão de nova partida não aparecer.

#### Passo 2: Desfazer o Ponto da Vitória (Reabertura)
- **Ação:**
  1. Ainda com a partida encerrada em `12 × 10`, no Dispositivo 1, toque no botão *"↺ Desfazer Último Ponto"*.
- **O que observar:**
  - Em ambas as telas, o placar reverte suavemente de `12 × 10` para `11 × 10`.
  - O banner de vitória e o botão "Iniciar Nova Partida" desaparecem.
  - Os botões `+1` de marcação voltam a ficar habilitados para ambas as equipes.
- **Condição de Aprovação:** A vitória é desfeita e o jogo segue normalmente em 11x10.
- **Condição de Falha:** O placar não reverter ou continuar bloqueado como encerrado.

#### Passo 3: Reinício Sob Demanda para a Próxima Pelada
- **Ação:**
  1. No Dispositivo 1, marque novamente o ponto para a Equipe A (`12 × 10`), reencerrando a partida.
  2. No Dispositivo 1, clique no botão **"▶ Iniciar Nova Partida"**.
- **O que observar:**
  - Em ambas as telas, o placar zera instantaneamente para `0 × 0`.
  - O banner de vitória fecha e os botões `+1` de marcação voltam prontos para o novo jogo.
  - A sala (código PIN de 5 dígitos) e os participantes conectados permanecem exatamente os mesmos. Ninguém é desconectado.
  - Se abrir a "Linha do Tempo", a nova partida inicia limpa em `0 × 0` com o evento `#1 Início`.
- **Condição de Aprovação:** O placar reinicia em 0x0 sincronizado em ambos os clientes sem queda de conexão.
- **Condição de Falha:** Erro na tela, desconexão de WebSocket ou divergência de placar.
