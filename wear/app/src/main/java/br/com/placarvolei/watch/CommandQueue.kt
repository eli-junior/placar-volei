package br.com.placarvolei.watch

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream

const val ACAO_PONTO = "ponto"
const val ACAO_DESFAZER = "desfazer"
const val ACAO_NOVA_PARTIDA = "nova_partida"

/**
 * Lance tocado no pulso, com a base (partida e versão do controle) vista no toque.
 * Ponto leva a equipe; desfazer leva o alvo: o seq de um ponto confirmado ou o
 * id de um lance anterior da fila.
 */
data class PendingCommand(
    val id: String,
    val partidaId: String,
    val controleVersao: Int,
    val equipe: String?,
    val acao: String = ACAO_PONTO,
    val alvoSeq: Int? = null,
    val alvoComando: String? = null,
)

/** Fila e motivo de pausa, gravados juntos para sobreviver ao fechamento do app. */
data class QueueState(val commands: List<PendingCommand> = emptyList(), val held: String? = null)

/**
 * Fila durável do relógio. Cada gravação escreve um arquivo temporário, força
 * o disco e troca pelo definitivo: um toque só aparece na tela depois de gravado.
 */
class CommandQueue(private val file: File) {
    fun load(): QueueState = runCatching {
        if (!file.exists()) return QueueState()
        val json = JSONObject(file.readText())
        val list = json.optJSONArray("comandos") ?: JSONArray()
        QueueState(
            commands = (0 until list.length()).map { i ->
                val c = list.getJSONObject(i)
                PendingCommand(
                    c.getString("id"), c.getString("partida_id"), c.getInt("controle_versao"),
                    c.nullableString("equipe"),
                    // Fila gravada pela 0.8.0 não tem `acao`: eram só pontos.
                    acao = c.optString("acao", ACAO_PONTO),
                    alvoSeq = if (c.has("alvo_seq") && !c.isNull("alvo_seq")) c.getInt("alvo_seq") else null,
                    alvoComando = c.nullableString("alvo_comando"),
                )
            },
            held = if (json.isNull("retido")) null else json.optString("retido"),
        )
    }.getOrElse { QueueState() }

    fun save(state: QueueState) {
        val json = JSONObject()
            .put("comandos", JSONArray().apply {
                state.commands.forEach {
                    put(it.toJson())
                }
            })
            .put("retido", state.held ?: JSONObject.NULL)
        val temp = File(file.parentFile, file.name + ".tmp")
        FileOutputStream(temp).use { out ->
            out.write(json.toString().toByteArray(Charsets.UTF_8))
            out.fd.sync()
        }
        check(temp.renameTo(file)) { "Não foi possível guardar o lance." }
    }
}

/** Mesmo formato no arquivo da fila e no corpo de `POST /api/watch/comandos`. */
fun PendingCommand.toJson(): JSONObject {
    val json = JSONObject().put("id", id).put("partida_id", partidaId)
        .put("controle_versao", controleVersao).put("acao", acao)
    equipe?.let { json.put("equipe", it) }
    alvoSeq?.let { json.put("alvo_seq", it) }
    alvoComando?.let { json.put("alvo_comando", it) }
    return json
}

private fun JSONObject.nullableString(key: String): String? =
    if (!has(key) || isNull(key)) null else getString(key)
