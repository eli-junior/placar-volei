package br.com.placarvolei.watch

import org.json.JSONArray
import org.json.JSONObject

/** Estado confirmado pelo servidor, extraído do snapshot da sala. */
data class Confirmed(
    val partidaId: String,
    val seq: Int,
    val controleVersao: Int,
    val controleId: String?,
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
    /** Pontos ativos confirmados, em ordem: (seq, equipe). Topo = último. */
    val ativos: List<Pair<Int, String>> = emptyList(),
) {
    companion object {
        fun fromSnapshot(json: JSONObject): Confirmed {
            val sala = json.getJSONObject("quadra")
            val partida = json.getJSONObject("estado_partida")
            return Confirmed(
                partidaId = json.getString("partida_id"),
                seq = json.optInt("seq", 0),
                controleVersao = sala.optInt("controle_versao", 0),
                controleId = sala.optString("controle_id").takeUnless { sala.isNull("controle_id") || it.isEmpty() },
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
                ativos = actives(partida),
            )
        }

        /** Sem `equipes_ativas` coerente, nenhum ponto confirmado é desfazível no relógio. */
        private fun actives(partida: JSONObject): List<Pair<Int, String>> {
            val seqs = partida.optJSONArray("eventos_ativos_seq") ?: return emptyList()
            val teams = partida.optJSONArray("equipes_ativas").strings()
            if (teams.size != seqs.length()) return emptyList()
            return (0 until seqs.length()).map { seqs.getInt(it) to teams[it] }
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

/** Ponto na pilha prevista: confirmado (com seq) ou lance ainda na fila (com id). */
data class StackPoint(val equipe: String, val seq: Int? = null, val comando: String? = null)

/**
 * Pilha prevista (CV3.DS1.US3): pontos confirmados ativos e, em cima deles, os
 * lances pendentes desta partida. Cada desfazer na fila tira o topo.
 */
fun stack(confirmed: Confirmed, pending: List<PendingCommand>): List<StackPoint> {
    val points = confirmed.ativos.map { (seq, equipe) -> StackPoint(equipe, seq = seq) }.toMutableList()
    pending.filter { it.partidaId == confirmed.partidaId }.forEach {
        if (it.acao == ACAO_DESFAZER) points.removeLastOrNull()
        else points += StackPoint(it.equipe.orEmpty(), comando = it.id)
    }
    return points
}

/** Placar previsto: confirmado + o efeito dos lances pendentes desta partida. */
fun predicted(confirmed: Confirmed, pending: List<PendingCommand>): Pair<Int, Int> {
    val base = confirmed.ativos.map { it.second }
    val top = stack(confirmed, pending).map { it.equipe }
    return (confirmed.pontosA + top.count { it == "A" } - base.count { it == "A" }) to
        (confirmed.pontosB + top.count { it == "B" } - base.count { it == "B" })
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
