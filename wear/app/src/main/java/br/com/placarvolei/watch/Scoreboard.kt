package br.com.placarvolei.watch

import org.json.JSONArray
import org.json.JSONObject

/** Estado confirmado pelo servidor, extraído do snapshot da sala. */
data class Confirmed(
    val partidaId: String,
    val seq: Int,
    val relogioVersao: Int,
    val controleRelogio: String?,
    val pontosA: Int,
    val pontosB: Int,
    val alvo: Int,
    val vantagem: Boolean,
    val teto: Int?,
    val encerrada: Boolean,
    val equipeA: String,
    val equipeB: String,
    val jogadoresA: List<String>,
    val jogadoresB: List<String>,
) {
    companion object {
        fun fromSnapshot(json: JSONObject): Confirmed {
            val sala = json.getJSONObject("quadra")
            val partida = json.getJSONObject("estado_partida")
            return Confirmed(
                partidaId = json.getString("partida_id"),
                seq = json.optInt("seq", 0),
                relogioVersao = sala.optInt("relogio_versao", 0),
                controleRelogio = sala.optString("controle_relogio").takeUnless { sala.isNull("controle_relogio") || it.isEmpty() },
                pontosA = partida.getInt("pontos_a"),
                pontosB = partida.getInt("pontos_b"),
                alvo = partida.optInt("alvo", 12),
                vantagem = partida.optBoolean("vantagem", true),
                teto = if (partida.isNull("teto")) null else partida.optInt("teto"),
                encerrada = partida.optBoolean("encerrada", false),
                equipeA = partida.optString("equipe_a", "Equipe A"),
                equipeB = partida.optString("equipe_b", "Equipe B"),
                jogadoresA = partida.optJSONArray("jogadores_a").strings(),
                jogadoresB = partida.optJSONArray("jogadores_b").strings(),
            )
        }

        private fun JSONArray?.strings() =
            if (this == null) emptyList() else (0 until length()).map { getString(it) }
    }

    /** Aceita um snapshot novo: outra partida ou log igual/mais avançado. */
    fun accepts(next: Confirmed) = next.partidaId != partidaId || next.seq >= seq
}

/** Espelho de `app.projecao.avaliar_vitoria`; o servidor continua a autoridade. */
fun avaliarVitoria(a: Int, b: Int, alvo: Int, vantagem: Boolean, teto: Int?): String? {
    if (vantagem) {
        if (teto != null && a >= teto && a > b) return "A"
        if (teto != null && b >= teto && b > a) return "B"
        if (a >= alvo && a - b >= 2) return "A"
        if (b >= alvo && b - a >= 2) return "B"
    } else {
        if (a >= alvo && a > b) return "A"
        if (b >= alvo && b > a) return "B"
    }
    return null
}

/** Placar previsto: confirmado + lances pendentes que valem para esta partida. */
fun predicted(confirmed: Confirmed, pending: List<PendingCommand>): Pair<Int, Int> {
    val valid = pending.filter { it.partidaId == confirmed.partidaId }
    return (confirmed.pontosA + valid.count { it.equipe == "A" }) to
        (confirmed.pontosB + valid.count { it.equipe == "B" })
}

/**
 * Rótulos no pulso: "Nós" (equipe A) e "Eles" (equipe B) com nomes padrão;
 * com nomes personalizados, as iniciais. Iniciais iguais voltam a Nós/Eles.
 */
fun teamLabels(confirmed: Confirmed): Pair<String, String> {
    val a = initials(confirmed.equipeA, confirmed.jogadoresA, "Equipe A")
    val b = initials(confirmed.equipeB, confirmed.jogadoresB, "Equipe B")
    if (a == null || b == null || a == b) return "Nós" to "Eles"
    return a to b
}

internal fun initials(name: String, players: List<String>, default: String): String? {
    val named = players.map { it.trim() }.filter { it.isNotEmpty() }
    if (named.isNotEmpty()) return named.joinToString("") { it.first().uppercase() }
    val clean = name.trim()
    if (clean.isEmpty() || clean.equals(default, ignoreCase = true)) return null
    val words = clean.split(Regex("\\s+")).filter { it.isNotEmpty() }
    return if (words.size >= 2) words.take(2).joinToString("") { it.first().uppercase() }
    else words.first().take(2).uppercase()
}
