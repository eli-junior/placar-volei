---
status: Decided
raised: 2026-09-13
decided: 2026-09-13
deciders:
  - Navigator
supersedes:
related:
  - CV1.DS2
---

# Sucessão automática de admin após 2 minutos offline

## Question

Quem administra a quadra quando o admin fecha o navegador, fica sem bateria ou perde conexão no meio da partida?

## Decision

Após **2 minutos** de admin offline, o sistema promove automaticamente **o controlador online há mais tempo** na quadra. A promoção gera evento `ADMIN_SUCEDIDO`, visível na linha do tempo.

O admin original, ao voltar, retorna como **controlador**. Não retoma o posto automaticamente.

Se não houver nenhum controlador online, a quadra segue sem admin: controladores existentes continuam pontuando e qualquer controlador pode alterar a configuração enquanto o posto estiver vago.

## Rationale

A partida não pode travar por ausência de uma pessoa. Dois minutos é longo o bastante para absorver queda momentânea de Wi-Fi e curto o bastante para não interromper o jogo.

Não devolver o posto automaticamente evita alternância de admin a cada oscilação de rede. Se o retorno ao posto for necessário, existe o owner takeover.

## Options Considered

- **Admin permanece dono da sessão indefinidamente** — rejeitado: bateria acabou, quadra fica sem configuração.
- **Quadra sem admin até ele voltar** — rejeitado pelo mesmo motivo; mantido apenas como caso degradado quando não há controlador online.

## Consequences

- Exige heartbeat/presença por WebSocket com detecção de desconexão.
- Exige ordem de chegada dos controladores registrada na quadra.
- A configuração da quadra é editável por controlador **apenas** enquanto o posto de admin estiver vago.

## Review Trigger

Se o grupo relatar trocas de admin indesejadas, reavaliar o limite de 2 minutos ou exigir confirmação humana antes da promoção.
