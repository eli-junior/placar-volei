/**
 * Ícones vetoriais do produto — CV2.DS4.US3.
 *
 * Os desenhos são os do conjunto **Lucide** (https://lucide.dev), distribuído
 * sob a licença ISC:
 *
 *   ISC License — Copyright (c) for portions of Lucide are held by Cole Bemis
 *   2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are
 *   held by Lucide Contributors 2022.
 *
 * Por que embutir em vez de instalar `lucide-svelte`:
 *
 * 1. O pacote npm traz mais de 1500 ícones e um componente por ícone. Usamos
 *    menos de vinte. Embutir o traçado custa ~4 KB e evita uma dependência de
 *    runtime num produto que precisa abrir rápido em 4G na beira da quadra.
 * 2. A licença ISC permite a redistribuição com o aviso de copyright acima,
 *    que este arquivo carrega.
 * 3. Sem dependência, o `npm install` da quadra continua reprodutível offline.
 *
 * Cada ícone é descrito como uma lista de formas primitivas e NÃO como uma
 * string de SVG. Isso mantém o componente `Icone.svelte` livre de `{@html}` e
 * torna o conjunto testável por `node --test`.
 *
 * Convenção do traçado (a mesma do Lucide): caixa 24×24, sem preenchimento,
 * traço de 2 unidades em `currentColor`, pontas e junções arredondadas.
 */

/** Caixa de desenho de todo ícone do conjunto. */
export const CAIXA_ICONE = 24;

/**
 * Traçados por nome. O nome é em português porque é o vocabulário do produto;
 * o nome original no Lucide fica anotado ao lado para facilitar a conferência.
 */
export const ICONES = {
  // lucide: settings
  engrenagem: [
    {
      tag: 'path',
      d: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z',
    },
    { tag: 'circle', cx: 12, cy: 12, r: 3 },
  ],

  // lucide: watch
  relogio: [
    { tag: 'path', d: 'M12 10v2.2l1.6 1' },
    { tag: 'path', d: 'm16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05' },
    { tag: 'path', d: 'm7.88 16.36.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05' },
    { tag: 'circle', cx: 12, cy: 12, r: 6 },
  ],

  // lucide: x
  fechar: [
    { tag: 'path', d: 'M18 6 6 18' },
    { tag: 'path', d: 'm6 6 12 12' },
  ],

  // lucide: info
  informacao: [
    { tag: 'circle', cx: 12, cy: 12, r: 10 },
    { tag: 'path', d: 'M12 16v-4' },
    { tag: 'path', d: 'M12 8h.01' },
  ],

  // lucide: triangle-alert
  alerta: [
    { tag: 'path', d: 'm21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3' },
    { tag: 'path', d: 'M12 9v4' },
    { tag: 'path', d: 'M12 17h.01' },
  ],

  // lucide: volleyball
  bola: [
    { tag: 'path', d: 'M11.1 7.1a16.55 16.55 0 0 1 10.9 4' },
    { tag: 'path', d: 'M12 12a12.6 12.6 0 0 1-8.7 5' },
    { tag: 'path', d: 'M16.8 13.6a16.55 16.55 0 0 1-9 7.5' },
    { tag: 'path', d: 'M20.7 17a12.8 12.8 0 0 0-8.7-5 13.3 13.3 0 0 1 0-10' },
    { tag: 'path', d: 'M6.3 3.8a16.55 16.55 0 0 0 1.9 11.5' },
    { tag: 'circle', cx: 12, cy: 12, r: 10 },
  ],

  // lucide: zap
  raio: [
    {
      tag: 'path',
      d: 'M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z',
    },
  ],

  // lucide: eye
  olho: [
    {
      tag: 'path',
      d: 'M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0',
    },
    { tag: 'circle', cx: 12, cy: 12, r: 3 },
  ],

  // lucide: users
  pessoas: [
    { tag: 'path', d: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2' },
    { tag: 'circle', cx: 9, cy: 7, r: 4 },
    { tag: 'path', d: 'M22 21v-2a4 4 0 0 0-3-3.87' },
    { tag: 'path', d: 'M16 3.13a4 4 0 0 1 0 7.75' },
  ],

  // lucide: settings-2
  regras: [
    { tag: 'path', d: 'M20 7h-9' },
    { tag: 'path', d: 'M14 17H5' },
    { tag: 'circle', cx: 17, cy: 17, r: 3 },
    { tag: 'circle', cx: 7, cy: 7, r: 3 },
  ],

  // lucide: refresh-cw
  atualizar: [
    { tag: 'path', d: 'M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8' },
    { tag: 'path', d: 'M21 3v5h-5' },
    { tag: 'path', d: 'M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16' },
    { tag: 'path', d: 'M8 16H3v5' },
  ],

  // lucide: arrow-right
  seta: [
    { tag: 'path', d: 'M5 12h14' },
    { tag: 'path', d: 'm12 5 7 7-7 7' },
  ],

  // lucide: scroll-text
  linhaDoTempo: [
    { tag: 'path', d: 'M15 12h-5' },
    { tag: 'path', d: 'M15 8h-5' },
    { tag: 'path', d: 'M19 17V5a2 2 0 0 0-2-2H4' },
    {
      tag: 'path',
      d: 'M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3',
    },
  ],

  // lucide: flag
  bandeira: [
    { tag: 'path', d: 'M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z' },
    { tag: 'path', d: 'M4 22v-7' },
  ],

  // lucide: trophy
  trofeu: [
    { tag: 'path', d: 'M6 9H4.5a2.5 2.5 0 0 1 0-5H6' },
    { tag: 'path', d: 'M18 9h1.5a2.5 2.5 0 0 0 0-5H18' },
    { tag: 'path', d: 'M4 22h16' },
    { tag: 'path', d: 'M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22' },
    { tag: 'path', d: 'M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22' },
    { tag: 'path', d: 'M18 2H6v7a6 6 0 0 0 12 0V2Z' },
  ],

  // lucide: rotate-ccw
  desfazer: [
    { tag: 'path', d: 'M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8' },
    { tag: 'path', d: 'M3 3v5h5' },
  ],

  // lucide: lock
  cadeado: [
    { tag: 'rect', x: 3, y: 11, width: 18, height: 11, rx: 2 },
    { tag: 'path', d: 'M7 11V7a5 5 0 0 1 10 0v4' },
  ],

  // lucide: share-2
  compartilhar: [
    { tag: 'circle', cx: 18, cy: 5, r: 3 },
    { tag: 'circle', cx: 6, cy: 12, r: 3 },
    { tag: 'circle', cx: 18, cy: 19, r: 3 },
    { tag: 'line', x1: 8.59, y1: 13.51, x2: 15.42, y2: 17.49 },
    { tag: 'line', x1: 15.41, y1: 6.51, x2: 8.59, y2: 10.49 },
  ],

  // lucide: qr-code
  qrCode: [
    { tag: 'rect', x: 3, y: 3, width: 5, height: 5, rx: 1 },
    { tag: 'rect', x: 16, y: 3, width: 5, height: 5, rx: 1 },
    { tag: 'rect', x: 3, y: 16, width: 5, height: 5, rx: 1 },
    { tag: 'path', d: 'M21 16h-3a2 2 0 0 0-2 2v3' },
    { tag: 'path', d: 'M21 21v.01' },
    { tag: 'path', d: 'M12 7v3a2 2 0 0 1-2 2H7' },
    { tag: 'path', d: 'M3 12h.01' },
    { tag: 'path', d: 'M12 3h.01' },
    { tag: 'path', d: 'M12 16v.01' },
    { tag: 'path', d: 'M16 12h1' },
    { tag: 'path', d: 'M21 12v.01' },
    { tag: 'path', d: 'M12 21v-1' },
  ],

  // lucide: copy
  copiar: [
    { tag: 'rect', x: 8, y: 8, width: 14, height: 14, rx: 2 },
    { tag: 'path', d: 'M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2' },
  ],

  // lucide: check
  confirmado: [{ tag: 'path', d: 'M20 6 9 17l-5-5' }],

  // lucide: link
  elo: [
    { tag: 'path', d: 'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71' },
    { tag: 'path', d: 'M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71' },
  ],

  // lucide: sun
  sol: [
    { tag: 'circle', cx: 12, cy: 12, r: 4 },
    { tag: 'path', d: 'M12 2v2' },
    { tag: 'path', d: 'M12 20v2' },
    { tag: 'path', d: 'm4.93 4.93 1.41 1.41' },
    { tag: 'path', d: 'm17.66 17.66 1.41 1.41' },
    { tag: 'path', d: 'M2 12h2' },
    { tag: 'path', d: 'M20 12h2' },
    { tag: 'path', d: 'm6.34 17.66-1.41 1.41' },
    { tag: 'path', d: 'm19.07 4.93-1.41 1.41' },
  ],

  // lucide: moon
  lua: [
    { tag: 'path', d: 'M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z' },
  ],
};

/** Nomes disponíveis, útil para testes e para inventário do conjunto. */
export const NOMES_DE_ICONE = Object.keys(ICONES);

/**
 * Formas de um ícone. Devolve `[]` para nome desconhecido em vez de quebrar a
 * tela: um ícone ausente é um detalhe visual, nunca um erro de placar.
 */
export function formasDoIcone(nome) {
  return ICONES[nome] ?? [];
}
