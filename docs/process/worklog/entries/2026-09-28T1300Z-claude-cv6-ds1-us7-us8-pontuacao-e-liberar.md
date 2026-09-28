---
related:
  - CV6.DS1.US7
  - CV6.DS1.US8
---

# CV6.DS1.US7/US8 — pontuação por slider e liberar quadra (0.23.0)

Padrão 10 pontos, slider 6–20 com Personalizado, topo `10 pts · +2`, selo Ⓐ/Ⓒ com dica e liberação da quadra pelo admin. O e2e pegou dois defeitos antes da validação: o `$effect` do modal passou a depender do alvo e desfazia cada mexida no slider; e o aviso do socket chegava antes da resposta do liberar, trocando a mensagem de quem liberou. Na validação o Navigator pediu `pts` e a vantagem de volta no topo (`+2`). Evidência: 224 pytest, 96 unit web, 34 e2e; Navigator validou no Fold.
