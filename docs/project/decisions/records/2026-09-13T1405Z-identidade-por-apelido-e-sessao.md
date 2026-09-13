---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS1
  - CV1.DS2
---

# Identidade por apelido preso à sessão do navegador

## Question

Como identificar participantes sem transformar o MVP num sistema de autenticação?

## Decision

Ao entrar numa quadra, **todo** participante — admin, controlador ou espectador — informa um apelido. A identidade é presa à sessão do navegador (cookie HttpOnly com id de sessão opaco). Sem senha, sem cadastro, sem provedor externo.

Ninguém entra anônimo: quem não se registra não vê a quadra.

## Rationale

O uso é presencial e efêmero. As pessoas estão na mesma quadra e a fraude possível — fingir ser outro apelido — não tem consequência relevante. Exigir cadastro criaria atrito exatamente no momento em que o grupo quer começar a jogar.

Registro obrigatório para espectadores existe porque a lista de presentes tem valor: identifica quem pode ser promovido a controlador e dá contexto à linha do tempo.

## Options Considered

- **Cadastro com login e senha** — rejeitado para o MVP: custo de auth completa sem valor proporcional; reavaliável se surgir histórico por jogador.
- **Link de convite com papel embutido** — rejeitado: elimina identidade individual, e sem identidade a linha do tempo perde a autoria do ponto.

## Consequences

- A sessão é a credencial. Limpar dados do navegador perde o papel; a sucessão automática (`adr` de sucessão) cobre esse caso para o admin.
- Apelidos não são únicos globalmente; unicidade só dentro da quadra ativa.
- Reconexão precisa restaurar participante e papel a partir da sessão, sem reentrada manual.
- Não há dado pessoal armazenado além do apelido informado.

## Review Trigger

Se o produto passar a exigir histórico ou estatística por jogador entre partidas, esta decisão precisa ser revista.
