package br.com.placarvolei.watch

import com.google.android.gms.wearable.DataEvent
import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.MessageEvent
import com.google.android.gms.wearable.WearableListenerService

/** Recibos e estado da quadra local que o celular manda pelo Data Layer (CV7.TS3). */
class CelularListenerService : WearableListenerService() {
    override fun onMessageReceived(evento: MessageEvent) {
        if (evento.path == CelularProtocolo.CAMINHO_RECIBO) CelularCanal.respostas.entregar(evento.data)
    }

    override fun onDataChanged(eventos: DataEventBuffer) {
        for (evento in eventos) {
            if (evento.type != DataEvent.TYPE_CHANGED || evento.dataItem.uri.path != CelularProtocolo.CAMINHO_ESTADO) continue
            CelularProtocolo.decodificarEstado(evento.dataItem.data ?: continue)?.let(CelularCanal::publicarEstado)
        }
    }
}
