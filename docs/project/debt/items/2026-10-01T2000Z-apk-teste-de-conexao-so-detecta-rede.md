---
id: debt-apk-teste-de-conexao-so-detecta-rede
status: Paid
kind: validation
severity: low
source: CV7.TS1
revisit_trigger: Falso "Servidor disponível" em quadra (backend fora com o túnel de pé), ou a TS2 começar a depender do servidor
closure_condition: /health responde com `Access-Control-Allow-Origin: https://localhost` e a tela inicial do APK lê `status: ok` em vez de só detectar a rede
---

# Teste de Conexão do APK Só Detecta Rede

## Description

A tela inicial do APK testa o servidor com `fetch(..., { mode: 'no-cors' })` em `/health`. A resposta é opaca: qualquer resposta HTTP conta como disponível, inclusive um 502 do Cloudflare Tunnel com o backend fora do ar. Só a falta de rede ou o tempo esgotado bloqueiam o botão.

## Carrying Reason

O backend não envia CORS e a TS1 prometia não mudar o backend. A falha de backend com o túnel de pé aparece logo ao abrir a quadra, sem perda de dados.

## Updates

- 2026-10-02 (CV7.US1): quitada sem mexer no backend. No APK o teste usa o `CapacitorHttp` (rede nativa, sem CORS) e só vale `200` com `status: ok` no `/health`; um 502 do túnel conta como indisponível. O servidor estava de fato fora (Cloudflare 530/1033) durante a validação, o caso que o teste antigo daria como disponível.

## Notes

Fechar exige liberar CORS só em `/health` para a origem `https://localhost` do Capacitor.
