# Plano — CV6.DS2.US2

## Checkpoint 1 — aprovado pelo Navigator

- Nível: User Story (HU), dentro de CV6.DS2.
- Branch: `feature/cv6-ds2-us2-aro-de-conexao`, criada de `origin/master` `290a36c`.
- Área separada: `/tmp/placar-cv6-ds2-us2`; preserva a área da US1 e o trabalho web simultâneo.
- Driver: Codex | Sessão: cv6-ds2-us2-20260927 | Data: 2026-09-27 14:53 -03.
- Versão: patch de apresentação da conexão. Candidata 0.20.2 se a US1 fechar como 0.20.1 antes da próxima minor. O web já registra alvo 0.21.0; confirmar número no fechamento sem rebaixar versão nem publicar versão concorrente.

## Escopo

Substituir a bolinha do placar por um aro fino completo na borda da tela. Preservar batimentos centralizados, quantidade de lances pendentes, descrição acessível do estado e áreas de toque.

## Desenho proposto

- Desenhar aro sobre o placar, com traço inicial de 2 dp e margem de 1 dp além da metade do traço; acomodar conteúdo dentro da borda. Aro circular em mostrador redondo; contorno da tela em mostrador retangular.
- Verde (`#4CD964`): conectado sem pendências. Amarelo (`#FFC83D`): reconectando ou enviando lances. Vermelho (`#FF4D4D`): sem conexão, inclusive se houver pendências.
- Reaproveitar `signal(connection, pending)` e `statusLine` existentes; não criar estado paralelo que possa divergir do transporte.
- Transição curta de cor, cerca de 150 ms, respeitando animações desativadas; sem pulsação contínua. Traço fino dá discrição sem reduzir a legibilidade com opacidade excessiva.
- Retirar bolinha e espaçador simétrico da US1. Batimentos continuam no centro. Quando houver fila, exibir contagem textual compacta em área própria no cabeçalho; reservar espaço e medir para não sobrepor batimentos. Sem fila, não reservar um novo indicador permanente.
- Nome acessível com estado e quantidade exata de pendentes. A camada gráfica não recebe gestos e não bloqueia pontuação, Voltar Ponto ou Nova.
- Preferir desenho nativo no Compose: não exige imagens nem dependências. Remover toda indicação de pendências foi rejeitado porque apagaria informação operacional já existente.

## Aceite

1. Dado o placar visível, o aro acompanha toda a borda, sem recorte nem sobreposição de números, batimentos ou ações.
2. Dada conexão saudável sem fila, o aro é verde. Ao reconectar/enviar, amarelo; sem conexão, vermelho. Cor deriva do estado real já reconhecido pelo cliente, sem promessa de detecção instantânea de perda silenciosa.
3. Dada fila com 1, vários ou mais de 9 lances, a existência e quantidade continuam consultáveis visualmente e por leitor de tela.
4. Com TalkBack, o estado é identificado sem depender apenas da cor. Com animações desativadas, a cor atual permanece compreensível.
5. Marcar, Voltar Ponto e Nova mantêm seu comportamento, incluindo confirmação em dois toques para Nova.

## Implementação prevista

- `ScoreScreen.kt`: substituir StatusDot por aro e contagem textual, integrar com o layout da US1.
- Testes de estado em `ScoreboardTest.kt`: verificar prioridade de desconexão, reconexão, pendências e descrições acessíveis.
- Investigar o estado de transporte só se a validação mostrar indicação incorreta. Se exigir mudança de transporte além da correção necessária, registrar bloqueio/escopo para o Navigator.

## Validação planejada

- Testes JVM, APK debug/release e lint Android; regressão exigida pelo guia local.
- Relógio real e telefone na mesma quadra: conferir aro completo e discreto com 0, 12 e 100 pontos, batimentos presentes/ausentes e fim de partida.
- Isolar rede por cerca de 30 s (incluindo Wi-Fi/Bluetooth quando aplicável), observar vermelho após detecção, registrar lances pendentes, restabelecer rede e conferir amarelo durante envio e verde após confirmação.
- Conferir o mesmo placar e um efeito por lance no telefone. Não reiniciar servidor: o reset do banco é deliberado e não prova reconexão do relógio.
- Testar TalkBack, animações desativadas e fonte ampliada. Conferir 1 e mais de 9 pendências e que a camada do aro não intercepta os botões.
- Aprova: aro completo, estados coerentes, contagem acessível e operação preservada. Falha: conexão saudável indicada após falha reconhecida pelo transporte, sobreposição, corte ou toque bloqueado.
- No Checkpoint 2, entregar comandos de instalação, APK, capturas e roteiro executável com observações por cliente. Aceite manual permanece do Navigator.

## Dependência e estado da HU anterior

A US1 está em `feature/cv6-ds2-us1-leitura-no-pulso`, último commit `90fc088`, instalada no relógio e sincronizada. Checkpoint 2 da US1 aceito pelo Navigator junto da aprovação deste plano. A US1 está em revisão no Checkpoint 3; ainda depende do fechamento no Checkpoint 4.

Esta branch nasce da master conforme o contrato. Antes de implementar sobre o novo layout, concluir os checkpoints da US1 e atualizar esta branch com a master que a integrar. Não copiar silenciosamente a implementação anterior nem fazer merge da US1 em master sem aceite. Planejamento da US2 aprovado; implementação aguarda essa integração.

## Fora do escopo

Som/retorno de pontuação (US3), repouso e execução em segundo plano (US4), revisão de conflitos do CV3, regras e permissões, mudanças na interface web.

## Documentação e coerência

Atualizar HU/DS, changelog e roteiro no mesmo ciclo; avaliar README do relógio por descrever a bolinha. Reconciliar foco do README/briefing e versão com o trabalho web na fase documental. Preservar todos os registros de outras branches no changelog.
