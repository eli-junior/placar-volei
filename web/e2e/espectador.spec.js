// CV4.DS2.US2 — imersão estável e tela cheia real.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

for (const [largura, altura] of [[360, 640], [390, 844], [1066, 600]]) {
  test(`placar do espectador não se move ao revelar controles (${largura}×${altura})`, async ({ abrir }) => {
    const admin = await abrir();
    const sala = await criarSala(admin);
    const esp = await abrir({ viewport: { width: largura, height: altura }, hasTouch: true });
    await entrarNaSala(esp, sala.id);
    await expect(esp.getByLabel('Tela cheia')).toHaveCount(0, { timeout: 6000 });
    const antes = await esp.locator('.area-resultado').boundingBox();
    await esp.touchscreen.tap(largura / 2, altura / 2);
    await expect(esp.getByLabel('Tela cheia')).toBeVisible();
    expect(await esp.locator('.area-resultado').boundingBox()).toEqual(antes);
    const fora = await esp.evaluate(() => [...document.querySelectorAll('.sala-header button, .ws-status')]
      .filter((e) => e.getBoundingClientRect().right > innerWidth + 1).length);
    expect(fora).toBe(0);
  });
}

test('toque que revela os controles não aciona o botão oculto', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 }, hasTouch: true });
  await entrarNaSala(esp, sala.id);
  await esp.touchscreen.tap(195, 400);
  const botao = esp.getByLabel('Tela cheia');
  const caixa = await botao.boundingBox();
  await expect(botao).toHaveCount(0, { timeout: 6000 });
  // Toca exatamente onde o botão aparecerá: só revela, não entra em tela cheia.
  await esp.touchscreen.tap(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2);
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
  expect(await esp.evaluate(() => Boolean(document.fullscreenElement))).toBe(false);
});

test('tela cheia confirmada pelo navegador e saída externa reconhecida', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 } });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(195, 400);
  await esp.getByLabel('Tela cheia').click();
  await expect(esp.getByLabel('Sair da tela cheia')).toBeVisible();
  await esp.evaluate(() => document.exitFullscreen());
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
});

test('recusa de tela cheia informa e mantém o placar na aba', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 } }, {
    fn: () => { Element.prototype.requestFullscreen = () => Promise.reject(new TypeError('negado')); },
  });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(195, 400);
  await esp.getByLabel('Tela cheia').click();
  await expect(esp.getByText('O navegador não permitiu a tela cheia. O placar continua nesta aba.')).toBeVisible();
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
});
