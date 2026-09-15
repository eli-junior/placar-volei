# Plano de Implementação — CV2.DS1.TS2: Capacidade por presença efetiva

## 1. Contexto e Intenção

`registrar_participante_sync` validava `settings.max_participantes_por_quadra` com um `SELECT COUNT(*) FROM participantes WHERE quadra_id = ?`. A contagem por linha bastava quando o limite nasceu (`CV1.DS1.US1`), antes de existir a noção de presença no hub.

Hoje o projeto tem duas fontes confiáveis de presença — a conexão WebSocket registrada em `app/hub.py` e a coluna `ultimo_visto_em`, atualizada na conexão e na desconexão — e nenhuma das duas participava da decisão. Numa pelada com rotatividade, a sala lota de gente que já foi embora e recusa quem está na quadra.

## 2. Nível no Roadmap e Branch

- **Nível**: Technical Story (`CV2.DS1.TS2`).
- **Branch**: `worktree-agent-a5cb003370b910540`.

## 3. O problema de desenho: transação síncrona x hub assíncrono

A checagem vive dentro de `with get_db(...)` + `BEGIN IMMEDIATE`, executada em uma thread por `asyncio.to_thread`. O hub é assíncrono e protege seu estado com um `asyncio.Lock`. Combinar os dois ingenuamente cria três riscos concretos:

1. **Bloqueio de thread no event loop.** Chamar `asyncio.run_coroutine_threadsafe(hub.participantes_online(...), loop).result()` de dentro da thread da transação faz a thread ficar parada esperando o loop enquanto **segura o lock de escrita do SQLite**. Qualquer lentidão no loop vira contenção no banco para todas as salas.
2. **Dependência circular de camadas.** `app/quadras.py` (persistência) passaria a importar `app/hub.py` (transporte). Hoje o hub não conhece o banco e o banco não conhece o hub; inverter isso amarra dois módulos que mudam por motivos diferentes.
3. **Espera aninhada.** `registrar_participante` já segura `get_quadra_lock(quadra_id)` (um `asyncio.Lock`) enquanto aguarda a thread. Somar a isso uma espera da thread pelo `hub._lock` cria um caminho de espera cruzada entre um lock do loop e um lock de thread — exatamente a forma de um deadlock aparecer em produção e nunca em teste.

### Desenho escolhido: presença entra como valor, não como chamada

A borda HTTP (`app/api.py`), que já é assíncrona e já importa o hub, lê `await hub.participantes_online(quadra_id)` **antes** de iniciar a transação e passa o conjunto adiante:

```
POST /entrar  →  ids_online = await hub.participantes_online(...)   (event loop)
              →  registrar_participante(..., ids_online=ids_online)
              →  asyncio.to_thread(registrar_participante_sync, ..., frozenset(ids_online))
              →  BEGIN IMMEDIATE ... contar_presentes(registrados, ids_online, limite)
```

Consequências:

- **Sem deadlock**: o `hub._lock` é adquirido e liberado no event loop, antes de a thread existir. A thread nunca espera pelo loop.
- **Sem dependência circular**: `app/quadras.py` continua sem importar `app/hub.py`. A persistência recebe um `frozenset` de strings; não sabe o que é um WebSocket.
- **Decisão atômica no banco**: a contagem e a inserção seguem dentro do mesmo `BEGIN IMMEDIATE`, então duas entradas simultâneas não passam pelo limite juntas.
- **Testável sem servidor**: `registrar_participante_sync` aceita `ids_online` direto, o que permite testar a regra sem levantar hub nem event loop.

**Trade-off aceito**: o retrato de presença é lido microssegundos antes da transação. Se alguém desconectar nesse intervalo, ainda conta como presente por até `presenca_ttl_seconds`. O erro é sempre conservador (recusa a mais, nunca admite a mais) e se corrige sozinho na janela seguinte.

**Alternativa rejeitada**: manter o hub como fonte única e consultar dentro da transação. Resolveria o retrato desatualizado ao custo dos três riscos acima. Não vale para um limite cujo propósito é proteção contra abuso, não precisão contábil.

## 4. Escopo

1. `app/config.py`: `presenca_ttl_seconds: int = 120`, com comentário explicando o papel da janela.
2. `app/quadras.py`:
   - `limite_de_presenca(agora=None)` devolve o instante ISO a partir do qual `ultimo_visto_em` ainda conta.
   - `contar_presentes(registrados, ids_online, limite)` conta quem está no hub ou dentro da janela.
   - `registrar_participante_sync(..., ids_online=None)` usa `contar_presentes` para a capacidade e mantém `len(registrados)` para o papel inicial.
   - `registrar_participante(..., ids_online=None)` repassa o conjunto como `frozenset`.
3. `app/api.py`: `post_entrar_quadra` lê o hub e injeta `ids_online`.
4. `tests/test_blindagem_e_confiabilidade.py`: três testes (cheia, fantasmas expirados, conexão ativa prevalecendo).

## 5. Decisão sobre o papel inicial

A capacidade passa a olhar presença, mas `papel = "ADMIN" if total_participantes == 0` continua olhando o total de registros. Se as duas contas usassem presença, uma sala com um admin ausente (fantasma) promoveria o próximo a entrar a administrador — uma escalada de privilégio silenciosa vinda de uma mudança sobre capacidade. A sucessão de admin já tem regra própria em `app/sucessao.py` e é lá que ela deve continuar. Um teste afirma que o participante que entra na vaga liberada recebe `ESPECTADOR`.

## 6. O que está Fora de Escopo

- Remover do banco participantes ausentes.
- Alterar a lista de presentes exibida na UI.
- Mudar o limite global de quadras.

## 7. Intenção de Versão

- **Patch** dentro da `CV2.DS1`: correção de comportamento, sem novo contrato de API.
