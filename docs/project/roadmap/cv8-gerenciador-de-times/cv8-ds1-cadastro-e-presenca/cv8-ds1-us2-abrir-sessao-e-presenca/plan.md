# Plano — CV8.DS1.US2 Abrir sessão e marcar presença

Nível: User Story. Branch: `feature/cv8-ds1-us2-abrir-sessao-e-presenca`. Versão-alvo: **0.33.0** (minor; backend, web e APK por consistência de versão; Wear inalterado).

## Escopo

**Sessão** (um dia de jogo)
- Tabela `sessoes (id, aberta_em, encerrada_em)` no `gerenciador.db` (schema 2 → 3, migração aditiva). Índice único parcial garante **no máximo uma sessão aberta** (`WHERE encerrada_em IS NULL`), inclusive sob corrida.
- Abrir com outra aberta → 409 ("Já existe uma sessão aberta"). **Encerrar sessão** (extra necessário: sem ele o CA1 deixaria o sistema preso numa sessão aberta para sempre) fecha a sessão e limpa a tela; presenças ficam gravadas.

**Presença e ordem de chegada** (RN-13, RN-15)
- Tabela `presencas (sessao_id, jogador_id, ordem, marcado_em)`, chave `(sessao_id, jogador_id)`.
- Marcar presença = entra **no fim** (`ordem = max + 1`); desmarcar apaga a linha e **recompacta** a ordem; marcar de novo vai para o fim. Só jogadores **ativos**.
- **Reordenar** a fila de chegada a qualquer momento: `PUT` com a lista completa e ordenada de jogadores presentes (validada: mesmos jogadores, sem repetição), gravada de forma atômica. Na tela: botões **subir / descer** por linha (acessíveis, sem arrastar). O travamento "só antes do sorteio" (RN-15) entra com a US-03, que é quem cria o sorteio.
- **Cadastro rápido inline:** formulário curto na tela da sessão (nome e sobrenome, gênero, nota opcional) que cria o jogador pelas mesmas regras da US1/US15 e já o marca presente, no fim da fila. Foto continua na tela de Jogadores.
- Contador de presentes com o aviso do mínimo (RN-11: "faltam N para poder sortear"). O bloqueio de fato do sorteio é da US-03.

**API** (`/api/sessao`, todas com `OWNER_SECRET`, como a base de jogadores)
- `GET /api/sessao` → `{sessao: {...}|null, presentes: [{...jogador, ordem, marcado_em}], ausentes: [jogadores ativos fora da sessão]}`.
- `POST /api/sessao` (abrir), `POST /api/sessao/encerrar`.
- `PUT /api/sessao/presencas/{jogador_id}` (marcar), `DELETE` (desmarcar), `PUT /api/sessao/ordem` (corpo `{jogador_ids: [...]}`), `POST /api/sessao/presencas/rapido` (corpo como o cadastro; devolve o jogador e a posição).
- Sem sessão aberta, marcar/desmarcar/reordenar → 409.

**Interação com a US1/US15:** inativar um jogador presente na sessão aberta o **remove da presença** (recompactando a ordem); reativar não o recoloca.

**Web**
- Nova tela `/sessao` (botão "Sessão" na Home, ao lado de "Jogadores"; oculta no APK), com a mesma proteção por segredo. O formulário de segredo hoje mora dentro de `Jogadores.svelte`: extraio para um componente `PortaoSegredo.svelte` usado pelas duas telas (refatoração pequena, sem mudar comportamento).
- Estados: sem sessão (botão "Abrir sessão"); com sessão (lista de presentes numerada com foto/iniciais, nota, botões subir/descer/desmarcar; lista de ausentes com botão "Presente"; cadastro rápido; "Encerrar sessão" com confirmação).

## Aceite (BDD)

- Given nenhuma sessão aberta, When abro a sessão, Then a tela mostra a sessão vazia; Given uma aberta, When tento abrir outra, Then é recusado.
- Given jogadores ativos, When marco Ana, Bia e Caio nessa ordem, Then a lista mostra 1 Ana, 2 Bia, 3 Caio.
- Given Ana presente em 1º, When a desmarco e marco de novo, Then ela vai para o fim e os demais sobem.
- Given três presentes, When subo/desço um deles, Then a ordem muda e persiste ao recarregar.
- Given um nome que não está na base, When uso o cadastro rápido, Then o jogador é criado (nota 60 se vazia) e já aparece presente no fim.
- Given 3 presentes, Then a tela indica que falta 1 para o mínimo de 4; com 4 o aviso some.
- Given um presente, When ele é inativado na tela de Jogadores, Then sai da presença e a ordem se recompacta.
- Given o servidor reiniciado (inclusive com `RESET_DB_ON_STARTUP=true`), Then a sessão aberta, as presenças e a ordem continuam.
- Given a tela dentro do APK, Then continua oculta.

## Testes

- pytest: uma sessão aberta por vez (inclusive duas aberturas concorrentes), marcar/desmarcar/recompactar, reordenar válida e inválida, só ativos, rápido (validações da US15 valem), inativar remove presença, sem sessão → 409, sem segredo → 404, migração 2→3 preservando dados, persistência após reset.
- `npm test`: cliente da sessão e função pura de mover posição.
- Playwright: fluxo completo (abrir, marcar, reordenar, rápido, aviso do mínimo, encerrar) e axe.

## Alternativas rejeitadas

- **Arrastar para reordenar:** pior acessibilidade e mais código; botões subir/descer bastam em celular.
- **Guardar a ordem como horário de chegada apenas:** a reordenação manual (RN-15) exigiria sobrescrever horários; uma coluna `ordem` explícita é mais simples e fiel.
- **Sessão sem encerramento (fecha sozinha à meia-noite):** esconde estado; o botão é explícito e reversível por abrir outra.
- **Presença como lista dentro da sessão (JSON):** impediria a chave única e as consultas das próximas histórias.

## Fora do escopo

Sorteio, rodadas e fila de jogo (DS2/DS3); travar a reordenação depois do sorteio (US-03); **sincronização em tempo real entre dispositivos** (WebSocket é a US-05, DS3 — por ora a tela tem "Atualizar" e recarrega ao voltar o foco); histórico de sessões (US-12); foto no cadastro rápido.

## Pontos para o Navigator confirmar

1. **Encerrar sessão** entra nesta história, mesmo não estando nos CAs, porque o CA1 sem ele trava o sistema.
2. **Inativar presente remove da presença** (em vez de bloquear a inativação).
3. **Dois aparelhos na mesma sessão** veem o mesmo estado ao atualizar, mas sem sincronia automática até a US-05; quem opera durante a rodada (RN-12, "qualquer dispositivo") ainda exigirá o `OWNER_SECRET`. Aceita assim por ora?

## Riscos

- Corrida de duas aberturas: coberta pelo índice único parcial + teste.
- Migração 2→3 é aditiva (tabelas novas), sem tocar nos jogadores.
