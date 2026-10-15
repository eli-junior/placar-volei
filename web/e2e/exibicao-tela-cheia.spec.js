// Modo de exibição ocupa mais a tela: o número cresce sem cobrir o nome da equipe.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

const TELAS = [
  { w: 1280, h: 768, nome: 'tablet (2000×1200)' },
  { w: 1280, h: 630, nome: 'tablet mais baixo' },
  { w: 1024, h: 768, nome: 'tablet 4:3' },
  { w: 1920, h: 1080, nome: 'tela cheia 16:9' },
  { w: 844, h: 390, nome: 'celular deitado' },
];

for (const { w, h, nome } of TELAS) {
  test(`o número não cobre o nome da equipe nem sai do cartão — ${nome}`, async ({ abrir }) => {
    const dono = await abrir();
    const sala = await criarSala(dono);
    const esp = await abrir({ viewport: { width: w, height: h } });
    await entrarNaSala(esp, sala.id);
    await esp.waitForTimeout(400);
    const m = await esp.evaluate(() => {
      const r = (e) => e.getBoundingClientRect();
      const cartao = r(document.querySelector('.resultado'));
      return [...document.querySelectorAll('.time')].map((t) => {
        const n = r(t.querySelector('.nome'));
        const p = r(t.querySelector('strong'));
        return { nomeFim: n.bottom, numIni: p.top, numFim: p.bottom, cartaoFim: cartao.bottom };
      });
    });
    for (const x of m) {
      expect(x.numIni, 'número abaixo do nome').toBeGreaterThanOrEqual(x.nomeFim - 1);
      expect(x.numFim, 'número dentro do cartão').toBeLessThanOrEqual(x.cartaoFim + 1);
    }
    if (w === 1280 && h === 768) await esp.screenshot({ path: '/tmp/claude-1000/-projetos-eli-junior-placar-volei/2f171989-35bc-4cda-a642-a6f3e84acde2/scratchpad/sim-768.png' });
    if (w === 1280 && h === 630) await esp.screenshot({ path: '/tmp/claude-1000/-projetos-eli-junior-placar-volei/2f171989-35bc-4cda-a642-a6f3e84acde2/scratchpad/sim-630.png' });
  });
}
