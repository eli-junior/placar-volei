// CV4.DS3.US1 — operação a um toque para admin e controlador.
import { test, expect, criarSala, entrarNaSala, postar, semRolagem } from './apoio.js';

for (const [largura, altura] of [[360, 640], [390, 844], [1066, 600]]) {
  test(`operação cabe sem rolagem (${largura}×${altura})`, async ({ abrir }) => {
    const p = await abrir({ viewport: { width: largura, height: altura } });
    await criarSala(p);
    expect(await semRolagem(p)).toEqual({ rolaVertical: false, rolaHorizontal: false, foraDaTela: 0 });
  });
}

test('+1 seguem a inversão e ficam nas laterais em paisagem', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 1066, height: 600 } });
  await criarSala(p);
  const a = p.getByLabel('Marcar ponto para Equipe A');
  const b = p.getByLabel('Marcar ponto para Equipe B');
  const placar = await p.locator('.palco > .resultado').boundingBox();
  expect((await a.boundingBox()).x).toBeLessThan(placar.x);
  expect((await b.boundingBox()).x).toBeGreaterThan(placar.x + placar.width - 1);
  await p.getByLabel('Inverter lados das equipes').click();
  await expect.poll(async () => (await a.boundingBox()).x).toBeGreaterThan(placar.x + placar.width - 1);
});

test('desfazer indica e anula o último ponto', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await criarSala(p);
  await p.getByLabel('Marcar ponto para Equipe A').click();
  await p.getByLabel('Marcar ponto para Equipe B').click();
  await expect(p.locator('.btn-desfazer')).toContainText('último: +1 Equipe B');
  await p.locator('.btn-desfazer').click();
  await expect(p.locator('.btn-desfazer')).toContainText('último: +1 Equipe A');
  await expect(p.locator('[aria-label^="Placar:"]')).toHaveAttribute('aria-label', 'Placar: Equipe A 1, Equipe B 0');
});

test('posse separada do papel; servidor recusa quem não tem o controle', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 390, height: 844 } });
  const sala = await criarSala(admin);
  const ana = await abrir({ viewport: { width: 1066, height: 600 } });
  const participante = await entrarNaSala(ana, sala.id);
  await postar(admin, `/api/quadras/${sala.id}/participantes/${participante.id}/promover`);
  await expect(ana.locator('.faixa-posse')).toContainText('Você é controlador');
  await expect(ana.getByLabel('Marcar ponto para Equipe A')).toBeDisabled();
  const forjada = await postar(ana, `/api/quadras/${sala.id}/pontos`, { equipe: 'A' });
  expect(forjada.status).toBe(403);
  await ana.getByRole('button', { name: 'Assumir' }).click();
  await expect(ana.locator('.faixa-posse')).toContainText('Você está no controle');
  await expect(admin.locator('.faixa-posse')).toContainText('Você é admin');
  await ana.getByLabel('Marcar ponto para Equipe B').click();
  for (const pg of [admin, ana]) {
    await expect(pg.locator('[aria-label^="Placar:"]')).toHaveAttribute('aria-label', 'Placar: Equipe A 0, Equipe B 1');
  }
});
