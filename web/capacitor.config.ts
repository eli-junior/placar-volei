import type { CapacitorConfig } from '@capacitor/cli';

// APK Android (CV7.TS1). A interface embarcada sai do mesmo build do FastAPI;
// a quadra online é o servidor aberto no WebView, então o host precisa estar
// em `allowNavigation` (senão o Android abre o navegador do sistema).
// PLACAR_SERVIDOR (ex.: placar.seudominio.com) é lido no `cap sync`.
const servidor = (process.env.PLACAR_SERVIDOR ?? '').replace(/^https?:\/\//, '').replace(/\/.*$/, '');

const config: CapacitorConfig = {
  appId: 'br.com.placarvolei',
  appName: 'Placar Vôlei',
  webDir: '../app/static',
  android: { path: '../android' },
  server: {
    androidScheme: 'https',
    allowNavigation: servidor ? [servidor] : [],
  },
};

export default config;
