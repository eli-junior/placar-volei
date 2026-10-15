package br.com.placarvolei;

import android.os.Bundle;
import android.webkit.JavascriptInterface;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        // Ponte com o relógio pelo Data Layer (CV7.TS3).
        registerPlugin(PlacarRelogioPlugin.class);
        registerPlugin(BarrasDoSistemaPlugin.class);
        super.onCreate(savedInstanceState);
        // A quadra online é a página do servidor, e o Capacitor não leva a ponte dos
        // plugins a essa origem. Esta ponte própria só liga e desliga as barras.
        getBridge().getWebView().addJavascriptInterface(new PonteBarras(), "PlacarBarras");
    }

    /** Exposta ao JS como `window.PlacarBarras`; só mexe nas barras do sistema. */
    private class PonteBarras {
        @JavascriptInterface
        public void esconder() { BarrasDoSistemaPlugin.pedir(MainActivity.this, true); }

        @JavascriptInterface
        public void mostrar() { BarrasDoSistemaPlugin.pedir(MainActivity.this, false); }
    }

    @Override
    public void onWindowFocusChanged(boolean temFoco) {
        super.onWindowFocusChanged(temFoco);
        if (temFoco) BarrasDoSistemaPlugin.reaplicarSeEscondidas(this);
    }
}
