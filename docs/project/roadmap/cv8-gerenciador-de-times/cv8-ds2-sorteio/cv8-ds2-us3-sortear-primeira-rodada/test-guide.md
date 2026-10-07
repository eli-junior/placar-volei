# Rota de validação — CV8.DS2.US3 Sortear a primeira rodada

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Abra `http://localhost:8000`, entre em **Jogadores** com `meu-segredo` e cadastre estes 8 (nome, gênero, nota), **nessa ordem**:

| # | Nome | Gênero | Nota |
|---|---|---|---|
| 1 | Ana Um | Mulher | 90 |
| 2 | Bia Dois | Mulher | 85 |
| 3 | Caio Tres | Homem | 70 |
| 4 | Davi Quatro | Homem | 65 |
| 5 | Eva Cinco | Mulher | 60 |
| 6 | Fabio Seis | Homem | 55 |
| 7 | Gil Sete | Homem | 40 |
| 8 | Helo Oito | Mulher | 30 |

Depois vá em **Sessão**, abra a sessão e marque **Presente** na mesma ordem (1 a 8).

## Passos e observações

1. **Mínimo de 4:** desmarque até sobrarem 3 → **Passa:** "Sortear duplas" fica desabilitado com "Faltam 1 presente(s) para sortear". Volte aos 8.
2. **Sortear (alvo 10):** toque **Sortear duplas** → **Passa:** aparece "Proposta 1 · alvo 10" com 4 times, em quadra os Times 1 e 2, e "Primeira partida: Time 1 × Time 2". **O resultado esperado, na ordem da fila:**
   - Time 1: Ana Um (90) + Gil Sete (40), soma 130
   - Time 2: Bia Dois (85) + Fabio Seis (55), soma 140
   - Time 3: Caio Tres (70) + Helo Oito (30), soma 100
   - Time 4: Davi Quatro (65) + Eva Cinco (60), soma 125
   Toda dupla é mista (4 homens e 4 mulheres: nenhuma H+H). A fila segue a chegada: Ana (1º) e Bia (2ª) jogam a primeira partida. **Falha:** dupla H+H, fila fora da ordem de chegada, ou resultado diferente a cada vez que repete o sorteio.
3. **Mesmo resultado:** **Descartar** e **Sortear** de novo → **Passa:** as mesmas duplas.
4. **Resortear:** com notas mais próximas há outras combinações. Aqui, `Combinação 1 de N`: se N for 1, "Resortear" fica desabilitado ("não há outra para trocar"). Para ver trocar, altere as notas para 60, 61, 60, 59, 62, 61, 60, 59 e repita → **Passa:** "Combinação 2 de N", duplas diferentes, ainda todas mistas, e a fila continua pela chegada.
5. **Ímpar:** desmarque o Helo (8º) e sorteie → **Passa:** 3 duplas + um time incompleto, **por último**, com o jogador que chegou por último (Gil), marcado "Incompleto: escolhe o parceiro na sua vez".
6. **Excedente de homens:** com 6 homens e 2 mulheres presentes → **Passa:** exatamente 2 duplas H+H e as 2 mulheres cada uma com um homem.
7. **Confirmar:** toque **Confirmar e iniciar** → **Passa:** "Rodada 1 · alvo 10", "Presença travada", "Desmarcar", "↑/↓", "Presente" e "Encerrar sessão" desabilitados, sem o cadastro rápido. Recarregue → a rodada continua.
8. **Cancelar:** **Cancelar rodada** → confirme → **Passa:** volta o bloco "Sortear a rodada" e a presença fica editável.
9. **Persistência:** com uma rodada confirmada, pare e suba o servidor (também com `RESET_DB_ON_STARTUP=true`) → **Passa:** a rodada continua.
10. **Inativar:** em **Jogadores**, tente inativar quem está na rodada → **Passa:** recusado ("está numa rodada ativa").
11. **APK:** os botões "Sessão" e "Jogadores" continuam ausentes.

## No Mini PC (depois do deploy)

`docker compose up -d --build` migra o `gerenciador.db` para o schema 4 (tabelas de rodada). Confira um sorteio e que os jogadores continuam. O backup de 6 h já guarda o banco novo.

## Evidência automatizada

`uv run pytest` (519; 203 novos desta história: gênero para todas as combinações até 12×12, ímpar, determinismo, fila pela chegada, resortear dentro da tolerância, ótimo contra força bruta, ciclo da rodada, trava de presença, concorrência, migração 3→4), `npm test` (179), `npm run check`, `npm run test:e2e` (68, com axe na proposta).
