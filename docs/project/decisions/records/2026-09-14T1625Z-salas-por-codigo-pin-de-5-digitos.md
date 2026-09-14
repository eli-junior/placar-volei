---
status: Decided
raised: 2026-09-14
decided: 2026-09-14
deciders:
  - Navigator
  - Driver
supersedes:
  - 2026-09-13T2005Z-arenas-como-agrupador-de-quadras.md
related:
  - CV1.DS1.US1
---

# Salas por Código PIN de 5 Dígitos e Simplificação de Entrada

## Question

Como simplificar a experiência de criação e ingresso em placares, eliminando o atrito do modelo hierárquico complexo de Arenas e Quadras?

## Decision

Substituir o fluxo de seleção hierárquica por um modelo direto baseado em salas com código PIN numérico aleatório de 5 dígitos (`10000` a `99999`):

1. **Entrada Direta em Duas Opções:** Ao abrir a aplicação, o usuário escolhe entre **Criar novo placar** ou **Acompanhar**.
2. **Criador é Admin:** Ao criar a sala com um apelido, um código numérico de 5 dígitos é gerado, exibido com destaque no topo da tela, e o criador é registrado imediatamente como `ADMIN`.
3. **Ingresso Rápido como Espectador:** Para acompanhar, qualquer pessoa digita o código de 5 dígitos e um apelido, ingressando imediatamente como `ESPECTADOR`.
4. **Ciclo de Vida Efêmero (TTL de 1 hora):** Salas sem atualização por mais de 1 hora são eliminadas automaticamente em cascata (partidas, eventos e participantes).
5. **Limites de Proteção:** Teto máximo de 20 quadras simultâneas ativas e teto máximo de 20 participantes por quadra.
6. **Banco de Dados Efêmero entre Deploys:** O banco SQLite não é persistido entre deploys (volume removido de `docker-compose.yml` e `Dockerfile`). Além disso, ao inicializar uma nova versão da aplicação, o banco de dados anterior é detectado via tabela `app_meta` e automaticamente apagado e recriado limpo.

## Rationale

- O modelo hierárquico anterior (Criar Arena -> Escolher Arena -> Criar Quadra -> Entrar na Quadra) trazia atrito cognitivo e operacional para uma partida amadora casual.
- Um PIN numérico curto (5 dígitos) é fácil de falar em voz alta na quadra ("entra na sala 48291") ou enviar por mensagem instantânea.
- A eliminação por inatividade após 1h preserva a saúde e leveza do banco SQLite local no Mini PC sem necessidade de manutenção manual.
- Como as partidas são efêmeras (pelada casual), não há necessidade de reter histórico de bancos antigos entre versões do software.

## Options Considered

- **Manter Arenas como passo obrigatório:** Rejeitado pelo Navigator por ser excessivamente burocrático para uso casual.
- **Códigos alfanuméricos longos / UUIDs na URL:** Rejeitados por serem difíceis de digitar manualmente em celulares.
- **PIN de 4 dígitos:** 10.000 números teria maior risco de colisão e adivinhação aleatória; 5 dígitos (`10000` a `99999`) fornece 90.000 opções com excelente margem para 20 salas simultâneas.
- **Manter volume persistente do SQLite entre deploys:** Rejeitado pelo Navigator. Nova versão deve descartar o banco anterior e iniciar limpa.

## Consequences

- A tela inicial (`HomePlacar.svelte`) se torna o ponto de entrada único.
- O topo da sala exibe com destaque o código numérico e atalho para copiar.
- O banco SQLite é recriado do zero a cada nova versão e não fica preso em volumes Docker.
- Endpoints legados de arenas são mantidos em segundo plano apenas para compatibilidade com testes anteriores.
