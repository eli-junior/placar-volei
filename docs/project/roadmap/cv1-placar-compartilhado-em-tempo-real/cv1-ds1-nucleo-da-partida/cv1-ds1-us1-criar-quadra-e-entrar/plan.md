---
code: CV1.DS1.US1
kind: plan
status: Implemented
approved_by: Navigator
updated: 2026-09-13
---

# Plano — CV1.DS1.US1 Criar quadra e entrar por apelido

## Nível e Versão

- **Nível:** User Story (`CV1.DS1.US1`)
- **Versão alvo:** `0.1.0` (trabalho interno dentro do primeiro marco de entrega)

## Escopo

1. **Backend (FastAPI + SQLite):**
   - Endpoints REST para quadras:
     - `GET /api/quadras`: lista de quadras com contagem de presentes.
     - `POST /api/quadras`: cria quadra e inicializa a primeira partida (`PARTIDA_INICIADA`).
     - `GET /api/quadras/{id}/eu`: retorna participante atual a partir do cookie de sessão.
     - `POST /api/quadras/{id}/entrar`: registra apelido na sessão, define cookie `session_id`, atribui `ADMIN` ao primeiro ou `ESPECTADOR` aos seguintes.
     - `GET /api/quadras/{id}/participantes`: lista de presentes com papel e status online.
   - WebSocket da quadra (`/ws/{quadra_id}`):
     - Atualização de presença em tempo real quando participantes conectam e desconectam.
     - Entrega do estado inicial da quadra na conexão.
   - Servir estáticos do frontend compildos e fallback SPA no `app/main.py`.

2. **Frontend (Svelte 5):**
   - Configuração do projeto `web/` com Vite e Svelte 5.
   - Telas:
     - **Tela de Entrada / Seleção de Quadras:** lista quadras disponíveis e botão "+ Criar Nova Quadra".
     - **Modal / Tela de Apelido:** formulário simples pedindo apelido antes de entrar na quadra.
     - **Sala da Quadra (Visão Inicial):** cabeçalho da quadra, badge de papel (Admin / Espectador), lista de presentes com animação Svelte (`slide` / `fade`), e aviso de aguardo do início do jogo.
   - Reconexão e persistência:
     - Ao recarregar a página em `/quadra/{id}`, valida sessão via cookie e restaura direto a sala sem pedir apelido.

## Comportamento de Aceite (BDD)

```gherkin
Given nenhuma quadra ativa no sistema
When o primeiro usuário acessa o sistema, cria a quadra "Vôlei das 19h" e informa o apelido "Eli"
Then ele entra na quadra com o papel de ADMIN
And a quadra passa a aparecer na listagem inicial para outros usuários
And quando um segundo usuário acessa a quadra e informa o apelido "Carlos"
Then Carlos entra na quadra com o papel de ESPECTADOR
And ambos visualizam imediatamente a lista de participantes atualizada em tempo real (Eli - Admin, Carlos - Espectador)
And ao recarregar a página em qualquer um dos dois navegadores, o participante permanece na quadra com o mesmo apelido e papel, sem necessidade de novo registro.
```

## Decisões de Design

### 1. Sessão por Cookie HttpOnly
- Cookie `session_id` com UUID opaco gerado no backend.
- Sem senhas, sem expiração curta invasiva.
- O cookie identifica o participante dentro da quadra; recarregar a página consulta `/api/quadras/{id}/eu` e restabelece a conexão WebSocket sem atrito.
- *Alternativa rejeitada:* LocalStorage / Token JWT manual no header — mais suscetível a XSS e exige gerenciar tokens em cada requisição na mão.

### 2. Primeiro a Entrar é Admin
- Ao processar o registro de apelido (`POST /entrar`), verifica atomicamente a contagem de participantes da quadra:
  - 0 participantes -> `ADMIN`.
  - >= 1 participantes -> `ESPECTADOR`.
- *Alternativa rejeitada:* Criação de quadra desvinculada de participante — quem cria já quer entrar e jogar.

### 3. Partida Inicial Criada com a Quadra
- Ao criar a quadra, uma partida com status `EM_ANDAMENTO` já é registrada e o evento `PARTIDA_INICIADA` é gravado no log append-only com a regra padrão (alvo: 12, vantagem: True, teto: None). A quadra já nasce pronta para a pontuação da US2.

### 4. SPA Integrado ao FastAPI
- O frontend Svelte compila para estáticos em `app/static/` (ou servido via Vite no dev).
- O backend FastAPI serve `index.html` como fallback para rotas client-side, permitindo abrir URLs diretas como `http://localhost:8000/quadra/{id}` sem 404.

## Fora de Escopo

- Exclusão ou encerramento manual de quadra.
- Expiração de quadra inativa (será tratada quando houver volume).
- Unicidade global de apelido (unicidade apenas dentro da mesma quadra ativa).
- Botões de pontuação (pertencem à `CV1.DS1.US2`).

## Riscos e Mitigações

1. **Risco:** Dois usuários tentarem registrar como primeiro participante no mesmo milissegundo.
   - **Mitigação:** Registro transacionado ou serializado pelo lock da quadra; o primeiro que obtém o lock vira admin.
2. **Risco:** Celular perder conexão momentânea e sumir da lista de presentes.
   - **Mitigação:** O participante permanece listado como participante da quadra; o status `online` reflete a conexão ativa de WebSocket, com reconexão automática no frontend.
