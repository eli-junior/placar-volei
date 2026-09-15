# Plano de Implementação — CV1.DS3.US1: Configurar pontuação-alvo, vantagem e teto

## 1. Contexto e Intenção

Cada grupo joga com a regra combinada na hora: set até 12, 15, 21 ou 25 pontos, com ou sem exigência de vantagem de 2 pontos e com ou sem teto de pontuação.

Esta história permite que o administrador da sala — ou qualquer controlador quando o posto de administrador estiver vago — ajuste as regras da partida diretamente na interface, a qualquer momento (inclusive com a partida em andamento):
- O ajuste gera o evento auditável `REGRA_ALTERADA` no log append-only.
- A alteração fica registrada de forma transparente na Linha do Tempo para todos os presentes.
- O motor de desfecho reage imediatamente às novas regras para encerramento de partida.
- Valores inconsistentes (como teto menor que a pontuação-alvo) são validados e rejeitados no cliente e no servidor com mensagem clara.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV1.DS3.US1` dentro da Delivery Story `CV1.DS3 — Regras da partida configuráveis pela quadra`).
- **Branch**: `feature/cv1-ds3-us1-configurar-regras-da-partida` (criada a partir de `master`).

## 3. Escopo

1. **Backend**:
   - `app/comandos.py`:
     - Nova ação `regras` em `executar_sync`:
       - Autorização: permitida para `ADMIN`; ou para `CONTROLADOR` se e somente se o posto de admin estiver vago (nenhum participante com papel `ADMIN` na quadra). Rejeita com HTTP 403 caso contrário.
       - Validação: `alvo >= 1`, `teto is None or teto >= alvo`. Se `teto < alvo`, lança HTTP 422 com mensagem explicativa.
       - Emissão do evento `TipoEvento.REGRA_ALTERADA` contendo `alvo`, `vantagem`, `teto` e `anterior`.
       - Avaliação de encerramento imediato: se a nova regra aplicada à pontuação atual resultar em vitória, grava o evento `PARTIDA_ENCERRADA` e atualiza o status da partida para `ENCERRADA`.
   - `app/api.py`:
     - Modelo `ConfigurarRegrasBody` (`alvo: int`, `vantagem: bool = True`, `teto: int | None = None`).
     - Endpoint `POST /api/quadras/{quadra_id}/regras` para submissão das alterações.
     - Broadcast WebSocket de `PLACAR_ATUALIZADO` para todos os participantes da sala.
   - `app/projecao.py`:
     - Detalhamento de `REGRA_ALTERADA` em `projetar_linha_do_tempo`:
       `"Regra alterada por {autor}: alvo {alvo} pts{detalhe_vantagem}{detalhe_teto}"`.

2. **Frontend**:
   - `SalaQuadra.svelte`:
     - Exibição das regras vigentes no cabeçalho (ex: `12 pts • Vantagem • Teto 15`).
     - Botão "⚙️ Regras" exibido para quem tem permissão de edição (`ehAdmin` ou `podeControlar && !temAdminNaSala`).
     - Modal/Painel "Configurar Regras da Partida":
       - Botões rápidos de alvo comum (12, 15, 21, 25) e campo numérico.
       - Checkbox/switch de "Exigir vantagem de 2 pontos".
       - Campo opcional de "Teto da vantagem" (habilitado apenas quando vantagem está ativa).
       - Mensagem de validação inline caso o teto digitado seja menor que o alvo.
       - Botão "Salvar Regras".
     - Reatividade imediata: ao receber `PLACAR_ATUALIZADO`, os novos valores refletem no placar, cabeçalho e linha do tempo.

3. **Testes Automatizados**:
   - `tests/test_configurar_regras.py` cobrindo:
     - Configuração de regras por admin com registro no log e na linha do tempo.
     - Encerramento de partida induzido por alteração de regra (ex: 11x11, desligar vantagem e marcar ponto).
     - Alteração permitida para controlador quando o posto de admin estiver vago.
     - Bloqueio HTTP 403 para espectador e para controlador com admin presente.
     - Rejeição HTTP 422 quando teto < alvo.
     - Propagação via WebSocket.

## 4. Comportamento de Aceite (BDD)

```gherkin
Given uma quadra com partida em andamento em 11x11 e alvo 12 com vantagem ligada
When o admin desliga a exigência de vantagem
Then o próximo ponto de qualquer lado encerra a partida
And a alteração fica registrada como evento com autor e horário
And com o posto de admin vago, um controlador consegue fazer a mesma alteração
And um espectador não consegue, mesmo forjando a chamada fora da UI
And um teto menor que a pontuação-alvo é rejeitado com mensagem clara.
```

## 5. Decisões de Design

- **A quadra manda, o software obedece**: alterações durante a partida em andamento são permitidas sem restrições artificiais.
- **Transparência e auditabilidade**: nenhuma alteração de regra ocorre silenciosamente; a linha do tempo registra quem alterou, quando e quais foram os parâmetros.
- **Autoridade flexível no posto vago**: permite que quadras que passaram por sucessão degradada (sem admin ativo) continuem jogáveis e configuráveis pelos controladores presentes.
- **Validação estrita no servidor**: proteção contra tetos incoerentes (`teto < alvo`) diretamente no comando de escrita.

## 6. O que está Fora de Escopo

- Alterar regras de partidas já arquivadas / encerradas.
- Sets múltiplos e tie-break formal indoor.
- Presets rígidos de modalidade esportiva (vôlei de praia, futevôlei, etc.).

## 7. Intenção de Versão

- **Minor (0.4.0)**: conclusão da Delivery Story `CV1.DS3 — Regras da partida configuráveis pela quadra`.
