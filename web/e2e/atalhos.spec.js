// CV6.DS1.US6 — atalhos de ajuste no placar: regras do topo e nome da equipe.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

for (const tema of ['esportivo', 'classico']) {
  test(`atalhos abrem só a parte certa e salvam sem mexer no resto (${tema})`, async ({ abrir }) => {
    const admin = await abrir({ viewport: { width: 1280, height: 800 } });
    const sala = await criarSala(admin, { config: { tema_placar: tema } });
    const esp = await abrir({ viewport: { width: 1280, height: 800 } });
    await entrarNaSala(esp, sala.id);
    const dialogo = admin.locator('dialog[open]');

    // Regras: só pontuação; tocar fora fecha sem salvar.
    await admin.getByTitle('Ajustar pontuação e vantagem').click();
    await expect(dialogo.getByRole('heading')).toHaveText('Pontuação e Vantagem');
    await expect(dialogo.getByLabel('Jogador 1')).toHaveCount(0);
    await admin.mouse.click(10, 790);
    await expect(dialogo).toHaveCount(0);

    await admin.getByTitle('Ajustar pontuação e vantagem').click();
    await dialogo.locator('#alvo-slider').fill('15');
    await dialogo.getByRole('button', { name: 'Salvar Alterações' }).click();
    await expect(admin.locator('.regras-topo')).toContainText(/15 pts (com vantagem|\(V\))/);

    // Equipe A: só os jogadores da A.
    await admin.getByLabel(/Editar jogadores da Equipe A/).click();
    await expect(dialogo.getByRole('heading')).toHaveText('Jogadores da Equipe A');
    await expect(dialogo.locator('input')).toHaveCount(2);
    await dialogo.locator('#cfg-time-a-j1').fill('Ana');
    await dialogo.locator('#cfg-time-a-j2').fill('Bia');
    await dialogo.getByRole('button', { name: 'Salvar Alterações' }).click();
    await expect(admin.getByLabel(/Editar jogadores da Ana/)).toBeVisible();
    await expect(admin.getByLabel(/Editar jogadores da Equipe B/)).toBeVisible();
    await expect(admin.locator('.regras-topo')).toContainText(/15 pts (com vantagem|\(V\))/);

    // Espectador vê o resultado e não tem atalho.
    await expect(esp.getByText(/Ana/).first()).toBeVisible();
    await expect(esp.getByLabel(/Editar jogadores/)).toHaveCount(0);

    // Limpar apaga os nomes de uma vez; salvar volta ao nome padrão.
    await admin.getByLabel(/Editar jogadores da Ana/).click();
    await dialogo.getByRole('button', { name: 'Limpar nomes da Equipe A' }).click();
    await expect(dialogo.locator('#cfg-time-a-j1')).toHaveValue('');
    await expect(dialogo.locator('#cfg-time-a-j2')).toHaveValue('');
    await dialogo.getByRole('button', { name: 'Salvar Alterações' }).click();
    await expect(admin.getByLabel(/Editar jogadores da Equipe A/)).toBeVisible();
  });
}
