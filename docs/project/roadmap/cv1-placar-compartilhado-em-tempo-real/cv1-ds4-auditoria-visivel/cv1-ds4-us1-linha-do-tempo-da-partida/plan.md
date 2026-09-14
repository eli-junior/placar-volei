---
code: CV1.DS4.US1
kind: plan
status: Implemented
approved_by: Navigator
updated: 2026-09-14
---

# Plano — CV1.DS4.US1 Linha do tempo da partida

## Nível e Versão

- **Nível:** User Story (`CV1.DS4.US1`)
- **Versão alvo:** `0.1.0` (primeira entrega de `CV1.DS4 - Auditoria Visível da Partida`)

## Escopo

1. **Projeção da Linha do Tempo no Backend (`app/projecao.py`):**
   - Função pura `projetar_linha_do_tempo(eventos, apelidos_map)`:
     - Itera cronologicamente sobre os eventos do log append-only.
     - Identifica pontos anulados por `PONTO_DESFEITO` (`ref_seq`).
     - Calcula o placar resultante a cada passo (`pontos_a` e `pontos_b`).
     - Produz itens ricos contendo: `seq`, `tipo`, `equipe`, `autor_apelido`, `criado_em`, `pontos_a`, `pontos_b`, `anulado`, `ref_seq` e `descricao`.

2. **Endpoints e WebSocket (`app/api.py` e `app/main.py`):**
   - `GET /api/quadras/{quadra_id}/linha-do-tempo`: retorna a lista cronológica da partida atual.
   - Inclusão dos dados de `linha_do_tempo` no broadcast WebSocket (`PLACAR_ATUALIZADO` e `ESTADO_INICIAL`), garantindo atualização em tempo real sem latência ou polling.

3. **Interface do Usuário no Frontend (Svelte 5):**
   - Componente `web/src/components/LinhaDoTempo.svelte`:
     - Modal/gaveta lateral ergonômico, responsivo para celular e tablet.
     - Apresentação visual limpa de cada lance com horário, autor, equipe, placar resultante e status (ativo vs. anulado com strikethrough/badge).
     - Atualização instantânea com transições suaves do Svelte (`slide`/`fly`) ao receber novos eventos via WebSocket.
   - Botão de acesso em `web/src/components/Placar.svelte`:
     - Acessível igualmente para **todos os papéis** (Admin, Controlador e Espectador).
     - Posicionamento no cabeçalho do placar mantendo a visão principal desobstruída.

4. **Empacotamento com Docker (`Dockerfile` e `docker-compose.yml`):**
   - Build multi-estágio: Node compila frontend em `app/static/`, uv prepara venv Python, runtime slim final sem Node ou npm.
   - Compose configurado com volume persistente para banco de dados SQLite.

## Comportamento de Aceite (BDD)

```gherkin
Given uma partida em andamento com pontos marcados e desfeitos
When qualquer participante (controlador, admin ou espectador) aciona o botão da linha do tempo
Then uma gaveta/modal abre exibindo todos os eventos da partida em ordem cronológica
And cada ponto marcado exibe o autor do lance, equipe, horário e o placar resultante naquele momento
And pontos que foram desfeitos aparecem claramente identificados como "Anulado" com estilo visual riscado
And as correções de anulação aparecem registradas com o autor que desfez
And quando outro participante marca ou desfaz um ponto com a linha do tempo aberta, o novo evento entra ao vivo com animação suave sem recarregar a tela
And ao fechar a linha do tempo, o usuário retorna imediatamente à visão do placar.
```

## Decisões de Design

### 1. Leitura Direta do Log de Eventos Append-Only
- A linha do tempo é uma projeção determinística direta da sequência de eventos (`eventos`), mapeando `autor_id` para o apelido gravado.
- *Por que:* Garante fidelidade matemática absoluta. Não existe cache intermediário ou tabela separada que possa divergir do placar real.

### 2. Transmissão no Broadcast do WebSocket
- Em vez de forçar o cliente a fazer requisições HTTP repetidas a cada ponto enquanto a linha do tempo está aberta, enviamos `linha_do_tempo` projetada no payload do WebSocket de `PLACAR_ATUALIZADO`.
- *Por que:* Numa partida de set único (12 a 25 pontos), o tamanho de todo o histórico é inferior a 2 KB. O custo de rede é desprezível e a experiência do usuário é instantânea (zero roundtrips adicionais).

### 3. Acesso Democrático
- Conforme solicitado pelo Navigator e registrado no roadmap, espectadores que assistem em celulares e tablets têm acesso total à linha do tempo para acompanhar como o jogo evoluiu.
- *Por que:* Transparência é o valor central de `CV1.DS4` ("Auditoria Visível").

## Fora de Escopo

- Partidas arquivadas de dias anteriores.
- Filtros por jogador ou busca de texto na linha do tempo.
- Exportação em PDF ou imagem.
