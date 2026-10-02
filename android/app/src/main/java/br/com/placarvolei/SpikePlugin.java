package br.com.placarvolei;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.HandlerThread;

import androidx.core.content.ContextCompat;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * SPIKE CV7.TS3 (descartável): o JS do WebView roda com a tela apagada?
 * Dispara um evento nativo a cada 5 s e guarda a própria contagem, para
 * comparar com o que o JS recebeu.
 */
@CapacitorPlugin(name = "Spike")
public class SpikePlugin extends Plugin {
    private static final long INTERVALO_MS = 5000;
    private HandlerThread thread;
    private Handler handler;
    private int n = 0;
    private boolean rodando = false;

    private final Runnable tique = new Runnable() {
        @Override
        public void run() {
            if (!rodando) return;
            n++;
            long agora = System.currentTimeMillis();
            SharedPreferences.Editor e = getContext().getSharedPreferences("spike", 0).edit();
            e.putInt("nativo_n", n).putLong("nativo_t", agora).apply();
            JSObject o = new JSObject();
            o.put("n", n);
            o.put("t", agora);
            notifyListeners("tique", o);
            handler.postDelayed(this, INTERVALO_MS);
        }
    };

    @PluginMethod
    public void iniciar(PluginCall call) {
        if (!rodando) {
            rodando = true;
            n = 0;
            getContext().getSharedPreferences("spike", 0).edit().clear().apply();
            thread = new HandlerThread("spike");
            thread.start();
            handler = new Handler(thread.getLooper());
            handler.post(tique);
        }
        call.resolve();
    }

    @PluginMethod
    public void servico(PluginCall call) {
        ContextCompat.startForegroundService(getContext(), new Intent(getContext(), SpikeService.class));
        call.resolve();
    }

    @PluginMethod
    public void parar(PluginCall call) {
        rodando = false;
        getContext().stopService(new Intent(getContext(), SpikeService.class));
        if (thread != null) thread.quit();
        call.resolve();
    }
}
