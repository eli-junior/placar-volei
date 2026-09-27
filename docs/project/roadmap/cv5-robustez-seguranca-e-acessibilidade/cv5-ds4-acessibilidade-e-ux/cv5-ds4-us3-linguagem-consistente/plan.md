# Plano — CV5.DS4.US3 Linguagem e estados consistentes

- **Nível:** User Story · **Branch:** `feature/cv5-ds4-us3-linguagem-consistente` · **Versão:** patch

## Scope
1. **Conexão:** o chip do cabeçalho (`SalaQuadra.svelte:474,533`) e o banner (`:551`) usam o mesmo vocabulário do relógio: "Ao vivo" / "Reconectando…" / "Sem conexão". O banner diz só o efeito: "Os controles voltam sozinhos."
2. **Aviso de envio** (`Placar.svelte:462-473`): cor fixa `#a5f3fc` trocada por `var(--acento-info)`, que já tem valor próprio no Modo Sol (`app.css:345`).
3. **Vitória:** "{nome} venceu!" em `Placar.svelte:155`, `PlacarManual.svelte:57` e no anúncio acessível (`Placar.svelte:120`), sem artigo.
4. **Selo de papel** (`SalaQuadra.svelte:486`): mapa `ADMIN → Admin`, `CONTROLADOR → Controlador`, `ESPECTADOR → Espectador`, fonte ≥ 0,8rem.
5. **Apelido lembrado:** constante única `CHAVE_APELIDO = 'placar:apelido'` em `lib/preferencias.js`, usada pela Home e pelo `ModalEntrar`; na primeira leitura, migra o valor de `placar_ultimo_apelido`.

## Acceptance
- Dada a rede caída, então o cabeçalho e o banner dizem a mesma coisa.
- Dado o Modo Sol, então "Enviando o toque…" tem contraste ≥ 4,5:1 (teste de contraste existente).
- Dado que digitei "Eli" na Home, quando entro por um link de sala, então o apelido vem preenchido.

## Risks / Navigator
- Confirmar os textos: "{nome} venceu!" e "Controlador" (a revisão sugeriu "No controle", mas o papel e o controle são coisas diferentes no produto).

## Validation
`npm run check && npm test` (teste de contraste do Modo Sol cobre o token); roteiro visual nos temas claro, escuro e Sol.
