package br.com.placarvolei;

import android.view.Window;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Esconde ou mostra as barras do Android (status e navegação) para o placar do
 * espectador ocupar a tela toda. O JS decide quando; aqui só se aplica. Com as
 * barras escondidas, deslizar a partir da borda as traz de volta por instantes
 * (modo imersivo "sticky").
 */
@CapacitorPlugin(name = "BarrasDoSistema")
public class BarrasDoSistemaPlugin extends Plugin {

    @PluginMethod
    public void esconder(PluginCall call) {
        aplicar(true);
        call.resolve();
    }

    @PluginMethod
    public void mostrar(PluginCall call) {
        aplicar(false);
        call.resolve();
    }

    private void aplicar(boolean esconder) {
        getActivity().runOnUiThread(() -> {
            Window janela = getActivity().getWindow();
            WindowCompat.setDecorFitsSystemWindows(janela, !esconder);
            WindowInsetsControllerCompat controle = WindowCompat.getInsetsController(janela, janela.getDecorView());
            if (esconder) {
                controle.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                controle.hide(WindowInsetsCompat.Type.systemBars());
            } else {
                controle.show(WindowInsetsCompat.Type.systemBars());
            }
        });
    }
}
