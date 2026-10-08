---
author: Claude Sonnet 5.5 (Driver)
date: 2026-10-08
related:
  - CV8.DS6.US15
---

# CV8.DS6.US15 — formato trio (0.45.0)

- **Decisões do Navigator:** rodada inteira em trios; trio misto (nunca HHH/MMM, salvo grupo de um sexo só); sobra de 1 escolhe 2 parceiros; placar igual. Sobra de 2 e "minimizar trios de um sexo quando falta um sexo" foram propostas do Driver e confirmadas.
- **Código:** `sorteio._sortear_trios` (busca local por trocas, custo = trios de um sexo × peso + soma² das notas), `conducao.time_ruim`/`lista_de_escalacao` com `atuais` e `tamanho`, `rodadas.formato` (schema 9). O relógio não mudou: já mostra a lista de nomes.
- **Armadilha:** `escalar_parceiro` só zera `incompleto` quando o time chega ao tamanho; a escolha de 2 parceiros é um POST por vez.
- **Dívida:** dois algoritmos de sorteio; sem teste de 3 nomes no relógio físico.
