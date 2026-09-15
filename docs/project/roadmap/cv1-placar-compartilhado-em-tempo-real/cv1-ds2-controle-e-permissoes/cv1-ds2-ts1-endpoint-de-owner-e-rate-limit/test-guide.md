# Guia de Testes — CV1.DS2.TS1: Endpoint de owner e proteção contra força bruta

## 1. Testes Automatizados

Executar a suíte de testes com:

```powershell
uv run pytest tests/test_owner_endpoint.py
```

### Casos de Teste Automatizados Cobertos

1. **`test_owner_endpoint_sem_segredo_retorna_404`**:
   - Requisição GET a `/api/owner/quadras` sem headers de autenticação deve retornar status 404.
2. **`test_owner_endpoint_segredo_invalido_retorna_404`**:
   - Requisição com `x-owner-secret: segredo-errado` deve retornar status 404.
3. **`test_owner_endpoint_autenticado_com_sucesso`**:
   - Requisição com segredo correto (via `x-owner-secret` ou `Authorization: Bearer ...`) retorna 200 OK com array de quadras, incluindo seus respectivos `codigo_mestre` de 4 dígitos.
4. **`test_owner_endpoint_rate_limit_bloqueia_apos_5_tentativas`**:
   - 5 requisições seguidas com segredo inválido retornam 404.
   - A 6ª requisição (mesmo com segredo correto) é bloqueada com status 429 Too Many Requests e cabeçalho `Retry-After`.
5. **`test_rotas_publicas_nao_vazam_codigo_mestre`**:
   - Respostas de `GET /api/quadras` e `GET /api/quadras/{id}` não contêm a chave `codigo_mestre`.
6. **`test_codigo_mestre_formato_4_digitos`**:
   - Confere que o código gerado em `quadras` sempre possui comprimento 4 e consiste apenas em dígitos decimais (ex: `0000` a `9999`).

---

## 2. Rota de Validação Manual do Navigator

Com o servidor rodando localmente (`uv run uvicorn app.main:app --port 8000`):

### Cenário 1: Tentativa Não Autorizada
```powershell
# Requisição sem segredo
Invoke-RestMethod -Uri "http://localhost:8000/api/owner/quadras" -Method Get -SkipHttpErrorCheck -StatusCodeVariable status
# Deve retornar código HTTP 404
```

### Cenário 2: Consulta de Owner Autenticada
```powershell
# Cria uma quadra de teste pelo browser ou via API
# Consulta como operador da instância
Invoke-RestMethod -Uri "http://localhost:8000/api/owner/quadras" -Headers @{ "x-owner-secret" = "troque-este-segredo-em-producao" }
# O retorno deve listar as quadras ativas com id (5 dígitos) e codigo_mestre (4 dígitos)
```

### Cenário 3: Bloqueio por Força Bruta
```powershell
# Envia 6 requisições consecutivas com segredo incorreto
1..6 | ForEach-Object {
    Invoke-RestMethod -Uri "http://localhost:8000/api/owner/quadras" -Headers @{ "x-owner-secret" = "senha-errada-$_" } -SkipHttpErrorCheck -StatusCodeVariable status
    Write-Host "Tentativa $_: Status $status"
}
# As primeiras 5 retornam 404; a 6ª retorna 429 Too Many Requests
```
