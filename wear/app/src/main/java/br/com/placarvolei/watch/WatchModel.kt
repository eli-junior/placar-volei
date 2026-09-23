package br.com.placarvolei.watch

import android.app.Application
import android.util.Base64
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.security.SecureRandom
import java.util.concurrent.TimeUnit

class WatchModel(app: Application) : AndroidViewModel(app) {
    private val store = CredentialStore(app)
    private val http = OkHttpClient.Builder().connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS).callTimeout(15, TimeUnit.SECONDS)
        .pingInterval(20, TimeUnit.SECONDS)
        .followRedirects(false).followSslRedirects(false).build()
    private var socket: WebSocket? = null
    private var visible = false
    var server by mutableStateOf(store.server())
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

    private suspend fun request(path: String, post: Boolean = false): Pair<Int, JSONObject> = withContext(Dispatchers.IO) {
        val token = store.token() ?: error("Gere um código para começar.")
        val builder = Request.Builder().url(store.server() + path).header("Authorization", "Bearer $token")
        if (post) builder.post(ByteArray(0).toRequestBody())
        http.newCall(builder.build()).execute().use { response ->
            val body = response.body?.string().orEmpty()
            val json = runCatching { JSONObject(body) }.getOrElse { JSONObject() }
            if (response.isRedirect) error("Use o endereço final HTTPS do servidor.")
            response.code to json
        }
    }

    fun generateCode() = viewModelScope.launch {
        if (busy) return@launch
        busy = true
        try {
            val address = serverAddress(server, BuildConfig.DEBUG)
            // Persistir antes da rede permite recuperar aprovação após resposta perdida.
            if (store.token() == null || invalid || address != store.server()) {
                val bytes = ByteArray(32).also { SecureRandom().nextBytes(it) }
                store.saveToken(Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING), address)
            }
            val (status, data) = request("/api/watch/pairing", true)
            if (status == 409) {
                refresh()
            } else {
                check(status == 201) { data.optString("detail", "Não foi possível gerar o código.") }
                code = data.getString("code")
                store.saveCode(code)
                invalid = false
                message = "No telefone: Relógio → digite este código. Válido por 5 minutos."
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            message = e.message ?: "Sem conexão. Tente novamente."
        } finally { busy = false }
    }

    private suspend fun refresh() {
        val (status, data) = request("/api/watch/session")
        when {
            status == 200 && data.optString("status") == "linked" -> {
                linked = true
                invalid = false
                code = ""
                store.saveCode("")
                message = "Vinculado como ${data.getString("display_name")}\nSala ${data.getString("court_id")}"
                connectPresence(data.getString("court_id"))
            }
            status == 200 -> { linked = false; message = "Aguardando autorização no telefone." }
            status == 401 || status == 410 -> {
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
        val url = store.server().replaceFirst("https://", "wss://").replaceFirst("http://", "ws://")
        val request = Request.Builder().url("$url/ws/$court")
            .header("Authorization", "Bearer ${store.token()}").build()
        socket = http.newWebSocket(request, object : WebSocketListener() {
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                viewModelScope.launch {
                    if (socket === webSocket) {
                        socket = null
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
                        message = "Sem conexão. Tentando novamente."
                    }
                }
            }
        })
    }

    suspend fun observeWhileVisible() {
        visible = true
        try {
        while (true) {
            if (!busy) {
                try {
                    if (store.token() != null) refresh()
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    message = "Sem conexão. Vínculo preservado; tentando novamente."
                }
            }
            delay(if (linked) 15_000 else 3_000)
        }
        } finally {
            visible = false
            socket?.close(1000, null)
            socket = null
        }
    }
}
