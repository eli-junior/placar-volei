package br.com.placarvolei.watch

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream

/** Lance tocado no pulso, com a base (partida e versão do controle) vista no toque. */
data class PendingCommand(val id: String, val partidaId: String, val controleVersao: Int, val equipe: String)

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
                PendingCommand(c.getString("id"), c.getString("partida_id"), c.getInt("controle_versao"), c.getString("equipe"))
            },
            held = if (json.isNull("retido")) null else json.optString("retido"),
        )
    }.getOrElse { QueueState() }

    fun save(state: QueueState) {
        val json = JSONObject()
            .put("comandos", JSONArray().apply {
                state.commands.forEach {
                    put(JSONObject().put("id", it.id).put("partida_id", it.partidaId)
                        .put("controle_versao", it.controleVersao).put("equipe", it.equipe))
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
