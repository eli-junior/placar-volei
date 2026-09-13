---
code: CV1.DS1.US1
kind: test-guide
updated: 2026-09-13
---

# Guia de Teste — CV1.DS1.US1 Criar quadra e entrar por apelido

## Testes Automatizados

`tests/test_quadras_e_participantes.py`:

| caso | o que verifica |
|---|---|
| criação de quadra | `POST /api/quadras` cria quadra e grava `PARTIDA_INICIADA` na primeira partida |
| listagem de quadras | `GET /api/quadras` lista quadras criadas com contagem correta |
| primeiro participante vira admin | Primeiro `POST /entrar` recebe papel `ADMIN` |
| segundo participante vira espectador | Segundo `POST /entrar` com outra sessão recebe `ESPECTADOR` |
| persistência da sessão | `GET /api/quadras/{id}/eu` com cookie de sessão retorna participante sem pedir apelido |
| apelido duplicado na mesma quadra | Rejeição ou tratamento amigável de conflito de apelido na mesma quadra |
| presença WebSocket | Conexão WebSocket notifica outros clientes da entrada do participante |

## Rota de Validação do Navigator (Multi-Dispositivo)

1. Subir o servidor (`uv run uvicorn app.main:app --reload` ou build completo).
2. Abrir **Navegador 1** (ex: Chrome normal) em `http://localhost:8000`:
   - Visualizar a tela inicial limpa com o botão de criar quadra;
   - Clicar em "+ Criar Nova Quadra", nomear como "Quadra Praia";
   - Informar o apelido "Eli";
   - Confirmar entrada: o badge superior exibe "Admin" e "Eli" aparece na lista de presentes.
3. Abrir **Navegador 2** (janela anônima ou outro navegador, simulando um segundo celular):
   - Acessar `http://localhost:8000`;
   - "Quadra Praia" aparece na lista com 1 participante;
   - Clicar na quadra, informar o apelido "Carlos";
   - Confirmar entrada: o badge superior exibe "Espectador".
4. Observar em tempo real:
   - No Navegador 1, "Carlos" aparece na lista de presentes com animação suave;
   - No Navegador 2, "Eli (Admin)" e "Carlos (Espectador)" estão ambos visíveis.
5. Recarregar a página em ambos:
   - A página recarrega e volta direto para a quadra, mantendo Eli como Admin e Carlos como Espectador, sem exigir novo apelido.

**Condição de aprovação:**
- Primeiro participante é Admin, segundo é Espectador;
- Atualização visual em tempo real entre as duas abas;
- Preservação do papel e sessão ao recarregar a página.

**Condição de falha:**
- Segundo participante conseguir virar Admin;
- Tela pedir apelido novamente após F5;
- Ausência de sincronização em tempo real na lista de presentes.
