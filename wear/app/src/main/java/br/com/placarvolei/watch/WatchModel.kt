package br.com.placarvolei.watch

import android.app.Application
import android.util.Base64
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.File
import java.security.SecureRandom
import java.util.UUID
import java.util.concurrent.TimeUnit

enum class Connection { CONECTADO, RECONECTANDO, SEM_CONEXAO }

class WatchModel(app: Application) : AndroidViewModel(app) {
    private val store = CredentialStore(app)
    private val http = OkHttpClient.Builder().connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS).callTimeout(15, TimeUnit.SECONDS)
        .pingInterval(20, TimeUnit.SECONDS)
        .followRedirects(false).followSslRedirects(false).build()
    private var socket: WebSocket? = null
    private var visible = false
    // Endereço compilado no APK (CV3.DS1.US3): o relógio não edita o servidor.
    private val address = BuildConfig.SERVER_URL.trim().trimEnd('/')
    var code by mutableStateOf(store.code())
        private set
    var message by mutableStateOf("Vincule pelo telefone")
        private set
    var linked by mutableStateOf(false)
        private set
    var busy by mutableStateOf(false)
        private set
    var invalid by mutableStateOf(false)
        private set

    // Um vínculo por vez (CV3.DS1.US5): a atividade recriada abre na escolha
    // entre retornar à quadra e gerar um código novo. Tela que só apagou e
    // acendeu reaproveita este modelo e volta direto ao placar.
    var stage by mutableStateOf(
        openingStage(hasLink(), store.pendingToken() != null, store.cancelPending())
    )
        private set
    var linkCheck by mutableStateOf(LinkCheck.VERIFICANDO)
        private set
    /** Nome da quadra do vínculo guardado (ou "Quadra 48291", sem nome). */
    var court by mutableStateOf(store.courtName())
        private set
    /** Entrando na quadra guardada: a bola fica na tela até o servidor responder. */
    var connecting by mutableStateOf(false)
        private set
    /** Aviso na tela de abertura (código expirado, falha ao gerar). */
    var notice by mutableStateOf<String?>(null)
        private set
    private val poke = Channel<Unit>(Channel.CONFLATED)
    /** Espera antes de reabrir o socket caído; volta a 2 s quando ele abre. */
    private var reconnectDelay = 2_000L

    // Placar (CV3.DS1.US2, TS1): confirmado pelo servidor + fila durável de
    // lances, persistidos juntos na `ScoreSync`. `rev` avisa a tela a cada mudança.
    private val sync = ScoreSync(CommandQueue(File(app.filesDir, "fila-lances.json")))
    private var rev by mutableIntStateOf(0)
    private val wake = Channel<Unit>(Channel.CONFLATED)
    val score get() = rev.let { sync.score }
    val participantId get() = rev.let { sync.participantId }
    var connection by mutableStateOf(Connection.RECONECTANDO)
        private set
    val pending get() = rev.let { sync.pending }
    val held get() = rev.let { sync.held }
    val labels get() = score?.let(::teamLabels) ?: ("Nós" to "Eles")
    val shown get() = score?.let { predicted(it, pending) }

    /** O controle do placar está com este relógio. */
    val controlled get() = rev.let { sync.controlled }

    /** Por que os botões de ponto estão travados agora; null = pode marcar. */
    val blockReason get() = rev.let { sync.blockReason }

    /** Desfazer segue valendo com a vitória prevista ou a partida encerrada. */
    val canUndo get() = rev.let { sync.canUndo }

    /** Grava o lance antes de qualquer retorno visual. Devolve se foi aceito. */
    fun tap(equipe: String) = changed(sync.tap(equipe))

    /** Grava na fila o desfazer do ponto visto no topo, antes do retorno visual. */
    fun undo() = changed(sync.undo())

    /** Depois de mexer na `ScoreSync`: atualiza a tela e acorda o envio. */
    private fun changed(accepted: Boolean = true): Boolean {
        rev++
        sync.saveError?.let { message = it }
        if (accepted) wake.trySend(Unit)
        return accepted
    }

    /** Dono do relógio é admin da quadra (CV3.DS2.US3); vem de `/api/watch/session`. */
    var ownerAdmin by mutableStateOf(false)
        private set
    /** Pedido de nova partida em andamento: o botão não aceita outro toque. */
    var startingMatch by mutableStateOf(false)
        private set
    // Mesmo id para a mesma partida encerrada: reenviar nunca cria duas.
    private var newMatchId: Pair<String, String>? = null

    /** Partida encerrada com o controle: a faixa de baixo ganha "▶ Nova". */
    val showNewMatch get() = controlled && ownerAdmin && score?.encerrada == true

    /** Só com conexão e fila vazia: a partida nova não entra na fila offline. */
    val canStartNewMatch get() = showNewMatch && sync.controlReason == null && pending.isEmpty() &&
        connection == Connection.CONECTADO && !startingMatch

    /** Nova partida nos mesmos moldes (CV3.DS2.US3), enviada direto ao servidor. */
    fun startNewMatch(): Boolean {
        val s = score ?: return false
        if (!canStartNewMatch) return false
        val id = newMatchId?.takeIf { it.first == s.partidaId }?.second ?: UUID.randomUUID().toString()
        newMatchId = s.partidaId to id
        startingMatch = true
        viewModelScope.launch {
            try {
                val body = PendingCommand(id, s.partidaId, s.controleVersao, null, ACAO_NOVA_PARTIDA).toJson()
                val (status, data) = request("/api/watch/comandos", body = body.toString())
                when {
                    status == 401 -> unlink(data)
                    data.has("recibo") -> {
                        data.optJSONObject("estado")?.let { sync.applySnapshot(it); changed(false) }
                        val recibo = data.getJSONObject("recibo")
                        if (recibo.optString("status") != "APLICADO") message = recibo.optString("detalhe")
                    }
                    else -> message = data.optString("detail", "Não foi possível iniciar a partida.")
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                connection = Connection.SEM_CONEXAO
            } finally { startingMatch = false }
        }
        return true
    }

    /** Descarte explícito, confirmado no relógio, dos lances retidos por recusa. */
    fun discardHeld() {
        sync.discardHeld()
        changed()
    }

    private suspend fun sendLoop() {
        var backoff = 1_000L
        while (true) {
            if (!linked || stage != Stage.PLACAR) {
                wake.receive()
                continue
            }
            val (result, data) = try {
                sync.sendNext { body ->
                    try {
                        request("/api/watch/comandos", body = body.toString())
                    } catch (e: CancellationException) {
                        throw e
                    } catch (e: Exception) {
                        null
                    }
                }
            } finally { changed(false) }
            when (result) {
                SendResult.OCIOSO -> wake.receive()
                SendResult.SEM_REDE -> {
                    // Sem rede: o lance continua na fila e volta a ser enviado.
                    connection = Connection.SEM_CONEXAO
                    withTimeoutOrNull(backoff) { wake.receive() }
                    backoff = (backoff * 2).coerceAtMost(15_000L)
                }
                SendResult.NAO_AUTORIZADO -> unlink(data ?: JSONObject())
                SendResult.ENVIADO -> {
                    backoff = 1_000L
                    connection = Connection.CONECTADO
                }
            }
        }
    }

    private fun unlink(data: JSONObject) {
        linked = false
        invalid = true
        code = ""
        message = data.optString("detail", "Vínculo indisponível. Use o telefone.")
    }

    private suspend fun request(
        path: String, post: Boolean = false, body: String? = null,
        token: String? = null, delete: Boolean = false,
    ): Pair<Int, JSONObject> = withContext(Dispatchers.IO) {
        val bearer = token ?: store.token() ?: error("Gere um código para começar.")
        val builder = Request.Builder().url(address + path).header("Authorization", "Bearer $bearer")
        if (body != null) builder.post(body.toRequestBody("application/json".toMediaType()))
        else if (post) builder.post(ByteArray(0).toRequestBody())
        else if (delete) builder.delete()
        http.newCall(builder.build()).execute().use { response ->
            val text = response.body?.string().orEmpty()
            val json = runCatching { JSONObject(text) }.getOrElse { JSONObject() }
            if (response.isRedirect) error("Use o endereço final HTTPS do servidor.")
            response.code to json
        }
    }

    fun generateCode() = viewModelScope.launch {
        if (busy) return@launch
        busy = true
        try {
            serverAddress(address, BuildConfig.DEBUG)
            // Persistir antes da rede permite recuperar aprovação após resposta perdida.
            if (!hasLink() || invalid) store.saveToken(newToken(), address)
            val (status, data) = request("/api/watch/pairing", true)
            if (status == 409) {
                refresh()
            } else {
                check(status == 201) { data.optString("detail", "Não foi possível gerar o código.") }
                code = data.getString("code")
                store.saveCode(code)
                invalid = false
                notice = null
                message = "No telefone: Relógio → digite este código. Válido por 5 minutos."
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            notice = e.message ?: "Sem conexão. Tente novamente."
        } finally { busy = false }
    }

    private fun newToken(): String {
        val bytes = ByteArray(32).also { SecureRandom().nextBytes(it) }
        return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
    }

    /** "Retornar à quadra": só agora começam presença e envio da fila. */
    fun returnToCourt() {
        notice = null
        connecting = true
        stage = Stage.PLACAR
        poke.trySend(Unit)
    }

    /** "Gerar novo código": com lances pendentes, pede confirmação antes. */
    fun requestNewCode() {
        notice = null
        if (abandonWarning(pending.size, court) != null) stage = Stage.CONFIRMAR_TROCA
        else startReplacement()
    }

    fun backToOpening() { stage = Stage.ABERTURA }

    /**
     * Código novo com token novo, informando o vínculo que ele substitui. O
     * vínculo atual, a fila e o token ficam intactos até a aprovação.
     */
    fun startReplacement() = viewModelScope.launch {
        if (busy) return@launch
        busy = true
        try {
            val current = store.token() ?: error("Vínculo não encontrado. Gere um código.")
            val token = newToken()
            store.savePendingToken(token)
            val body = JSONObject().put("substitui", current).toString()
            val (status, data) = request("/api/watch/pairing", body = body, token = token)
            check(status == 201) { data.optString("detail", "Não foi possível gerar o código.") }
            code = data.getString("code")
            store.saveCode(code)
            message = "No telefone: Relógio → digite este código. Válido por 5 minutos."
            stage = Stage.CODIGO_NOVO
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            // Sem código na tela, ninguém aprova o pedido que ficou no servidor.
            runCatching { store.clearPending() }
            notice = e.message ?: "Sem conexão. Tente novamente."
            stage = Stage.ABERTURA
        } finally { busy = false }
    }

    /** "Voltar à quadra": cancela o código novo no servidor e volta ao placar. */
    fun giveUp() {
        runCatching {
            store.markCancelPending()
            store.saveCode("")
        }
        code = ""
        stage = Stage.PLACAR
        poke.trySend(Unit)
    }

    /**
     * Resolve o código novo: refaz o cancelamento pendente ou confere se o
     * telefone já aprovou. Aprovado (ou aprovado antes do cancelamento chegar),
     * o relógio adota o vínculo novo, que é o que o servidor já fez.
     */
    private suspend fun settlePending() {
        val token = store.pendingToken() ?: return
        if (store.cancelPending()) {
            when (request("/api/watch/pairing", token = token, delete = true).first) {
                204 -> store.clearPending()
                409 -> adopt(token)
            }
            return
        }
        if (stage != Stage.CODIGO_NOVO) return
        val (status, data) = request("/api/watch/session", token = token)
        when {
            status == 200 && data.optString("status") == "linked" -> adopt(token)
            status == 401 || status == 410 -> {
                store.clearPending()
                store.saveCode("")
                code = ""
                notice = data.optString("detail", "Código expirado.")
                stage = Stage.ABERTURA
            }
        }
    }

    private suspend fun adopt(token: String) {
        val (status, data) = request("/api/watch/session", token = token)
        if (status != 200 || data.optString("status") != "linked") {
            store.clearPending()
            return
        }
        store.promotePending(courtLabel(data.optString("court_name"), data.getString("court_id")).orEmpty())
        court = store.courtName()
        // Lances da quadra anterior: o abandono foi confirmado ao gerar o código.
        sync.reset()
        changed(false)
        socket?.let { old -> socket = null; old.close(1000, null) }
        linked = false
        invalid = false
        code = ""
        connecting = true
        stage = Stage.PLACAR
        refresh()
    }

    private fun saveCourt(session: JSONObject): String? =
        courtLabel(session.optString("court_name"), session.optString("court_id"))?.also(store::saveCourtName)

    /** Tela de abertura: confere o vínculo guardado sem entrar na sala. */
    private suspend fun checkOpening() {
        val (status, data) = request("/api/watch/session")
        when {
            status == 200 && data.optString("status") == "linked" -> {
                linkCheck = LinkCheck.VALIDO
                court = saveCourt(data)
            }
            // Primeiro código ainda sem aprovação, ou vínculo que caiu: fluxo de vínculo.
            status == 200 || status == 401 || status == 410 -> {
                stage = Stage.PLACAR
                poke.trySend(Unit)
            }
            else -> linkCheck = LinkCheck.SEM_REDE
        }
    }

    /** Token guardado para este servidor; o de outro endereço não vale mais. */
    private fun hasLink() = store.token() != null && store.server() == address

    private suspend fun refresh() {
        val (status, data) = request("/api/watch/session")
        when {
            status == 200 && data.optString("status") == "linked" -> {
                connecting = false
                notice = null
                linked = true
                invalid = false
                code = ""
                store.saveCode("")
                sync.setParticipant(data.optString("participant_id").ifBlank { null })
                changed(false)
                ownerAdmin = data.optBoolean("pode_nova_partida", false)
                court = saveCourt(data)
                message = "Vinculado como ${data.getString("display_name")}\nSala ${data.getString("court_id")}"
                connectPresence(data.getString("court_id"))
                val (stateStatus, snapshot) = request("/api/watch/state")
                if (stateStatus == 200) { sync.applySnapshot(snapshot); changed(false) }
                wake.trySend(Unit)
            }
            status == 200 -> { connecting = false; linked = false; message = "Aguardando autorização no telefone." }
            status == 401 || status == 410 -> {
                connecting = false
                linked = false
                invalid = true
                code = ""
                message = data.optString("detail", "Gere um novo código.")
            }
            else -> error(data.optString("detail", "Servidor indisponível. Tente novamente."))
        }
    }

    private fun connectPresence(court: String) {
        if (!visible || socket != null) return
        val url = address.replaceFirst("https://", "wss://").replaceFirst("http://", "ws://")
        val request = Request.Builder().url("$url/ws/$court")
            .header("Authorization", "Bearer ${store.token()}").build()
        connection = Connection.RECONECTANDO
        socket = http.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                viewModelScope.launch {
                    if (socket === webSocket) { connection = Connection.CONECTADO; reconnectDelay = 2_000L }
                }
            }
            override fun onMessage(webSocket: WebSocket, text: String) {
                // Snapshot interpretado fora da thread principal; aplicado nela.
                val payload = runCatching {
                    val json = JSONObject(text)
                    if (json.optString("tipo") in setOf("ESTADO_INICIAL", "PLACAR_ATUALIZADO")) {
                        json.getJSONObject("payload").also { Confirmed.fromSnapshot(it) }
                    } else null
                }.getOrNull() ?: return
                viewModelScope.launch {
                    if (socket !== webSocket) return@launch
                    // Lance já confirmado: sai da fila junto com o snapshot, sem contar duas vezes.
                    sync.applySnapshot(payload, payload.optString("comando_id").ifBlank { null })
                    changed(false)
                }
            }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                viewModelScope.launch {
                    if (socket === webSocket) {
                        socket = null
                        poke.trySend(Unit)
                        if (code == 4401 || code == 4404) {
                            linked = false
                            invalid = true
                            message = "Vínculo indisponível. Use o telefone."
                        }
                    }
                }
            }
            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(code, null)
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                viewModelScope.launch {
                    if (socket === webSocket) {
                        socket = null
                        poke.trySend(Unit)
                        connection = Connection.SEM_CONEXAO
                        message = "Sem conexão. Tentando novamente."
                    }
                }
            }
        })
    }

    suspend fun observeWhileVisible() = coroutineScope {
        visible = true
        // O envio só roda com o app visível; em segundo plano fica para a US4.
        val sender = launch { sendLoop() }
        try {
        while (true) {
            if (!busy) {
                try {
                    settlePending()
                    when (stage) {
                        Stage.ABERTURA -> checkOpening()
                        // Com o socket aberto, o servidor avisa tudo por ele
                        // (placar, controle, revogação 4401): sem polling.
                        Stage.PLACAR -> if (hasLink() && !(linked && socket != null)) refresh()
                        else -> Unit
                    }
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    connection = Connection.SEM_CONEXAO
                    when (stage) {
                        Stage.ABERTURA -> linkCheck = LinkCheck.SEM_REDE
                        // O código segue na tela: as instruções continuam valendo.
                        Stage.CODIGO_NOVO, Stage.CONFIRMAR_TROCA -> Unit
                        Stage.PLACAR -> {
                            message = "Sem conexão. Vínculo preservado; tentando novamente."
                            if (connecting) notice = "Sem conexão. Tentando novamente."
                        }
                    }
                }
            }
            val wait = when {
                stage == Stage.CODIGO_NOVO -> 3_000L
                stage != Stage.PLACAR -> 5_000L
                linked && socket != null -> Long.MAX_VALUE
                linked -> reconnectDelay.also { reconnectDelay = (it * 2).coerceAtMost(30_000L) }
                else -> 3_000L
            }
            withTimeoutOrNull(wait) { poke.receive() }
        }
        } finally {
            sender.cancel()
            connection = Connection.RECONECTANDO
            visible = false
            socket?.close(1000, null)
            socket = null
        }
    }
}
