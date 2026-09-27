# Plano — CV5.DS3.TS1 Broadcast paralelo

- **Nível:** Technical Story · **Branch:** `feature/cv5-ds3-ts1-broadcast-paralelo` · **Versão:** patch

## Scope
1. `ConnectionHub.broadcast` (`app/hub.py:72`) envia para todos os sockets com `asyncio.gather`, cada envio com `asyncio.wait_for(..., 2 s)`. Socket que estoura o tempo ou falha é desconectado e fechado; o cliente reconecta e recebe `ESTADO_INICIAL`.
2. `device_active` sai do caminho do broadcast: o laço de 5 s de cada socket de relógio (`app/main.py:197`) já fecha dispositivos revogados, e a revogação explícita chama `close_watch_connections`. Menos um SELECT por relógio por mensagem.
3. `publicar_snapshot` (`app/main.py:52`) manda os dois tipos numa rodada só (`broadcast_many`), sem mudar o contrato das mensagens.

## Acceptance
- Dado um cliente que não lê o socket, quando marco um ponto, então os outros recebem o placar em menos de 1 s e o cliente travado é desconectado em até 2 s.
- Dado um relógio revogado, então o socket dele é fechado com 4401 em até 5 s.

## Design
Timeout por socket em vez de fila por cliente: menos código, e o cliente lento já tem reconexão com snapshot completo. Rejeitado: fila com descarte por cliente (complexidade sem ganho nesta escala).

## Out of Scope
Trocar o SELECT de expiração por aviso do hub (`app/main.py:192`): ganho pequeno com 20 salas, fica anotado.

## Risks
Mensagens para o mesmo socket passam a sair em paralelo entre broadcasts? Não: cada broadcast espera o `gather` antes de retornar, e os broadcasts da sala já correm sob o lock da sala.

## Validation
Teste com socket falso que dorme 10 s em `send_json`; `uv run pytest -q`.
