---
code: CV1.DS3.US1
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV1.DS3.US1: Configurar pontuação-alvo, vantagem e teto na criação da sala

Este guia estabelece os testes automatizados e o roteiro de validação multi-dispositivo do Navigator para a história `CV1.DS3.US1`.

---

## 1. Verificação Automatizada

Execute na raiz do projeto:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
npm --prefix web test
npm --prefix web run check
```

### Cobertura de Testes Automatizados (`tests/test_configurar_regras.py`)

1. **`test_criar_quadra_com_regras_personalizadas`**:
   - Criação via `POST /api/quadras` informando `alvo=15`, `vantagem=False`.
   - Verifica se o evento inicial `PARTIDA_INICIADA` foi gravado com `alvo=15`, `vantagem=False`.
   - Verifica se a linha do tempo inicial projeta: `"Partida iniciada até 15 pts"`.

2. **`test_vitoria_sem_vantagem_ao_atingir_alvo`**:
   - Quadra criada com `alvo=15` e `vantagem=False`.
   - Disputa atinge 14 × 14.
   - Ponto marcado para Equipe A (15 × 14).
   - Partida encerra formalmente com vitória da Equipe A e evento `PARTIDA_ENCERRADA`.

3. **`test_vitoria_com_teto_ao_atingir_teto`**:
   - Quadra criada com `alvo=12`, `vantagem=True`, `teto=15`.
   - Disputa em 11 × 11 -> ponto vai a 12 × 11 (não encerra por falta de 2 de vantagem).
   - Disputa chega a 14 × 14 -> ponto vai a 15 × 14.
   - Partida encerra com vitória no teto de 15 pontos!

4. **`test_rejeicao_teto_menor_que_alvo`**:
   - Tentativa de criar quadra com `alvo=15` e `teto=10`.
   - Servidor rejeita com HTTP 422: `"O teto da vantagem não pode ser menor que a pontuação-alvo."`.

5. **`test_regras_preservadas_no_reinicio`**:
   - Partida criada com `alvo=21` e `vantagem=False` é jogada até o encerramento.
   - Admin clica em iniciar nova partida (`POST /api/quadras/{id}/reiniciar`).
   - A nova partida inicia mantendo estritamente as regras da sala (`alvo=21`, `vantagem=False`).

---

## 2. Roteiro de Validação do Navigator (Multi-dispositivo com 2 clientes)

### Contexto de Validação
- **Cliente A**: Navegador comum (Admin criador da sala).
- **Cliente B**: Janela anônima ou celular (Espectador acompanhando o placar).

### Passo a Passo

#### 1. Iniciar a aplicação
No terminal:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Criar sala com regra personalizada (Sem vantagem)
- Acesse `http://localhost:8000`.
- No formulário **"Criar Placar"**:
  - Preencha os apelidos e jogadores.
  - Na seção **"Regras da Partida"**:
    - Selecione o botão rápido de pontuação-alvo: **`15`**.
    - Desmarque a opção **"Exigir vantagem de 2 pontos"**.
  - Clique em **"Criar Placar"**.
- Observe o código de 5 dígitos e o topo da sala exibindo: **`Até 15 pts • Sem vantagem`**.

#### 3. Conectar Cliente B
- Em janela anônima ou celular, acesse com o código da sala.
- Observe que para o espectador o topo também exibe com clareza: **`Até 15 pts • Sem vantagem`**.

#### 4. Validar encerramento no alvo exato (15 × 14)
- No **Cliente A**, marque pontos até o placar chegar em 14 × 14.
- Marque o 15º ponto para a Equipe A (15 × 14).
- **O que observar**:
  - A partida encerra imediatamente com vitória da Equipe A!
  - Banner de vitória aparece nas duas telas e os botões de ponto travam.

#### 5. Validar reinício preservando as regras
- No **Cliente A**, clique em **"▶ Iniciar Nova Partida"**.
- O placar zera para 0 × 0.
- As regras continuam vigentes: **`Até 15 pts • Sem vantagem`**.

#### 6. Validar prevenção de teto menor que alvo
- Volte para a tela inicial `http://localhost:8000` em outra aba.
- No formulário "Criar Placar", escolha alvo `15`, marque vantagem e digite teto `12`.
- **Condição de aprovação**: Um alerta de validação aparece abaixo do campo avisando que o teto não pode ser menor que o alvo, e o botão de criar placar fica desabilitado.

---

## 3. Critérios de Sucesso

- **Condição de Passagem**:
  - O criador escolhe as regras no formulário de criação com atalhos rápidos ou campos livres.
  - As regras ativas são exibidas para todos os participantes no cabeçalho da sala.
  - A partida encerra no momento exato estipulado pelas regras (com ou sem vantagem, ou no teto).
  - A reinicialização da partida preserva as regras originais da sala.
  - Tentativas com teto < alvo são bloqueadas no formulário e na API com HTTP 422.
- **Condição de Falha**:
  - Falha na aplicação das regras escolhidas na criação;
  - Desmarcar a vantagem não permitir vitória por 1 ponto de diferença;
  - Permitir criar sala com teto menor que o alvo;
  - Regras resetarem para 12 pontos ao reiniciar a partida.
