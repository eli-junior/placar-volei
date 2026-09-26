# Handoff — CV4 Painel esportivo

## Estado em 2026-09-26

- **Responsável pelo planejamento:** Codex (Driver), sessão `01a0dd8e-b3b3-7482-a278-5f22f9738d3e`.
- **Branch documental:** `codex/plano-cv4-painel-esportivo`.
- **Base:** `origin/master` em `ab2cedb` (release registrada 0.11.0).
- **Checkout do planejamento:** `C:/Users/eli/.codex/worktrees/plano-painel-esportivo/placar_volei`.
- **Checkout original preservado:** `D:/projetos/placar_volei`, na branch do relógio; não trocar sua branch nem presumir que está atualizado.
- **Passo Ariad:** 2 — Planejamento. **Checkpoint 1 de implementação: pendente.**
- **Implementação de aplicação:** nenhuma. Todas as seis histórias permanecem `Planned`.
- **O que o Navigator aprovou:** direção de painel esportivo, prioridade dos números, Teko mais fina e maior, temas claro/escuro, início pela Home e manutenção do recolhimento automático de controles.
- **O que não aprovou ainda:** execução do plano, layout operacional do admin/controlador, entrega física, merge e publicação.

## Ordem de leitura para outro agente

1. `AGENTS.md` e contexto obrigatório do projeto, incluindo `docs/process/development-guide.md`.
2. [Plano](plan.md), [decisão visual](../../decisions/records/2026-09-26T1238Z-painel-esportivo-e-numeros-prioritarios.md) e [referências](references/README.md).
3. [E1 / CV4.DS1.US1](cv4-ds1-inicio/cv4-ds1-us1-home/index.md).
4. [Rota de validação](test-guide.md), especialmente preparação e V1.
5. Changelog da branch e estado remoto. Conferir se este handoff foi sucedido por atualização mais recente.

## Retomar na mesma máquina

No checkout do planejamento, executar operações de leitura primeiro:

```powershell
git status --short --branch
git fetch origin
git log -3 --oneline
git log -1 --oneline origin/master
```

Se houver mudanças não commitadas, inspecionar e preservar. Não resetar nem limpar a pasta para igualar ao remoto. Atualizar assinatura e estado ao assumir.

## Retomar em outra máquina/agente

Em clone do repositório, com diretório de destino disponível:

```powershell
git fetch origin
git worktree add -b codex/retomada-plano-cv4 ../placar-cv4-planejamento origin/codex/plano-cv4-painel-esportivo
```

Se essa branch/caminho já existir, inspecionar antes de escolher outro ou reutilizar; não excluir checkout existente. O comando cria uma branch local de retomada a partir do plano remoto, sem alterar o checkout de trabalho do usuário. Para continuar a branch canônica do plano, usar a branch já disponível/trackeada no checkout correspondente e sincronizar nela.

O plano e as referências estão no Git; não dependem dos PNGs temporários nem dos caminhos CrossDevice do usuário. Os HTMLs em `references/` são amostras documentais e não devem ser copiados para `web/src`.

## Próxima ação exata

**Apresentar/confirmar o Checkpoint 1 do plano e de E1. Não implementar enquanto estiver pendente.** O documento e a resposta desta sessão apresentam a superfície de planejamento; uma aprovação futura deve ser registrada com a data, a mensagem e a entrega liberada.

Depois da aprovação:

1. Confirmar `origin/master` e a situação de `origin/fix/entrar-na-quadra-pela-home`. Essa branch relata erro 409 por apelido em uso mostrado fora da área visível e está em planejamento na inspeção de 2026-09-26. Não assumir merge ou aceite.
2. Registrar/ajustar os limites da E1 e a decisão sobre testes de navegador conforme aprovação.
3. Integrar esta documentação em `master` somente com autorização de histórico documental. Se ainda não houver merge documental e for autorizado iniciar E1, criar branch de E1 a partir da master e trazer apenas os arquivos do plano necessários, registrando a origem; não partir da branch do relógio nem depender de código não aceito.
4. Criar branch própria sugerida `codex/cv4-ds1-us1-home` a partir da master atualizada. Dependências de código precisam estar aceitas e integradas antes de basear a entrega nelas.
5. Instalar dependências no checkout isolado, medir baseline, registrar E1 em implementação no changelog e implementar até o Checkpoint 2.
6. Atualizar o arquivo da história e este handoff a cada pausa; push frequente da branch de trabalho. Só merge em master após aceite final.

## Verificações desta etapa documental

- Leitura da implementação e documentos na base identificada.
- Direção visual recuperada das decisões explícitas do Navigator e das prévias.
- Nenhuma execução de teste de aplicação, browser real, Fold ou tablet atribuída a este plano.
- Verificação documental executada: 59 links relativos válidos, seis índices de história encontrados e JavaScript das duas referências HTML analisado sem erro de sintaxe. Conferência de whitespace e diff restrito a documentação/changelog no fechamento.
- Sincronização remota da branch será verificada no fechamento da sessão; consultar `git log` e upstream para obter o SHA final, evitando registrar um SHA do próprio commit dentro dele.

## Limites das referências

- As prévias usam dados fictícios; fullscreen é apenas uma simulação de composição.
- A fonte nas prévias vem do Google Fonts; a implementação precisa usar a fonte local existente.
- O ambiente da conversa fornece ícones e controles opcionais. Abrir os fragmentos diretamente pode omitir esses ícones; a especificação textual é autossuficiente.
- O protótipo usa escala só por largura e não foi validado fisicamente. A fórmula final deve tratar altura, zoom, teclado e três dígitos.
- O protótipo contém fluxo demonstrativo de criação e não é a especificação de permissões ou regras do produto.

## Coerência e concorrência

- README/changelog da base dizem 0.11.0; briefing e versões web/backend ainda dizem 0.10.1. Não “corrigir” essa diferença alterando o Wear OS. Rever no fechamento da próxima release e registrar a decisão.
- Correção da Home e nova partida rápida no relógio existem no remoto. Consultar seus registros antes de tocar arquivos comuns. Este plano não toma a propriedade dessas histórias.
- O contrato contém uma frase de commit ao final e outra regra explícita de commits parciais + push contínuo. Este ciclo usa a segunda para persistir documentos na branch, mantendo a restrição de merge/aceite. Não há dispensa de checkpoint da implementação.
- A documentação canônica Ariad não foi consultada; seguimos o contrato local. Não inferir uma diferença nova com o método canônico além das exceções já documentadas.

## Modelo de atualização ao interromper

```text
Agente / sessão / data:
História / branch / commit remoto:
Base utilizada:
Passo Ariad:
Último checkpoint explicitamente aprovado:
Trabalho concluído:
Arquivos pendentes / mudanças não commitadas:
Testes executados / resultados / evidências:
Validação física pendente:
Decisões e bloqueios:
Próxima ação exata:
Push confirmado / upstream:
```

Nunca marcar uma história `Done` só porque sua parte de código parece pronta. O próximo agente deve conseguir distinguir implementado, testado, validado pelo Navigator e integrado.
