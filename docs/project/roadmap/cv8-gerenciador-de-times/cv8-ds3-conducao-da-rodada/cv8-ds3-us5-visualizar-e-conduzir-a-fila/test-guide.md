# Rota de validação — CV8.DS3.US5 Visualizar e conduzir a fila

## Preparação (local)

```bash
cd web && npm run build && cd ..
OWNER_SECRET=meu-segredo GERENCIADOR_DB_PATH=/tmp/gerenciador-teste.db uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Para ver a sincronia use **dois aparelhos** (ou dois navegadores) na mesma URL. Cadastre os 8 jogadores da tabela da US3 (Ana 90 M, Bia 85 M, Caio 70 H, Davi 65 H, Eva 60 M, Fabio 55 H, Gil 40 H, Helo 30 M), abra a **Sessão**, marque-os na ordem e **sorteie** (alvo 12) e **confirme** — você deve ver: Time 1 Ana + Gil, Time 2 Bia + Fabio, Time 3 Caio + Helo, Time 4 Davi + Eva.

## Passos e observações

1. **Painel inicial:** com a rodada em andamento → **Passa:** "Rodada 1 · alvo 12", blocos **Quadra do placar**, **Próxima partida** (Time 1 × Time 2), **Fila (2)** (1º Time 3, 2º Time 4), **Reis (0)** e **Eliminados (0)** com os textos vazios, e **Chamar partida** desabilitado com "Vincule uma quadra do placar…".
2. **Criar e vincular:** toque **Criar quadra e vincular** → **Passa:** "Quadra NNNNN (Quadra do dia): disponível" e o link **Abrir o placar**; **Chamar partida** habilitado. Abra o link em outra aba (o navegador é o admin dessa quadra).
3. **Chamar partida:** toque **Chamar partida** → **Passa:** o título vira "Partida em quadra" com o selo "chamada", o botão fica desabilitado ("Já há uma partida chamada…"), e **na aba do placar, sem recarregar**, aparecem as duplas **"Ana + Gil" × "Bia + Fabio"**, alvo 12 e 0 × 0.
4. **Proteção:** no placar, marque 1 ponto; no gerenciador **Cancelar rodada**, sorteie, confirme e tente **Chamar partida** de novo na mesma quadra → **Passa:** recusado com "tem uma partida em andamento (1 × 0): encerre ou reinicie no placar antes"; o placar continua 1 × 0. (Encerre/reinicie a partida no placar e a chamada passa a funcionar.)
5. **Quadra indisponível:** reinicie o servidor (o banco das quadras é efêmero) → **Passa:** a rodada, o vínculo e a partida continuam gravados, mas a quadra aparece "indisponível — vincule de novo"; **Criar quadra e vincular** (ou **Vincular** com o código de outra) resolve.
6. **Vincular por código:** digite `00000` → erro "não encontrada ou expirada"; digite o código de uma quadra real → vincula. **Desvincular** funciona antes de chamar a partida e fica bloqueado depois (a partida chamada precisa ser encerrada, na US6).
7. **Sincronia (dois aparelhos):** com os dois na tela da sessão (selo **Ao vivo**), em um deles marque/desmarque presença, sorteie, confirme e cancele → **Passa:** o outro acompanha **sozinho**, em poucos segundos, sem tocar em "Atualizar". Desligue o Wi-Fi de um e religue → o selo passa por "Reconectando…" e volta a "Ao vivo" com o estado atual.
8. **Time incompleto:** com 5 presentes (ímpar) o time incompleto é o último da fila; enquanto não chega a vez dele nada muda. (O bloqueio "escolha o parceiro" aparece quando ele entra em quadra, o que exige resultados — US6/US8.)
9. **Persistência:** reinicie o servidor com `RESET_DB_ON_STARTUP=true` → **Passa:** sessão, rodada e partida chamada continuam (a quadra do placar não).
10. **APK:** os botões "Sessão" e "Jogadores" continuam ausentes.

**Falha:** placar mostrando nomes errados, partida zerada sem pedir, aparelho que só atualiza ao recarregar, ou segredo visível na URL do WebSocket (confira no navegador: `/ws/gerenciador` sem parâmetros).

## Observação sobre o painel

"Reis" e "Eliminados" aparecem vazios porque os resultados só passam a ser registrados na **US6**. A derivação já está pronta e testada com resultados sintéticos.

## Evidência automatizada

`uv run pytest` (552; 33 novos: derivação do rei da quadra, vínculo, chamada com placar real, recusa com pontos, quadra sumida, compensação de falha, concorrência, migração 4→5, WebSocket com autenticação e difusão), `npm test` (182), `npm run check`, `npm run test:e2e` (73, com axe no painel e dois aparelhos sincronizando).
