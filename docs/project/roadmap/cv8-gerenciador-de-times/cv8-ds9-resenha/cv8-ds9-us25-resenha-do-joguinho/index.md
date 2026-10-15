---
code: CV8.DS9.US25
level: User Story
status: Validated
status_reason: tela aprovada pelo Navigator em 2026-10-15 ("ficou legal"), que pediu os cartões e o botão de imagens e autorizou revisão e docs; o compartilhar no Android físico não foi observado
updated: 2026-10-15
related:
  - plan.md
  - test-guide.md
  - ../../regras-de-negocio.md
  - ../../../../decisions/records/2026-10-15T1800Z-resenha-do-joguinho.md
---

# Resenha do Joguinho

## Intent

Uma página de estatísticas divertida, que favoreça a resenha, para mandar no grupo do WhatsApp depois da partida: prêmios com zoeira, a foto de cada jogador com um título positivo ou negativo, campeões e a tabela do dia.

## Acceptance

Dado um joguinho com partidas encerradas (aberto ou o último encerrado)
Quando o operador abre **Joguinho → Resenha**
Então vê cartões 4:5 com capa e rei do dia, prêmios, galeria e tabela, que batem com as partidas do dia (RN-19)
E um prêmio sem dado não aparece
E **Baixar N imagens** salva um PNG de 1080 × 1350 por cartão, e **Mandar no grupo** abre o compartilhar do sistema com as imagens, quando o aparelho suporta.

Roteiro de validação: [test-guide.md](test-guide.md). Plano e desvios: [plan.md](plan.md).

## Out of Scope

Ranking entre sessões, escolher uma sessão antiga, página pública para o grupo, estatística ponto a ponto (os eventos das quadras expiram) e a Resenha dentro do APK.
