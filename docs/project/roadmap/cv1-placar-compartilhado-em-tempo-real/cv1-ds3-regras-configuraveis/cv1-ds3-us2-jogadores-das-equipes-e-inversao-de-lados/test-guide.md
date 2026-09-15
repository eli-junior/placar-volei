# Roteiro de Validação Manual (Navigator) — CV1.DS3.US2

**História**: CV1.DS3.US2 — Jogadores das Equipes e Inversão de Lados  
**Branch**: `feature/cv1-ds3-us2-jogadores-das-equipes-e-inversao-de-lados`  
**Objetivo**: Validar a substituição de "Equipe A" e "Equipe B" pelo nome dos jogadores reais (1 ou 2 por time) no início da partida, e a capacidade de inverter os lados da quadra apenas no dispositivo/navegador local sem alterar a visão dos demais participantes.

---

## 1. Preparação do Ambiente

Inicie a aplicação via terminal:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Abra o navegador em `http://localhost:8000`.

---

## 2. Cenário 1 — Criação da Sala com Nomes dos Jogadores (Individual ou Duplas)

### Ação:
1. Na tela inicial ("Criar Placar"):
   - Preencha **Seu nome ou apelido**: `Eli`
   - Observe a seção **Jogadores das Equipes**:
     - No **Time A**: preencha `Carlos` no Jogador 1 (obrigatório). Deixe Jogador 2 vazio (ou preencha `Daniel`).
     - No **Time B**: preencha `Roberto` no Jogador 1 (obrigatório). Deixe Jogador 2 vazio (ou preencha `Eduardo`).
   - Observe que o botão **"Criar Placar e Iniciar"** só é habilitado quando ambos os Jogadores 1 estão preenchidos.
2. Clique em **"Criar Placar e Iniciar"**.

### Observações Esperadas:
- A sala é criada e aberta como Controlador/Admin.
- No placar, o cabeçalho das colunas não diz mais genericamente "Equipe A" / "Equipe B", mas sim os nomes dos jogadores inseridos:
  - Ex: `Carlos` (ou `Carlos / Daniel`) na esquerda e `Roberto` (ou `Roberto / Eduardo`) na direita.
- Os botões grandes de pontuação exibem:
  - `+1 Carlos` e `+1 Roberto`.
- Marque um ponto para o Time A: a **Linha do Tempo** registra `"Eli marcou para Carlos"`.

---

## 3. Cenário 2 — Inversão de Lados no Controlador

### Ação:
1. Na tela da quadra como Controlador, observe o botão **"⇄ Inverter Lados"** no cabeçalho do placar (ao lado de "Linha do Tempo") ou na barra superior.
2. Clique em **"⇄ Inverter Lados"**.

### Observações Esperadas:
- O botão fica destacado (estilo ativo, laranja com texto "Lados Invertidos").
- As colunas invertem de posição na tela:
  - O time `Roberto` passa para a coluna esquerda com seu respectivo botão `+1 Roberto`.
  - O time `Carlos` passa para a coluna direita com seu respectivo botão `+1 Carlos`.
- A pontuação e o histórico continuam corretos.
- Recarregue a página (F5): a preferência de inversão é mantida salva localmente (`localStorage`).
- Clique novamente em **"⇄ Inverter Lados"**: as colunas retornam à posição original.

---

## 4. Cenário 3 — Inversão Local (Independente entre Navegadores)

### Ação:
1. Copie o código de 5 dígitos da sala.
2. Abra uma **janela anônima** ou **outro navegador** (ou dispositivo no mesmo Wi-Fi).
3. Na tela inicial, acerte a aba "Acompanhar", insira o apelido `Torcedor` e o código da sala.
4. Na tela do espectador (janela anônima):
   - Toque na tela para revelar as opções e clique em **"⇄ Inverter Lados"** (no rodapé ou no topo).
5. Volte para a janela do Controlador (primeiro navegador).

### Observações Esperadas:
- Na janela anônima (espectador), os cartões manuais invertem de lado (`Roberto` na esquerda, `Carlos` na direita).
- **CRÍTICO**: Na janela do Controlador, os lados **NÃO se alteram**. A visualização do espectador permaneceu estritamente restrita ao navegador dele, sem propagação via WebSocket para os demais.

---

## 5. Critérios de Sucesso

- **Pass**:
  1. Nomes dos jogadores formatados corretamente nos placares, botões e linha do tempo.
  2. Validação bloqueia criação se Jogador 1 de qualquer time não for preenchido.
  3. Inversão de lados permuta as colunas e botões correspondentes sem erros de marcação.
  4. Inversão é 100% local (persistida em `localStorage`), não afetando outros navegadores/dispositivos conectados.
- **Fail**:
  - Exibição de "Equipe A" em vez dos nomes informados.
  - Inversão de lados em um navegador provocar a inversão em outro navegador.
  - Botão `+1` marcar para a equipe errada após a inversão.
