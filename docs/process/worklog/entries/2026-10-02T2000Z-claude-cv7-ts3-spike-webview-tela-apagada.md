---
date: 2026-10-02T20:00:00Z
author: Claude Code (Driver)
kind: spike
related:
  - CV7.TS3
verification:
  - adb: registro do JS (Preferences) contra o contador nativo, com a tela apagada por KEYCODE_SLEEP
---

# Spike: o JS do WebView roda com a tela apagada?

## Question

A quadra local roda em JS dentro do WebView. O celular atende o relógio (Data Layer) com a tela apagada?

## Method

Plugin de teste que dispara um evento nativo a cada 5 s e guarda a própria contagem; página de teste que anota cada evento recebido, um `setInterval` de 5 s, o wake lock e a visibilidade. Galaxy Z Fold (SM-F956B), build debug, tela apagada por `adb`. Duas condições: só o plugin, e com serviço em primeiro plano + wake lock parcial (CPU acordada).

## Result

- **Wake lock da página** (`navigator.wakeLock`): funciona neste WebView. Com ele ativo a tela ficou acesa 11 minutos sem toque. Ele é liberado sozinho quando a tela apaga.
- **Só o plugin**, tela apagada por 3m16s: o JS seguiu irregular por cerca de 2 minutos (tiques de 8 a 16 s em vez de 5 s) e parou. O próprio contador nativo ficou atrás (155 de ~183): o processo inteiro foi congelado.
- **Serviço em primeiro plano + wake lock parcial**, tela apagada por 3m26s: processo e CPU vivos (contador nativo regular, 51 de ~49 esperados), mas o JS do WebView rodou regular por cerca de 2 minutos e parou do mesmo jeito. O corte é do WebView escondido, não do processo.

## Decision

Plano B (Navigator, 2026-10-02): a quadra local mantém a tela do celular acesa e atende o relógio pelo plugin. O JS não é confiável com a tela apagada além de ~2 min. Se a tela apagar, a fila offline do relógio guarda os lances e eles são reenviados quando o celular voltar; o celular descarta duplicatas pelos recibos. O plano C (regras também em Java, aplicadas pelo processo nativo) fica como evolução se, na quadra, a tela apagar com frequência.

## Follow-up

O código do spike (`SpikePlugin`, `SpikeService`, `Spike.svelte`) saiu da árvore; o histórico da branch o guarda.
