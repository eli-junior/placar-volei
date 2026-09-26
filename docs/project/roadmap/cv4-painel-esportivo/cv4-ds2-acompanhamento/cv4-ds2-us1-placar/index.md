---
code: CV4.DS2.US1
level: User Story
status: Active
status_reason: branch criada da master 0.13.2; plano da implementação pronto para o Checkpoint 1
updated: 2026-09-26
effort: 7
---

# CV4.DS2.US1 — Placar do espectador em qualquer tela

## Intent / Scope

Entrega E2 — seção 7 do [plano detalhado](../../plan.md). A seção correspondente contém escopo, tarefas com esforço individual, arquivos prováveis, decisões, riscos, limites e ponto seguro de pausa.

**Esforço estimado:** 7/10. Não equivale a prazo em dias.

## Dependências

CV4.DS1.US1 aceita e integrada.

## Acceptance / Done Condition

Given espectador; When pontuar, corrigir ou redimensionar; Then o placar permanece legível e completo, com estado preservado e metadados secundários.

### Comportamentos verificáveis

- **Given** espectador em uma partida, **When** abre a sala, **Then** os pontos ocupam a maior área visual e nome, código e regras permanecem compactos.
- **Given** placar entre 0 e 999 e equipes com nomes longos, **When** a largura ou altura muda, **Then** nenhum dígito é truncado, sobreposto ou substituído por reticências.
- **Given** Fold fechado, aberto ou girado, **When** o navegador redimensiona a área visível, **Then** sala, sessão, resultado e inversão local permanecem iguais sem recarregar.
- **Given** ponto ou desfazer, **When** o resultado muda, **Then** a leitura atual tem prioridade, a mudança recebe feedback curto e movimento reduzido elimina animação não essencial.
- **Given** os lados invertidos localmente, **When** o placar atualiza, **Then** as mesmas equipes continuam associadas às suas cores e o servidor não recebe mudança de lado.

## Plano de implementação

1. Criar uma representação visual reutilizável do resultado, separada de comandos e do estado da sala. Ela recebe equipes, pontos, vencedor, inversão e preferência de movimento; não conhece WebSocket nem permissões.
2. Reformular `PlacarManual.svelte` como composição esportiva do espectador, removendo cavalete, argolas e cartões dobráveis dessa superfície. `CartaoDobravel.svelte` permanece intacto porque outros papéis ainda podem depender dele até a E4.
3. Escalar números Teko 600 pela área disponível, combinando largura e altura. Reservar espaço simétrico para 1–3 dígitos e limitar nomes sem permitir que empurrem ou reduzam o resultado de forma imprevisível.
4. Compactar identificação da sala e regras no topo do placar. Em retrato estreito, permitir quebra controlada dos metadados; em paisagem e Fold aberto, usar faixa única quando houver espaço.
5. Preservar inversão local e ações existentes de inverter lados e abrir linha do tempo. Os controles continuam seguindo o comportamento imersivo atual; fullscreen real permanece para `CV4.DS2.US2`.
6. Adicionar feedback de ponto/desfazer com duração curta e `prefers-reduced-motion`. Incluir uma região acessível que anuncie apenas mudanças relevantes, sem repetir a cada renderização.
7. Cobrir composição e contratos com testes de componente/fonte existentes e executar a rota V2 com dados extremos, temas e redimensionamentos.

## Decisões de design

- O painel esportivo substitui a metáfora de placar de folhas apenas para o espectador nesta história. O componente antigo não será removido enquanto consumidores futuros não forem migrados.
- Ciano e laranja continuam exclusivos das equipes; ações usam tokens neutros ou de marca.
- A pontuação não terá molduras físicas, argolas ou brilho pesado. Contraste, tamanho e cor identificam o resultado.
- CSS responde ao contêiner e à área visível; JavaScript continua responsável apenas pela medição já necessária ao giro por software e pela detecção da mudança de pontos.
- A primeira versão mantém duas equipes lado a lado mesmo no Fold fechado. Empilhamento vertical dificultaria comparar o resultado e mudaria a leitura aprovada.

## Riscos e mitigação

- **Altura reduzida pelas barras do navegador:** a escala usa o menor limite entre largura e altura e preserva uma margem mínima para controles.
- **Três dígitos:** ambas as equipes reservam colunas simétricas e usam redução contínua, sem corte.
- **Nome longo:** nome pode truncar com título/label acessível; pontuação nunca trunca.
- **Transição entre Fold fechado e aberto:** nenhum estado de jogo ficará no componente visual; remontagem ou recalculo não altera sessão.
- **Animações concorrentes em pontos rápidos:** a mudança mais recente substitui a anterior; o valor atual sempre é renderizado imediatamente.

## Fora do escopo desta história

- Solicitar ou detectar fullscreen do navegador.
- Redesenhar controles de admin/controlador.
- Alterar APIs, WebSocket, permissões, regras esportivas ou Wear OS.
- Migrar todas as janelas auxiliares ou quitar a matriz transversal de acessibilidade.

## Arquivos previstos

- `web/src/components/PlacarManual.svelte`
- `web/src/components/PlacarResultado.svelte` (novo, se a separação se confirmar durante a implementação)
- `web/src/components/SalaQuadra.svelte` apenas para integração/semântica necessária
- `web/src/app.css` somente se faltarem tokens semânticos
- `web/tests/` para regressões de representação, redimensionamento e movimento reduzido

## Validation Route

Executar V2 no [guia de validação](../../test-guide.md), além das verificações obrigatórias transversais. Registrar resultados reais e aceite físico do Navigator.

## Estado para retomada

- Branch de implementação: `feature/cv4-ds2-us1-placar-espectador`, base `42f514d` (`origin/master`, versão 0.13.2).
- Último checkpoint aprovado desta história: nenhum.
- Implementação: não iniciada.
- Próxima ação: obter aprovação do Checkpoint 1; depois implementar até o Checkpoint 2 sem incorporar fullscreen ou controles de operação.
- Atualizar este arquivo, changelog e [handoff](../../handoff.md) ao assumir ou interromper.

## Out of Scope

Respeitar os limites da seção correspondente do plano. Não incorporar mudanças no motor de eventos, permissões ou Wear OS sem novo acordo.
