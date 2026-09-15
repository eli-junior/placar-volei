---
code: CV2.DS4
level: Delivery Story
status: Planned
status_reason: Registrado no backlog para execução futura
updated: 2026-09-15
related:
  - docs/project/briefing.md
  - docs/project/roadmap/cv2-experiencia-na-quadra-e-confiabilidade/index.md
---

# CV2.DS4 — Celebração de Vitória, Microcopy e Compartilhamento

## Intent

Conferir acabamento esportivo de alto padrão ao placar, com celebração vibrante do resultado da partida, microcopy natural em português de quadra, facilidade de compartilhamento por link/QR e suporte a instalação como PWA.

## Scope

- **US1 — Tela de Vitória Celebrada e Memorável (M21, §11.7):** Ao fim do jogo, ocultar controles operacionais e renderizar celebração com troféu, cores do time campeão, resumo estatístico (duração e pontos totais), vibração festiva e botões para \"Nova Partida\" e \"Compartilhar Resultado\".
- **US2 — Padronização de Modais e Sheets com `<dialog>` (M2, §11.10):** Unificação de todos os diálogos da aplicação (linha do tempo, regras, entrada) sob a tag nativa `<dialog>`, garantindo retenção de foco (focus trap), fechamento por tecla `Esc` e clique no backdrop com blur.
- **US3 — Ícones Vetoriais SVG Lucide (M22, §10.5):** Substituição de emojis de texto por ícones SVG com renderização uniforme em todas as plataformas (Android, iOS, Windows, Mac).
- **US4 — Revisão Geral de Microcopy e Linguagem de Quadra (§12, M14, M15):** Adequação dos textos em todo o app (remoção de termos técnicos como \"append-only\", mensagens de erro inline próximas aos campos e suporte a tecla Enter/\"Ir\" no teclado móvel).
- **US5 — Compartilhamento por Link, QR Code e Open Graph (B1, B2, B3):** Integração com a Web Share API (`navigator.share`) para compartilhamento direto da URL `/quadra/{id}`, geração de modal com QR Code da sala e tags Open Graph dinâmicas para prévia no WhatsApp.
- **US6 — Instalação PWA e Otimização de Fontes (B4, B10, B11):** Manifesto web, ícones adaptativos para tela inicial, self-hosting das fontes Teko e Inter (subset latin) e headers de cache imutável de assets.

## Acceptance / Done Condition

- Encerramento do jogo comemora o vencedor com a identidade visual do time campeão e dados da partida.
- Compartilhamento de sala copia o link completo ou aciona a folha de compartilhamento nativa do sistema operacional.
- Aplicação pode ser adicionada à tela inicial de dispositivos móveis com inicialização em modo standalone.
- Todos os modais possuem comportamento nativo de foco e acessibilidade por teclado.

## Validation Route

- Simulação de fim de partida até a condição de vitória e conferência da tela de celebração.
- Teste da Web Share API e leitura do QR Code gerado com câmera de smartphone.
- Inspeção de Lighthouse PWA e verificação do funcionamento offline do shell da aplicação.
