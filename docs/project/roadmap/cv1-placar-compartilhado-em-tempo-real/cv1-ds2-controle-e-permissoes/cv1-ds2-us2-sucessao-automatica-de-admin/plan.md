# Plano de Implementação — CV1.DS2.US2: Sucessão automática do admin

## 1. Contexto e Intenção

A partida não pode travar nem ficar sem administração se o administrador fechar o navegador, perder conexão ou ficar sem bateria durante o jogo.

Esta história implementa a sucessão automática após 2 minutos de ausência do admin:
- O controlador que entrou na quadra há mais tempo (`criado_em ASC`) é promovido automaticamente a `ADMIN`.
- O evento auditável `ADMIN_SUCEDIDO` é registrado no log append-only e exibido na Linha do Tempo.
- O admin original, caso retorne à partida, volta como `CONTROLADOR` (não recupera a administração automaticamente).
- Caso não haja nenhum controlador online no momento da sucessão, a quadra permanece sem admin (posto vago), e os controladores existentes continuam com permissão para pontuar e desfazer pontos normalmente.

## 2. Nível no Roadmap e Branch

- **Nível**: User Story (`CV1.DS2.US2` dentro da Delivery Story ativa `CV1.DS2 — Controle e permissões da quadra`).
- **Branch**: `feature/cv1-ds2-us2-sucessao-automatica-de-admin` (criada a partir de `master`).

## 3. Escopo

1. **Backend**:
   - `app/sucessao.py`:
     - Função `verificar_sucessao_quadra_sync(db_path, quadra_id, online_ids, timeout_seconds=None)`:
       - Localiza o admin atual da quadra e afere se está ausente (`id not in online_ids`).
       - Calcula o tempo offline a partir de `ultimo_visto_em`.
       - Se tempo offline >= `admin_timeout_seconds` (padrão 120s):
         - Busca controladores online ordenados por `criado_em ASC`.
         - Se houver controlador online: promove o primeiro a `ADMIN`, rebaixa o admin anterior a `CONTROLADOR`, transfere controle ativo se estava com o admin anterior, grava evento `ADMIN_SUCEDIDO`.
         - Se não houver controlador online: rebaixa o admin anterior a `CONTROLADOR` (posto vago), grava evento `ADMIN_SUCEDIDO` com `novo_admin_id=None`.
     - Função assíncrona `verificar_sucessao(quadra_id)`.
   - `app/quadras.py`:
     - Função `atualizar_ultimo_visto_sync(db_path, participante_id)` para registrar com precisão o momento em que o participante desconectou ou esteve ativo.
   - `app/main.py`:
     - No disconnect do WebSocket, atualizar `ultimo_visto_em` do participante.
     - Rotina assíncrona periódica em background no `lifespan` do FastAPI para checar sucessão nas quadras com conexões ativas e realizar broadcast WebSocket de `PLACAR_ATUALIZADO` e `PRESENCA_ATUALIZADA`.
   - `app/eventos.py`:
     - Payload padrão para `TipoEvento.ADMIN_SUCEDIDO`: `antigo_admin_id`, `antigo_admin_apelido`, `novo_admin_id`, `novo_admin_apelido`, `motivo`.
   - `app/projecao.py`:
     - Projeção de `ADMIN_SUCEDIDO` na narrativa da `Linha do Tempo`:
       - Com novo admin: `"{novo_admin} assumiu a administração por sucessão (ausência de {antigo_admin})"`
       - Sem novo admin: `"Administração vaga por ausência de {antigo_admin}"`
   - `app/config.py`:
     - `admin_timeout_seconds: int = 120` (já presente, configurável via ambiente).

2. **Frontend**:
   - `App.svelte` & `sync.js`:
     - Ao receber `PLACAR_ATUALIZADO`, os participantes e o objeto `eu` reagem imediatamente ao novo papel.
   - `ListaPresentes.svelte`:
     - Quando um participante é promovido a `ADMIN`, ele passa a ver os botões de gerência ("Tornar controlador" / "Revogar controlador") para os outros participantes.
     - Badges de papéis atualizam em tempo real.
   - `Placar.svelte` e `SalaQuadra.svelte`:
     - Mantêm a capacidade de controle e pontuação reativa sem interrupção.

3. **Testes Automatizados**:
   - `tests/test_sucessao_admin.py` cobrindo:
     - Promoção do controlador online mais antigo.
     - Rebaixamento do admin antigo para `CONTROLADOR`.
     - Evento `ADMIN_SUCEDIDO` e projeção na Linha do Tempo.
     - Reconexão do admin original mantendo papel de `CONTROLADOR`.
     - Caso sem controladores online (posto vago, controladores continuam pontuando).
     - Não disparar sucessão quando o admin ainda está online ou antes dos 2 minutos.
     - Ciclo via WebSocket.

## 4. Comportamento de Aceite (BDD)

```gherkin
Given uma quadra com admin e dois controladores
When o admin fica offline por mais de 2 minutos
Then o controlador que entrou primeiro é promovido a admin
And o evento aparece para todos na quadra
And quando o admin original reconecta, ele volta como controlador
And se não houver controlador online, a quadra segue sem admin e os controladores existentes continuam pontuando.
```

## 5. Decisões de Design

- **Ordem de sucessão determinística**: baseada em `criado_em ASC` dos participantes cadastrados como `CONTROLADOR` na quadra, premiando o controlador mais antigo online.
- **Demoting no banco de dados**: ao disparar a sucessão, o admin anterior passa para `CONTROLADOR` no SQLite. Quando ele reconectar com seu cookie de sessão existente, a API já o carrega como `CONTROLADOR`, sem risco de recuperar o posto sem autorização.
- **Worker periódico e leve**: loop com `asyncio.sleep(2)` no `lifespan` do FastAPI verifica apenas as quadras ativas que possuem participantes conectados no `ConnectionHub`, garantindo overhead mínimo de CPU e I/O.
- **Timeout parametrizável**: o padrão operacional em produção é de 120 segundos (2 minutos), mas a rotina aceita override para testes automatizados rápidos e determinísticos.

## 6. O que está Fora de Escopo

- Devolução automática do posto ao admin original ao reconectar.
- Recuperação de administração por código mestre do operador / Owner Takeover (`CV1.DS2.US3`).
- Alteração de regras por controlador enquanto o posto de admin estiver vago (`CV1.DS3.US1`).

## 7. Intenção de Versão

- **Patch (0.3.3)**: entrega de funcionalidade incremental da Delivery Story `CV1.DS2`.
