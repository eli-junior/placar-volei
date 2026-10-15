package br.com.placarvolei;

import android.util.Log;
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
    private static final String TAG = "BarrasDoSistema";

    /** O que o JS pediu por último; a atividade reaplica quando a janela volta a ter foco. */
    private static volatile boolean escondidas = false;

    /** O Android desfaz o modo imersivo ao perder o foco (painel de notificações, troca de app). */
    static void reaplicarSeEscondidas(android.app.Activity atividade) {
        if (escondidas) aplicar(atividade, true);
    }

    @PluginMethod
    public void esconder(PluginCall call) {
        Log.d(TAG, "esconder");
        escondidas = true;
        aplicar(getActivity(), true);
        call.resolve();
    }

    @PluginMethod
    public void mostrar(PluginCall call) {
        Log.d(TAG, "mostrar");
        escondidas = false;
        aplicar(getActivity(), false);
        call.resolve();
    }

    private static void aplicar(android.app.Activity atividade, boolean esconder) {
        atividade.runOnUiThread(() -> {
            Window janela = atividade.getWindow();
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
