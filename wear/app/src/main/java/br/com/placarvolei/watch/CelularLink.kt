package br.com.placarvolei.watch

import android.content.Context
import com.google.android.gms.tasks.Task
import com.google.android.gms.wearable.CapabilityClient
import com.google.android.gms.wearable.Node
import com.google.android.gms.wearable.Wearable
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.suspendCancellableCoroutine
import org.json.JSONObject
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** Ponto de encontro com o `CelularListenerService`: respostas e estado do celular. */
object CelularCanal {
    val respostas = RespostasEsperadas()

    @Volatile var ultimoEstado: JSONObject? = null
        private set
    private val ouvintes = java.util.concurrent.CopyOnWriteArrayList<(JSONObject) -> Unit>()

    fun publicarEstado(estado: JSONObject) {
        ultimoEstado = estado
        ouvintes.forEach { it(estado) }
    }

    fun observarEstado(ouvinte: (JSONObject) -> Unit): () -> Unit {
        ouvintes += ouvinte
        return { ouvintes -= ouvinte }
    }
}

/**
 * Transporte "Celular" do relógio (CV7.TS3): envia o lance ao celular pelo
 * Data Layer e espera o recibo; lê o último estado da quadra local publicado.
 * `null` em `enviar` = sem celular ao alcance ou sem resposta a tempo, o mesmo
 * que "sem rede" para a fila.
 */
class CelularLink(private val context: Context) {
    /** O celular com o app instalado e ao alcance, se houver. */
    suspend fun celular(): Node? {
        val capacidade = Wearable.getCapabilityClient(context)
            .getCapability(CelularProtocolo.CAPACIDADE_CELULAR, CapabilityClient.FILTER_REACHABLE).await()
        return capacidade.nodes.firstOrNull { it.isNearby } ?: capacidade.nodes.firstOrNull()
    }

    suspend fun enviar(corpo: JSONObject, tempoMs: Long = 8_000): Pair<Int, JSONObject>? = try {
        val no = celular()
        if (no == null) null else CelularCanal.respostas.aguardar(corpo.getString("id"), tempoMs) {
            Wearable.getMessageClient(context)
                .sendMessage(no.id, CelularProtocolo.CAMINHO_COMANDO, CelularProtocolo.codificarComando(corpo)).await()
            true
        }
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        null
    }

    /** Último estado da quadra local que o celular publicou, mesmo de antes de reconectar. */
    suspend fun estadoAtual(): JSONObject? = try {
        val itens = Wearable.getDataClient(context).dataItems.await()
        try {
            itens.firstOrNull { it.uri.path == CelularProtocolo.CAMINHO_ESTADO }
                ?.data?.let(CelularProtocolo::decodificarEstado)
        } finally {
            itens.release()
        }
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        null
    }
}

/** `Task` do Play Services como função suspensa, sem depender de `kotlinx-coroutines-play-services`. */
suspend fun <T> Task<T>.await(): T = suspendCancellableCoroutine { cont ->
    addOnSuccessListener { cont.resume(it) }
    addOnFailureListener { cont.resumeWithException(it) }
    addOnCanceledListener { cont.cancel() }
}
