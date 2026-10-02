package br.com.placarvolei;

import com.google.android.gms.wearable.MessageEvent;
import com.google.android.gms.wearable.WearableListenerService;

import java.nio.charset.StandardCharsets;

/** Recebe os lances do relógio (CV7.TS3) e os entrega ao plugin. */
public class RelogioListenerService extends WearableListenerService {
    @Override
    public void onMessageReceived(MessageEvent evento) {
        if (PlacarRelogioPlugin.CAMINHO_COMANDO.equals(evento.getPath())) {
            PlacarRelogioPlugin.entregar(evento.getSourceNodeId(), new String(evento.getData(), StandardCharsets.UTF_8));
        }
    }
}
