---
status: Accepted
date: 2026-10-15
related:
  - CV8.DS9.US25
  - RN-19
---

# Resenha do Joguinho: dados do gerenciador e imagens geradas no navegador

## Contexto

O Navigator quer, depois da partida, uma página de estatísticas divertida para mandar no grupo do WhatsApp. No primeiro retorno (Checkpoint 2) pediu que a página não fosse uma imagem infinita e que um botão baixasse as imagens.

## Decisão (Navigator, 2026-10-15)

- **Zoeira liberada:** prêmios negativos com nome (Pé-frio, Pneu, Freguês, Circuit breaker…) ao lado dos positivos; critérios na RN-19.
- **Sessão:** a aberta ou a última encerrada; sem escolher sessões antigas.
- **Só o `gerenciador.db`:** os eventos ponto a ponto das quadras expiram com a sala (`app/quadras.py`), então viradas e sequências de pontos ficam de fora. Quem jogou cada partida vem de `ajustes_nota`, porque substituição e retirada reescrevem `time_jogadores` depois (o mesmo critério da `fila-por-tempo-sem-jogar`).
- **Só o dono vê:** a rota fica em `/api/sessao` (segredo do dono); o grupo recebe as imagens, nenhum dado novo fica público.
- **Cartões 4:5 de tamanho fixo** (1080 × 1350, o formato que o WhatsApp mostra inteiro), medidos em `cqw` para o PNG sair igual à tela.
- **PNG gerado no navegador com `html-to-image` 1.11.11** (MIT, sem dependências, só no bundle do build). Web Share com arquivos quando existe; download quando não.

## Alternativas rejeitadas

- **Desenhar cada cartão à mão em canvas:** sem dependência, mas duplicaria todo o layout e cada ajuste visual seria feito duas vezes.
- **Gerar a imagem no servidor** (Chromium ou Pillow no contêiner): peso e serviço novo no Mini PC, contra o princípio de simplicidade de operação.
- **Página pública para o grupo:** exporia nomes e fotos fora do Joguinho; a imagem já resolve.
- **Prêmios de pontos individuais:** o placar é do time; não há esse dado.

## Consequências

`app/estatisticas.py` concentra os critérios (pura e testada); mudar um prêmio é mudar a RN-19 e esse módulo. A exportação depende do navegador do celular: o compartilhar de arquivos existe no Chrome do Android e no Safari, mas não em todo desktop (lá o botão some e fica o download). Débito: `2026-10-15T1800Z-imagens-da-resenha-dependem-do-navegador`.
