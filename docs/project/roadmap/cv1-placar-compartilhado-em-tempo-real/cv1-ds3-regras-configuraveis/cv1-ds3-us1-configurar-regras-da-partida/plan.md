# Plano de Implementação — CV1.DS3.US1: Configurar pontuação-alvo, vantagem e teto na criação da sala

## 1. Contexto e Intenção

Cada pelada joga com as regras que combinou antes de entrar em quadra: set até 12, 15, 21 ou 25 pontos, com ou sem exigência de vantagem de 2 pontos, e com ou sem teto da vantagem.

Conforme decisão de produto do Navigator (ADR `2026-09-15T1525Z-regras-da-partida-definidas-na-criacao-da-sala.md`), **as configurações da partida são definidas exclusivamente no início da jornada, na criação da sala**. Caso o grupo queira alterar as regras da pelada, cria-se uma nova sala com novo código PIN em poucos segundos.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV1.DS3.US1` dentro da Delivery Story `CV1.DS3 — Regras da partida configuráveis pela quadra`).
- **Branch**: `feature/cv1-ds3-us1-configurar-regras-da-partida` (criada a partir de `master`).

## 3. Escopo

1. **Backend**:
   - `app/api.py`:
     - Expandir `CriarQuadraBody` com:
       - `alvo: int = Field(default=12, ge=1, le=100, description="Pontuação-alvo para vitória")`
       - `vantagem: bool = Field(default=True, description="Exigência de 2 pontos de vantagem")`
       - `teto: int | None = Field(default=None, ge=1, le=200, description="Teto máximo de pontuação")`
     - Validação estrita: se `teto is not None and teto < alvo`, lançar `HTTPException(422, "O teto da vantagem não pode ser menor que a pontuação-alvo.")`.
     - Repassar `alvo`, `vantagem` e `teto` para `criar_quadra` e `criar_quadra_sync`.
   - `app/quadras.py`:
     - `criar_quadra_sync` e `criar_quadra`: receber e persistir os parâmetros `alvo`, `vantagem` e `teto` no payload do evento `PARTIDA_INICIADA`.
   - `app/projecao.py`:
     - Ajustar narrativa inicial da `Linha do Tempo`:
       - `descricao = f"Partida iniciada até {alvo} pts{desc_vantagem}{desc_teto}"` (exibindo teto quando presente).
   - `app/comandos.py`:
     - `reiniciar`: já preserva `alvo`, `vantagem` e `teto` da partida anterior na criação da nova partida.

2. **Frontend**:
   - `HomePlacar.svelte` (Formulário "Criar Placar"):
     - Seção estilizada e intuitiva: **"Regras da Partida"**.
     - Seleção de Pontuação-Alvo:
       - Botões de seleção rápida (pills): `12`, `15`, `21`, `25`.
       - Opção/campo numérico para valor personalizado.
     - Interruptor/Checkbox: "Exigir vantagem de 2 pontos" (marcado por padrão).
     - Campo numérico: "Teto da pontuação (opcional)" (habilitado apenas quando a vantagem está ligada).
     - Validação inline: se o usuário preencher um teto menor que o alvo, alertar visualmente e desabilitar o botão de criar até corrigir.
   - `SalaQuadra.svelte`:
     - Badge/resumo no topo da sala exibindo a regra vigente com clareza para todos os participantes (ex: `Até 15 pts • Vantagem • Teto 18` ou `Até 21 pts • Sem vantagem`).

3. **Testes Automatizados**:
   - `tests/test_configurar_regras.py` cobrindo:
     - Criação de quadra com regras customizadas (alvo 15, sem vantagem; alvo 21, com vantagem e teto 25).
     - Encerramento sem vantagem: 15 × 14 encerra imediatamente no alvo.
     - Encerramento com teto: 15 × 14 em jogo com teto 15 encerra imediatamente por teto atingido.
     - Rejeição na API com HTTP 422 quando `teto < alvo`.
     - Preservação das regras no reinício (`POST /reiniciar`).

## 4. Comportamento de Aceite (BDD)

```gherkin
Given a tela inicial "Criar Placar"
When o criador define a pontuação-alvo para 15 com vantagem de 2 e teto 18
Then a sala é criada com as regras configuradas e exibidas com destaque no cabeçalho
And a partida encerra no momento em que a condição configurada for atingida (15 com 2 de vantagem ou teto 18)
And quando a vantagem for desmarcada, a partida encerra no momento em que qualquer equipe atingir o alvo
And uma tentativa de criar sala com teto menor que a pontuação-alvo é rejeitada com mensagem clara no cliente e no servidor
And ao iniciar nova partida na mesma sala, as regras configuradas são preservadas.
```

## 5. Decisões de Design

- **Regras pertencem à sala**: definidas no momento de criação; se for necessário mudar, cria-se uma nova sala em menos de 10 segundos.
- **Formulário simples e rápido**: presets com 1 toque (12, 15, 21, 25) para que o criador não perca tempo configurando na beira da quadra.
- **Validação preventiva no cliente e punitiva no servidor**: a UI não permite submeter com erro e o backend garante a consistência com HTTP 422.

## 6. O que está Fora de Escopo

- Alteração dinâmica de regras durante a partida em andamento (superada pelo ADR de regras na criação).
- Sets múltiplos e tie-break formal.

## 7. Intenção de Versão

- **Minor (0.4.0)**: encerramento formal da Delivery Story `CV1.DS3 — Regras da partida configuráveis pela quadra`.
