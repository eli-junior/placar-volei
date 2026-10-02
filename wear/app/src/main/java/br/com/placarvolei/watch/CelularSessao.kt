package br.com.placarvolei.watch

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import org.json.JSONObject
import java.util.UUID

/**
 * O relógio na quadra local do celular (CV7.US2). Fonte de placar como o
 * `WatchModel`, mas com o celular no lugar do servidor: a mesma `ScoreSync`
 * (fila durável, desfazer previsto, descarte com aviso) sobre o Data Layer, com
 * fila própria para nunca se misturar com a de uma quadra do servidor.
 *
 * `ativa` diz se o relógio deve mostrar a quadra local: o celular está com a
 * sala local aberta e deu sinal de vida há pouco. É o celular quem decide o
 * modo; o relógio só o segue.
 */
class CelularSessao(
    queue: CommandQueue,
    private val canal: CanalCelular,
    private val scope: CoroutineScope,
    private val agora: () -> Long = System::currentTimeMillis,
    private val disk: CoroutineDispatcher = Dispatchers.IO.limitedParallelism(1),
    /** Sem notícia do celular por tanto tempo, a sala conta como fechada (app morto, fora de alcance). */
    private val vidaMs: Long = VIDA_MS,
) : PlacarFonte {
    private val sync = ScoreSync(queue)
    private var rev by mutableIntStateOf(0)
    private val wake = Channel<Unit>(Channel.CONFLATED)
    private var salaAberta = false
    private var sinalEm = 0L
    private var iniciada: Job? = null
    private var gravando = false
    private var startingMatch = false
    private var newMatchId: Pair<String, String>? = null

    /** Mostrar a quadra local no lugar da do servidor. */
    var ativa by mutableStateOf(false)
        private set
    override var connection by mutableStateOf(Connection.RECONECTANDO)
        private set
    override val modoRotulo = "Local"

    override val score get() = rev.let { sync.score }
    override val pending get() = rev.let { sync.pending }
    override val lastPointTeam get() = rev.let { sync.lastPointTeam }
    override val pointFeedback get() = sync.pointFeedback
    override val discardNotice get() = rev.let { sync.notice }
    override val labels get() = score?.let(::teamLabels) ?: ("Equipe A" to "Equipe B")
    override val shown get() = score?.let { predicted(it, pending) }
    override val controlled get() = rev.let { sync.controlled }
    override val blockReason get() = rev.let { sync.blockReason }
    override val canUndo get() = rev.let { sync.canUndo }
    override val lostQueue get() = rev.let { sync.lostQueue }
    override val undoSpoken get() = score.let { s ->
        undoDescription(rev.let { sync.undoTeam }, s?.equipeA.orEmpty(), s?.equipeB.orEmpty())
    }

    /** Partida encerrada com o controle: o relógio oferece a próxima (o celular é o admin da quadra). */
    override val showNewMatch get() = controlled && score?.encerrada == true
    override val canStartNewMatch get() = showNewMatch && sync.controlReason == null && pending.isEmpty() &&
        connection == Connection.CONECTADO && !startingMatch

    /**
     * Começa a seguir o celular. Idempotente: a atividade pode abrir várias vezes,
     * e cada abertura pergunta o estado de novo em vez de esperar o sinal de vida.
     */
    fun iniciar() {
        if (iniciada?.isActive == true) {
            scope.launch { canal.pedirEstado() }
            return
        }
        iniciada = scope.launch {
            val remover = CelularCanal.observarEstado { estado -> scope.launch { aplicarEstado(estado) } }
            try {
                // O que já chegou enquanto o app estava fechado vale se for recente (pelo relógio do relógio).
                CelularCanal.ultimoEstado?.let { aplicarEstado(it, CelularCanal.ultimoEstadoEm) }
                launch { canal.pedirEstado() }
                launch { enviarSempre() }
                while (true) {
                    delay(VERIFICACAO_MS)
                    reavaliar()
                }
            } finally {
                remover()
            }
        }
    }

    /**
     * Estado da quadra local que o celular publicou (mudança de placar ou sinal
     * de vida). Aplica o snapshot e decide se o relógio deve mostrá-la.
     */
    internal suspend fun aplicarEstado(estado: JSONObject, recebidoEm: Long = agora()) {
        val aberta = CelularProtocolo.salaAberta(estado)
        withContext(disk) {
            sync.setParticipant(CelularProtocolo.ID_RELOGIO)
            sync.applySnapshot(estado, estado.optString("comando_id").ifBlank { null })
        }
        salaAberta = aberta
        sinalEm = recebidoEm
        if (aberta && recebidoEm >= agora() - vidaMs) connection = Connection.CONECTADO
        reavaliar()
        changed(false)
        wake.trySend(Unit)
    }

    /**
     * O sinal de vida venceu? Chamado pela verificação periódica e a cada estado.
     * Com lances ainda na fila a quadra local não some: com a tela do celular
     * apagada o JS dele congela e o sinal para, e o relógio não pode largar a
     * partida (e esconder os pontos que ainda não foram) por causa disso. Só o
     * celular dizendo que fechou a sala, ou a fila vazia, devolve ao servidor.
     */
    internal fun reavaliar() {
        val fresco = agora() - sinalEm <= vidaMs
        ativa = salaAberta && score != null && (fresco || pending.isNotEmpty())
        if (ativa && !fresco) connection = Connection.SEM_CONEXAO
        else if (!ativa && connection == Connection.CONECTADO) connection = Connection.RECONECTANDO
    }

    override fun tap(equipe: String, done: (Boolean) -> Unit) = write({ sync.tap(equipe) }, done)

    override fun undo(done: (Boolean) -> Unit) = write({ sync.undo() }, done)

    /** Grava o lance na fila antes de qualquer retorno visual; um toque por vez. */
    private fun write(action: () -> Boolean, done: (Boolean) -> Unit) {
        if (gravando) return
        gravando = true
        scope.launch {
            val aceito = try { withContext(disk) { action() } } finally { gravando = false }
            done(changed(aceito))
        }
    }

    private fun changed(accepted: Boolean = true): Boolean {
        rev++
        if (accepted) wake.trySend(Unit)
        return accepted
    }

    /** Envia o lance mais antigo da fila e aplica o recibo. */
    internal suspend fun enviarProximo(): SendResult {
        val (resultado, _) = try {
            withContext(disk) { sync.sendNext { corpo -> canal.enviar(corpo) } }
        } finally {
            changed(false)
        }
        when (resultado) {
            SendResult.SEM_REDE -> connection = Connection.SEM_CONEXAO
            SendResult.ENVIADO -> connection = Connection.CONECTADO
            else -> Unit
        }
        return resultado
    }

    private suspend fun enviarSempre() {
        var backoff = 1_000L
        while (true) {
            if (!ativa) {
                wake.receive()
                continue
            }
            when (enviarProximo()) {
                SendResult.OCIOSO -> wake.receive()
                SendResult.SEM_REDE -> {
                    withTimeoutOrNull(backoff) { wake.receive() }
                    backoff = (backoff * 2).coerceAtMost(15_000L)
                }
                SendResult.ADIADO, SendResult.NAO_AUTORIZADO -> {
                    withTimeoutOrNull(backoff) { wake.receive() }
                    backoff = (backoff * 2).coerceAtMost(30_000L)
                }
                SendResult.ENVIADO -> backoff = 1_000L
            }
        }
    }

    /** Próxima partida pelo celular (direto, como no servidor: não entra na fila offline). */
    override fun startNewMatch(): Boolean {
        val s = score ?: return false
        if (!canStartNewMatch) return false
        val id = newMatchId?.takeIf { it.first == s.partidaId }?.second ?: UUID.randomUUID().toString()
        newMatchId = s.partidaId to id
        startingMatch = true
        scope.launch {
            try {
                val corpo = PendingCommand(id, s.partidaId, s.controleVersao, null, ACAO_NOVA_PARTIDA).toJson()
                val resposta = canal.enviar(corpo)
                if (resposta == null) {
                    connection = Connection.SEM_CONEXAO
                } else {
                    resposta.second.optJSONObject("estado")?.let { withContext(disk) { sync.applySnapshot(it) } }
                    changed(false)
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                connection = Connection.SEM_CONEXAO
            } finally {
                startingMatch = false
                changed(false)
            }
        }
        return true
    }

    override fun dismissLostQueue() {
        sync.dismissLostQueue()
        changed(false)
    }

    override fun dismissDiscardNotice() {
        sync.dismissNotice()
        changed(false)
    }

    companion object {
        /** O celular publica o sinal de vida a cada 20 s; três perdidos e a sala conta como fechada. */
        const val VIDA_MS = 90_000L
        const val VERIFICACAO_MS = 10_000L
    }
}
