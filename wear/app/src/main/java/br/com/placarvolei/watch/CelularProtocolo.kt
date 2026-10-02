package br.com.placarvolei.watch

import org.json.JSONObject
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.withTimeoutOrNull

/**
 * Contrato com a quadra local do celular pelo Wearable Data Layer (CV7.TS3).
 * Os corpos são os do servidor: o lance é o de `POST /api/watch/comandos` e a
 * resposta é `{id, status, recibo, estado}` (ou `{id, status, detail}`), para a
 * `ScoreSync` tratar celular e servidor do mesmo jeito.
 */
object CelularProtocolo {
    const val CAMINHO_ESTADO = "/placar/local/estado"
    const val CAMINHO_COMANDO = "/placar/local/comando"
    const val CAMINHO_RECIBO = "/placar/local/recibo"
    /** Relógio recém-aberto pede o estado agora, sem esperar o sinal de vida do celular. */
    const val CAMINHO_PING = "/placar/local/ping"
    const val CAPACIDADE_CELULAR = "placar_celular"

    /** Participante fixo do relógio na quadra local: o controle é sempre dele. */
    const val ID_RELOGIO = "relogio-local"

    fun codificarComando(corpo: JSONObject): ByteArray = corpo.toString().toByteArray(Charsets.UTF_8)

    /** Resposta do celular: o id do lance a que responde e o par (status, corpo). */
    fun decodificarResposta(bytes: ByteArray): Pair<String, Pair<Int, JSONObject>>? = runCatching {
        val json = JSONObject(String(bytes, Charsets.UTF_8))
        val id = json.getString("id")
        val status = json.getInt("status")
        json.remove("id")
        json.remove("status")
        id to (status to json)
    }.getOrNull()

    /**
     * O celular está com a sala local aberta? Só um celular com a CV7.US2 diz
     * `sala_aberta`; sem o campo, o relógio não entra na quadra local.
     */
    fun salaAberta(estado: JSONObject): Boolean = estado.optBoolean("sala_aberta", false)

    /** Estado publicado como DataItem; só vale se for um snapshot legível. */
    fun decodificarEstado(bytes: ByteArray): JSONObject? = runCatching {
        JSONObject(String(bytes, Charsets.UTF_8)).also { Confirmed.fromSnapshot(it) }
    }.getOrNull()
}

/**
 * Lances à espera da resposta do celular, por id. O envio e a chegada da
 * resposta (outro thread, no serviço do Data Layer) se encontram aqui.
 */
class RespostasEsperadas {
    private val esperando = ConcurrentHashMap<String, CompletableDeferred<Pair<Int, JSONObject>>>()

    /**
     * Registra a espera antes de enviar, para a resposta nunca chegar antes dela.
     * `enviar` devolve false se a mensagem nem saiu (sem celular ao alcance).
     */
    suspend fun aguardar(id: String, tempoMs: Long, enviar: suspend () -> Boolean): Pair<Int, JSONObject>? {
        val espera = CompletableDeferred<Pair<Int, JSONObject>>()
        esperando[id] = espera
        try {
            if (!enviar()) return null
            return withTimeoutOrNull(tempoMs) { espera.await() }
        } finally {
            esperando.remove(id)
        }
    }

    /** Devolve se havia alguém esperando por essa resposta. */
    fun entregar(bytes: ByteArray): Boolean {
        val (id, resposta) = CelularProtocolo.decodificarResposta(bytes) ?: return false
        return esperando[id]?.complete(resposta) == true
    }
}
