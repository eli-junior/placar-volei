# Plano de Implementação — CV1.DS2.TS1: Endpoint de owner e proteção contra força bruta

## 1. Contexto e Intenção

O operador da instância (Mini PC local publicado via túnel) precisa de um canal seguro e isolado da interface pública para inspecionar as quadras ativas do servidor e consultar os códigos mestres de 4 dígitos gerados para cada quadra.

Para manter códigos curtos de 4 dígitos (10.000 combinações) seguros e defensáveis na rede, é mandatório um mecanismo robusto de proteção contra força bruta (rate limiting com bloqueio temporário após 5 tentativas falhas), autenticação segura com segredo configurado no ambiente (`settings.owner_secret`) e isolamento completo para que o segredo e o código mestre nunca vazem na UI pública ou em logs.

## 2. Nível no Roadmap e Branch

- **Nível**: Technical Story (`CV1.DS2.TS1` dentro da Delivery Story `CV1.DS2 — Controle e permissões da quadra`).
- **Branch**: `feature/cv1-ds2-ts1-endpoint-owner-rate-limit` (criada a partir de `master`).

## 3. Escopo

1. **Banco de Dados e Persistência**:
   - `app/db.py`:
     - Adicionar coluna `codigo_mestre TEXT` na tabela `quadras` em `SCHEMA_SQL`.
     - Migração transparente em `init_db_sync`: se a coluna não existir, executar `ALTER TABLE quadras ADD COLUMN codigo_mestre TEXT;`.
   - `app/quadras.py`:
     - Gerar código mestre criptograficamente seguro de 4 dígitos (`0000` a `9999`) usando `secrets.randbelow(10000)`.
     - Persistir o código na criação da quadra (`criar_quadra_sync`).

2. **Proteção Contra Força Bruta (Rate Limiting)**:
   - `app/rate_limit.py`:
     - Mecanismo em memória de contagem de tentativas falhas por chave (IP / Session).
     - Janela de observação (10 minutos) e tolerância máxima de 5 tentativas consecutivas incorretas.
     - Ao exceder 5 falhas, bloqueia requisições daquele IP/sessão retornando `HTTP 429 Too Many Requests` com cabeçalho `Retry-After`.
     - Sucesso na autenticação limpa as falhas acumuladas para o identificador.

3. **Endpoint de Owner Autenticado**:
   - `app/api.py`:
     - Novo endpoint `GET /api/owner/quadras` (e rota de conveniência `GET /owner/quadras`).
     - Extração de segredo via header `x-owner-secret` ou `Authorization: Bearer <secret>`.
     - Comparação em tempo constante usando `secrets.compare_digest` para mitigar timing attacks.
     - Se o rate limit estiver acionado: retornar `HTTP 429`.
     - Se o segredo for inválido ou ausente: registrar tentativa falha no rate limiter e retornar `HTTP 404 Not Found` (resposta neutra para não confirmar a existência do endpoint para atacantes).
     - Se autenticado com sucesso: retornar JSON estruturado com as quadras ativas da instância, incluindo `codigo_mestre`, `id` (PIN de 5 dígitos), `nome`, `partida_id`, `participantes`, `controle_id` e `estado_partida`.

4. **Confidencialidade e Segurança de Dados**:
   - Garantir que `codigo_mestre` **nunca** seja incluído nas respostas dos endpoints públicos (`/api/quadras`, `/api/quadras/{id}`, `/api/quadras/{id}/partida`) nem transmitido em eventos via WebSocket.
   - Garantir que `settings.owner_secret` nunca seja impresso em logs de aplicação.

5. **Testes Automatizados**:
   - Criação de `tests/test_owner_endpoint.py`:
     - Consulta bem-sucedida com segredo válido retornando dados completos e códigos de 4 dígitos.
     - Rejeição sem segredo ou com segredo inválido (retornando 404).
     - Bloqueio após 5 tentativas incorretas consecutivas com retorno HTTP 429.
     - Validação de isolamento: conferir que endpoints públicos e WebSocket não vazam `codigo_mestre`.
     - Conferir que `secrets.randbelow` gera códigos de 4 dígitos preenchidos com zeros à esquerda (ex: `0042`).

## 4. Comportamento de Aceite (BDD)

```gherkin
Given a aplicação em execução com owner_secret configurado
When uma requisição chega a /api/owner/quadras sem o segredo correto
Then a resposta retorna 404 Not Found sem revelar detalhes nem os códigos mestres
And a tentativa incorreta é contabilizada no rate limiter
When 5 tentativas incorretas consecutivas ocorrem a partir da mesma origem
Then a 6ª requisição é bloqueada com status 429 Too Many Requests
When uma requisição chega com o segredo correto via header x-owner-secret ou Bearer token
Then a resposta retorna 200 OK com a listagem completa das quadras e seus respectivos códigos mestres de 4 dígitos
And nenhuma rota pública (/api/quadras/*) expõe o código mestre.
```

## 5. Decisões de Design

- **404 em vez de 401 para requisições não autenticadas**: O ADR define que o endpoint de owner é isolado e invisível na aplicação; retornar 404 mascara a própria existência da rota para varreduras públicas não autorizadas.
- **`secrets` vs `random`**: Geração criptograficamente segura via CSPRNG para evitar previsibilidade matemática dos códigos de 4 dígitos.
- **Formatação de 4 dígitos com zero-padding**: `f"{secrets.randbelow(10000):04d}"` assegura que números como 7 virem `"0007"`, mantendo formato uniforme e amigável.
- **Timing-safe comparison**: Uso de `secrets.compare_digest` para checagem do token de owner.

## 6. O que está Fora de Escopo

- Rota de takeover do admin em si (`CV1.DS2.US3` - depriorizada pelo Navigator).
- Interface web/UI administrativa pública (o endpoint é restrito ao operador da instância via API/CLI).

## 7. Intenção de Versão

- **Patch (0.4.1)**: capacidade técnica interna e endurecimento de segurança do operador da instância.
