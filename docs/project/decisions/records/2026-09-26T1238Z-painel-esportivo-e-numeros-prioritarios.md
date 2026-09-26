---
status: Decided
raised: 2026-09-26
decided: 2026-09-26
deciders:
  - Eli (Navigator)
related:
  - CV4
---

# Painel esportivo com prioridade para os números

## Decision

O Navigator escolheu a direção de painel esportivo, aprovou a composição proposta e pediu que os pontos ganhassem mais destaque que nome da quadra, código e regras. Preferiu a fonte original **Teko**, depois pediu números mais finos e maiores. A prévia com peso 600 e escala maior foi aprovada com “perfeito”; o modo claro correspondente foi aprovado com “ótimo”.

Começar pela tela inicial. A aplicação deve servir usos variáveis: celular na mão, Fold aberto/fechado, tablet apoiado e acompanhamento em outros aparelhos. O computador é usado sobretudo durante o desenvolvimento.

Manter o recolhimento automático dos controles do espectador, atualmente após três segundos. O Navigator quer tela cheia do navegador quando possível. A forma técnica de solicitação e o comportamento de falha serão validados em uma entrega própria.

## Especificação visual aprovada como referência

- Teko local para pontuação; peso inicial 600. Texto de interface pode continuar em Inter local.
- Números grandes e escuros no tema claro; claros no tema escuro.
- Ciano e laranja identificam equipes; não repetir essas cores em papéis administrativos e ações genéricas durante a migração dos componentes afetados.
- Nome da quadra aproximadamente 14–15 px na prévia; regras/código 12 px, sujeitos a zoom e validação de leitura.
- Na prévia, números do acompanhamento usam `clamp(104px, 36cqw, 350px)`. É referência visual, **não fórmula final para produção**: a implementação precisa considerar altura disponível, nomes e placares de três dígitos.
- Painéis simples, sem argolas, placas físicas, brilho ou sombras pesadas como elemento dominante.
- Temas claro e escuro equivalentes. Acento lima da proposta aceito como direção; cor final de cada estado exige medição de contraste.

## Rationale

A pessoa acompanhando deve identificar o resultado rapidamente, inclusive à distância. A diferenciação visual vem da tipografia, proporção e feedback da partida. Metadados não podem empurrar os números para fora da primeira tela.

## Options Considered

- Refinar o placar de folhas/argolas: apresentado como alternativa; o Navigator escolheu painel esportivo.
- Numerais em fonte genérica: substituídos por Teko a pedido do Navigator.
- Peso muito forte: refinado para 600 e aprovado.
- Novo tema claro: demonstrado e aprovado, mantendo a mesma hierarquia.

## Limite da decisão

Aprovação visual não autoriza implementação, merge ou publicação. O Navigator solicitou um plano detalhado antes de alterar a aplicação. Admin, controle de pontuação, janelas auxiliares e a política exata de tela cheia ainda precisam de suas superfícies de plano/validação. Não tomar o comportamento demonstrativo dos protótipos como regra de negócio aprovada.

## Consequences

Quando a nova experiência for entregue, a decisão de representação visual da `CV1.DS1.US5` será sucedida para o placar migrado. Preservar o histórico dessa história e seu comportamento de acompanhamento; não reescrever o passado como se as folhas nunca tivessem sido aprovadas.

Fontes e ícones em produção continuam locais, sem dependência de CDN. As amostras da conversa usam Google Fonts e ícones do ambiente somente para apresentação.

## Review Trigger

Leitura insuficiente no tablet à distância, cortes em três dígitos, dificuldades com zoom ou feedback do Navigator na validação física. Ajustar medidas dentro desta direção antes de propor outra identidade.
