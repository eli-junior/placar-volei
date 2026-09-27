# Plano — CV6.DS2.US1

## Checkpoint 1 — aguardando aceite

- Nível: User Story (HU), dentro de CV6.DS2.
- Branch: `feature/cv6-ds2-us1-leitura-no-pulso`, criada de `master` `c02285b`, sincronizada com `origin/master`.
- Driver: Codex | Sessão: cv6-ds2-us1-20260927 | Data: 2026-09-27 14:21 -03.
- Versão proposta: 0.20.1 (patch de legibilidade da capacidade existente), confirmada no fechamento.

## Escopo e aceite

1. Dado controle fora do relógio, exibir exatamente “Controle no telefone.”, mantendo o bloqueio de pontuação.
2. Dado placar com 0, 12 ou 100 pontos, elevar rótulos e ampliar números sem cortar a borda circular ou invadir as ações inferiores.
3. Com permissão de batimentos, centralizar o indicador no topo e ampliá-lo; sem leitura, manter “♥ --”; sem permissão, manter o indicador oculto.
4. Preservar desfazer, nova partida, indicação de pendências, avisos de conflito e transição dos números.

## Desenho e decisões propostas

- Ajustar `ScoreScreen.kt`: hoje números usam 58 sp e batimentos 13 sp; o batimento divide uma Row com a bolinha, o que desloca seu centro. Separar seu alinhamento do indicador de conexão, reservando espaço para ambos.
- Dimensionar o placar pela área disponível, incluindo três dígitos e fonte ampliada do sistema. Evitar aumentar indiscriminadamente valores fixos, que pode cortar 100 ou sobrepor a faixa inferior.
- Encurtar a mensagem em `ScoreSync.controlReason`; preservar prioridade de avisos de fila retida e demais estados de bloqueio.
- Avaliar Teko, usada no web em WOFF2. Não há licença nem recurso de fonte Android na pasta do relógio. Verificar fonte original, licença de redistribuição e renderização antes de incorporá-la; se não houver evidência suficiente, manter a fonte atual e registrar o resultado da avaliação. Paridade tipográfica não é condição de aceite desta HU.
- Manter rótulos existentes (Nós/Eles ou iniciais de jogadores).

## Fora do escopo

Aro de conexão (US2), novo retorno sonoro/háptico (US3), repouso/retomada (US4), revisão de conflitos do CV3, alterações de permissões, regras e coleta de saúde.

## Verificação e rota do Navigator

- Executar testes JVM, `assembleDebug` e `lintDebug` com o JDK 21 e SDK descritos em `wear/README.md`.
- Cobrir a mensagem de controle e manutenção do bloqueio nos testes de ScoreSync; executar regressões existentes de batimentos, fila e pontuação.
- Preparar APK e roteiro de instalação no Checkpoint 2, com capturas comparáveis quando houver aparelho/emulador disponível.
- Usar relógio real e dois clientes web para alternar controle e observar papéis (três clientes). Conferir 0, 12 e 100; com jogadores e sem jogadores; permissão de sensor concedida/negada e leitura indisponível.
- Com treino Samsung Health ativo, conferir batimento e continuidade do treino. Validar desfazer e nova partida ao encerrar, números animados e animações desativadas no sistema, além de fonte ampliada.
- Desconectar o relógio por cerca de 30 s, conferir indicação de pendências e retorno ao placar confirmado sem sobreposição.
- Aprova: leitura melhor, mensagens corretas, ações acessíveis e telas concordantes. Falha: recorte, sobreposição, leitura inventada, ação bloqueada indevidamente ou divergência de placar.

## Riscos e coerência

- Dimensões finais exigem aceite no relógio físico; build e testes JVM não provam legibilidade.
- README/changelog indicam CV3.US4 como próximo trabalho; a escolha desta HU é proposta neste checkpoint e não encerra aquela pendência.
- Briefing está desatualizado sobre versões e HUs entregues. Atualizar o foco e contexto pertinente na fase documental, preservando o histórico.
- O guia contém commit ao final e também exige commits parciais para sync contínuo. Aplicar a seção específica Commit and Release Rules para salvar planejamento na branch; merge somente após Checkpoint 4.
- O guia pede persistência após restart e também determina reset do banco em produção. Esta HU valida reconexão do cliente; não usará restart destrutivo do servidor como prova de persistência.

## Documentação prevista

Atualizar HU/DS/CV, changelog, roteiro de validação e documentação pertinente do relógio na mesma entrega. Avaliar README/briefing no check de coerência. Nenhuma implementação foi alterada no planejamento.
