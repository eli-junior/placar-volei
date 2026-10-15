---
id: debt-imagens-da-resenha-dependem-do-navegador
status: Carried
kind: technical
severity: low
source: CV8.DS9.US25
revisit_trigger: Imagem da Resenha sair errada (sem foto, cortada, fonte trocada) num aparelho real, ou o html-to-image quebrar numa atualização do navegador
closure_condition: Teste de exportação num Android físico registrado e, se preciso, espera explícita pelas fotos antes de gerar
---

# Imagens da Resenha Dependem do Navegador

## Description

Os PNGs da Resenha são gerados no navegador pelo `html-to-image` (1.11.11, última versão publicada em 2023), que copia o cartão para um SVG e o desenha num canvas. O e2e cobre o download no Chromium de desktop; o compartilhar de arquivos (Web Share) não tem teste automático e não foi observado num Android físico. A foto de cada jogador é baixada depois que o cartão aparece: quem tocar em Baixar antes de ela chegar recebe as iniciais na imagem.

## Carrying Reason

O caminho comum (abrir a Resenha, olhar, tocar em Mandar) dá tempo de as fotos chegarem, e gerar no servidor custaria um serviço novo no Mini PC.

## Notes

Decisão: `docs/project/decisions/records/2026-10-15T1800Z-resenha-do-joguinho.md`.
