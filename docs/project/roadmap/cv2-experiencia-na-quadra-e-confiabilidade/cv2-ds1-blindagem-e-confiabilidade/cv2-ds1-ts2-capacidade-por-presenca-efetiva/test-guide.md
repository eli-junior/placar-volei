---
code: CV2.DS1.TS2
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV2.DS1.TS2: Capacidade por presença efetiva

## 1. Verificação Automatizada

```bash
cd web && npm run build && cd ..
uv run pytest tests/test_blindagem_e_confiabilidade.py
uv run pytest tests/test_quadras_e_participantes.py::test_limites_capacidade
uv run ruff check .
```

### Cobertura (`tests/test_blindagem_e_confiabilidade.py`)

1. **`test_sala_genuinamente_cheia_continua_bloqueando`**
   - Limite baixado para 2. Admin + uma pessoa ocupam a sala, ambos com sinal de vida recente.
   - A terceira entrada recebe HTTP 400 com `"Limite máximo de 2 participantes"`.
   - Prova que a mudança não afrouxou a proteção contra abuso.

2. **`test_entrada_liberada_apos_expiracao_dos_fantasmas`**
   - Mesma sala cheia; o `ultimo_visto_em` de todos é recuado uma hora, simulando quem fechou o navegador.
   - A entrada seguinte é aceita (HTTP 200).
   - O teste também afirma que o recém-chegado entra como `ESPECTADOR` — vaga liberada não é promoção a admin.

3. **`test_conexao_ativa_ocupa_vaga_mesmo_sem_sinal_recente`**
   - Limite 1. Com o WebSocket do admin **aberto**, o `ultimo_visto_em` é recuado uma hora e a entrada de outra pessoa é recusada: a conexão viva vale mais que o carimbo velho.
   - Fechado o socket e recuado o carimbo de novo, a mesma entrada é aceita.
   - É o teste que distingue as duas fontes de presença de forma independente.

## 2. Roteiro de Validação do Navigator (3 clientes)

Como o limite de produção é 20 pessoas, a validação manual baixa o limite por configuração.

### Preparação

No `.env`, acrescentar (e remover depois do teste):

```
MAX_PARTICIPANTES_POR_QUADRA=2
PRESENCA_TTL_SECONDS=30
```

Subir a aplicação:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Passo a passo

1. **Cliente A** (navegador comum): criar um placar em `http://localhost:8000`. Anotar o código.
2. **Cliente B** (janela anônima): entrar com o código e um apelido. A sala agora tem 2 de 2.
3. **Cliente C** (celular ou segundo navegador anônimo): tentar entrar com o mesmo código.
   - **O que observar**: mensagem legível de sala cheia, sem `[object Object]` e sem erro genérico.
4. Fechar as abas dos clientes **A e B** por completo (não apenas navegar para trás).
5. Esperar **35 segundos** (a janela de 30s mais folga).
6. No **Cliente C**, tentar entrar novamente.
   - **O que observar**: a entrada é aceita e o placar carrega normalmente.
7. Repetir o cenário mantendo o **Cliente A aberto** o tempo todo, com a tela da sala visível:
   - Entrar com B, tentar com C (recusado), fechar só o B, esperar 35s, tentar com C.
   - **O que observar**: C entra (vaga do B), mas a vaga do A nunca é liberada enquanto a aba dele estiver aberta.

### Condição de aprovação
- Sala com gente de verdade recusa a terceira pessoa com mensagem compreensível.
- Sala abandonada volta a aceitar entrada depois da janela de presença, sem reiniciar o servidor.
- A vaga de um cliente com a aba aberta **nunca** é liberada, mesmo depois da janela.
- Nenhum travamento: a resposta de `POST /entrar` continua imediata (o teste de fumaça é a própria fluidez das tentativas acima).

### Condição de falha
- Terceira pessoa entrando com A e B abertos (limite afrouxado).
- Sala abandonada continuando cheia depois da janela (débito não quitado).
- Resposta de entrada demorando visivelmente ou pendurando — sinal de contenção entre a transação e o hub.
- Pessoa que entra na vaga liberada aparecendo com papel `ADMIN`.
