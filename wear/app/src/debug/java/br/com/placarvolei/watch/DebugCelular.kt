package br.com.placarvolei.watch

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import org.json.JSONObject
import java.io.File

/**
 * Disparador de debug da ponte com o celular (CV7.TS3), só nas builds debug: a
 * tela do relógio para a quadra local chega na CV7.US2. Exercita o mesmo caminho
 * da US2: `ScoreSync` (fila durável, desfazer previsto) sobre o `CelularLink`.
 *
 *   adb shell am broadcast -n br.com.placarvolei/.DebugCelular -a br.com.placarvolei.watch.DEBUG_ESTADO
 *   adb shell am broadcast -n br.com.placarvolei/.DebugCelular -a br.com.placarvolei.watch.DEBUG_PONTO --es equipe A
 *   adb shell am broadcast -n br.com.placarvolei/.DebugCelular -a br.com.placarvolei.watch.DEBUG_DESFAZER
 *
 * O resultado sai no logcat, tag `CelularDebug`.
 */
class DebugCelular : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val app = context.applicationContext
        val pendente = goAsync()
        escopo.launch {
            try {
                mutex.withLock { executar(app, intent) }
            } catch (e: Exception) {
                Log.e(TAG, "falhou: ${e.message}", e)
            } finally {
                pendente.finish()
            }
        }
    }

    private suspend fun executar(context: Context, intent: Intent) {
        val sync = sync(context)
        val link = CelularLink(context)
        // Estado publicado pelo celular, mesmo de antes de o relógio reconectar.
        link.estadoAtual()?.let { sync.applySnapshot(it, it.optString("comando_id").ifBlank { null }) }
        sync.setParticipant(CelularProtocolo.ID_RELOGIO)
        when (intent.action) {
            ACAO_ESTADO -> Unit
            ACAO_PONTO -> Log.i(TAG, "ponto ${intent.getStringExtra("equipe")}: aceito=${sync.tap(intent.getStringExtra("equipe") ?: "A")}")
            ACAO_DESFAZER -> Log.i(TAG, "desfazer: aceito=${sync.undo()}")
            else -> return
        }
        drenar(sync, link)
        val s = sync.score
        Log.i(TAG, "placar A=${s?.pontosA} B=${s?.pontosB} partida=${s?.partidaId} seq=${s?.seq} fila=${sync.pending.size} aviso=${sync.notice}")
    }

    /** Envia a fila em ordem até esvaziar ou o celular sumir. */
    private suspend fun drenar(sync: ScoreSync, link: CelularLink) {
        while (true) {
            val (resultado, dados) = sync.sendNext { corpo ->
                Log.i(TAG, "enviando ${corpo.optString("acao")} ${corpo.optString("id").take(8)}")
                link.enviar(corpo)
            }
            Log.i(TAG, "envio: $resultado ${dados?.optJSONObject("recibo") ?: dados?.optString("detail").orEmpty()}")
            if (resultado == SendResult.OCIOSO || resultado == SendResult.SEM_REDE || resultado == SendResult.ADIADO) return
        }
    }

    companion object {
        private const val TAG = "CelularDebug"
        const val ACAO_ESTADO = "br.com.placarvolei.watch.DEBUG_ESTADO"
        const val ACAO_PONTO = "br.com.placarvolei.watch.DEBUG_PONTO"
        const val ACAO_DESFAZER = "br.com.placarvolei.watch.DEBUG_DESFAZER"
        private val escopo = CoroutineScope(SupervisorJob() + Dispatchers.IO)
        private val mutex = Mutex()
        private var sync: ScoreSync? = null

        /** Fila própria da quadra local, separada da do servidor. */
        @Synchronized private fun sync(context: Context): ScoreSync =
            sync ?: ScoreSync(CommandQueue(File(context.filesDir, "fila-celular-debug.json"))).also { sync = it }
    }
}
