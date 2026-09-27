package br.com.placarvolei.watch

import android.view.HapticFeedbackConstants
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.ChipDefaults
import androidx.wear.compose.material.Text
import androidx.compose.ui.platform.LocalConfiguration
import kotlinx.coroutines.delay

private val CorNos = Color(0xFFFFB020)
private val CorEles = Color(0xFF4FC3F7)

/**
 * Placar no pulso (CV3.DS1.US2): metade esquerda = Nós (equipe A), direita =
 * Eles (equipe B). O toque grava o lance antes de vibrar e de mudar o número.
 */
@Composable
fun ScoreScreen(model: WatchModel) {
    val score = model.score ?: return
    val (pontosA, pontosB) = model.shown ?: (score.pontosA to score.pontosB)
    val (rotuloA, rotuloB) = model.labels
    val reason = model.blockReason
    val pending = model.pending.size
    val view = LocalView.current
    // Tela acesa só no placar (CV3.DS2.US1): no jogo, o toque tem de estar
    // pronto sem acordar o relógio. Vínculo e escolha seguem o tempo normal.
    // Liberada depois de 10 min sem toque nem mudança no placar (CV5.DS2.TS3):
    // placar esquecido aberto não segura a tela até a bateria acabar.
    LaunchedEffect(view, pontosA, pontosB, pending) {
        view.keepScreenOn = true
        delay(SCREEN_IDLE_MS)
        view.keepScreenOn = false
    }
    DisposableEffect(view) { onDispose { view.keepScreenOn = false } }
    val heart = rememberHeartRate()
    fun tap(equipe: String) {
        model.tap(equipe) { ok -> if (ok) view.performHapticFeedback(HapticFeedbackConstants.CONFIRM) }
    }
    fun newMatch() {
        if (model.startNewMatch()) view.performHapticFeedback(HapticFeedbackConstants.CONFIRM)
    }
    fun undo() {
        // Vibração diferente da do ponto: o pulso sente que foi uma correção.
        model.undo { ok -> if (ok) view.performHapticFeedback(HapticFeedbackConstants.REJECT) }
    }

    Box(Modifier.fillMaxSize().background(Color.Black)) {
        Row(Modifier.fillMaxSize()) {
            TeamHalf(rotuloA, pontosA, CorNos, reason == null, pending > 0, Modifier.weight(1f)) { tap("A") }
            Box(Modifier.fillMaxHeight().width(2.dp).background(Color(0xFF333333)))
            TeamHalf(rotuloB, pontosB, CorEles, reason == null, pending > 0, Modifier.weight(1f)) { tap("B") }
        }
        Row(
            Modifier.align(Alignment.TopCenter).padding(top = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            StatusDot(model.connection, pending, Modifier)
            if (heart.granted) HeartText(heart.bpm)
        }
        if (model.controlled) {
            // Com o controle, a faixa de baixo é o desfazer; o motivo (fim de
            // partida) sobe para baixo da bolinha, longe dos números.
            if (model.showNewMatch) {
                UndoAndNewBar(
                    model.canUndo, model.canStartNewMatch, model.undoSpoken, Modifier.align(Alignment.BottomCenter),
                    ::undo, ::newMatch, onArm = { view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK) },
                )
            } else {
                UndoBar(model.canUndo, model.undoText, model.undoSpoken, Modifier.align(Alignment.BottomCenter), ::undo)
            }
            if (reason != null && model.held == null) {
                ReasonText(reason, Modifier.align(Alignment.TopCenter).padding(top = 34.dp))
            }
        } else if (reason != null && model.held == null) {
            // Sem o controle não há o que desfazer: a faixa some e o aviso fica embaixo.
            ReasonText(reason, Modifier.align(Alignment.BottomCenter).padding(bottom = 22.dp))
        }
        model.held?.let { HeldOverlay(it, pending, model::discardHeld) }
        if (model.lostQueue && model.held == null) LostQueueOverlay(model::dismissLostQueue)
    }
}

/** Tela do placar acesa sem atividade por no máximo 10 min. */
internal const val SCREEN_IDLE_MS = 10 * 60 * 1000L

enum class Signal { CONECTADO, PROCESSANDO, DESCONECTADO }

/** Verde: conectado e sem pendentes. Amarelo: enviando ou reconectando. Vermelho: sem conexão. */
internal fun signal(connection: Connection, pending: Int) = when {
    connection == Connection.SEM_CONEXAO -> Signal.DESCONECTADO
    connection == Connection.RECONECTANDO || pending > 0 -> Signal.PROCESSANDO
    else -> Signal.CONECTADO
}

/** Texto da bolinha para leitores de tela: a cor sozinha não informa. */
internal fun statusLine(connection: Connection, pending: Int): String {
    val link = when (connection) {
        Connection.CONECTADO -> "Conectado"
        Connection.RECONECTANDO -> "Reconectando…"
        Connection.SEM_CONEXAO -> "Sem conexão"
    }
    return when (pending) {
        0 -> link
        1 -> "$link · 1 pendente"
        else -> "$link · $pending pendentes"
    }
}

@Composable
private fun TeamHalf(
    label: String,
    points: Int,
    color: Color,
    enabled: Boolean,
    predicted: Boolean,
    modifier: Modifier,
    onTap: () -> Unit,
) {
    Box(
        modifier
            .fillMaxHeight()
            .background(color.copy(alpha = if (enabled) 0.16f else 0.06f))
            .clickable(enabled = enabled, onClick = onTap)
            // Número previsto ainda não confirmado: o leitor de tela diz (CV5.DS4.US1).
            .semantics { contentDescription = "$label, $points pontos${if (predicted) " (enviando)" else ""}. Tocar marca ponto." },
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Text(label, fontSize = 22.sp, fontWeight = FontWeight.Bold, color = color)
            AnimatedContent(
                targetState = points,
                // Ponto sobe; ponto desfeito desce, para ser visivelmente desfeito.
                transitionSpec = {
                    val up = if (targetState >= initialState) 1 else -1
                    (slideInVertically { up * it / 3 } + fadeIn()) togetherWith (slideOutVertically { -up * it / 3 } + fadeOut())
                },
                label = "Pontos $label",
            ) { value ->
                // Número previsto (ainda não confirmado) fica mais apagado e sublinhado por um traço.
                Text(
                    value.toString(),
                    fontSize = 58.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (predicted) Color.White.copy(alpha = 0.7f) else Color.White,
                )
            }
            Spacer(
                Modifier.width(28.dp).height(3.dp)
                    .background(if (predicted) color.copy(alpha = 0.8f) else Color.Transparent)
            )
        }
    }
}

/** Bolinha de conexão no alto; com lances pendentes, mostra quantos. */
@Composable
private fun StatusDot(connection: Connection, pending: Int, modifier: Modifier) {
    val color = when (signal(connection, pending)) {
        Signal.CONECTADO -> Color(0xFF4CD964)
        Signal.PROCESSANDO -> Color(0xFFFFC83D)
        Signal.DESCONECTADO -> Color(0xFFFF4D4D)
    }
    val description = statusLine(connection, pending)
    Box(
        modifier.size(22.dp).clip(CircleShape).background(color)
            .semantics { contentDescription = description },
        contentAlignment = Alignment.Center,
    ) {
        if (pending > 0) {
            Text(if (pending > 9) "9+" else pending.toString(), fontSize = 11.sp, fontWeight = FontWeight.Bold, color = Color.Black)
        }
    }
}

/** Batimento ao lado da bolinha; fica só no relógio (CV3.DS2.US2). */
@Composable
private fun HeartText(bpm: Int?) {
    val label = heartLabel(bpm)
    val description = if (label == "♥ --") "Batimento sem leitura" else "Batimento $bpm por minuto"
    Text(
        label,
        Modifier.semantics { contentDescription = description },
        fontSize = 13.sp,
        fontWeight = FontWeight.Bold,
        color = Color(0xFFFF6B81),
    )
}

@Composable
private fun ReasonText(reason: String, modifier: Modifier) {
    Text(
        reason,
        modifier.padding(horizontal = if (LocalConfiguration.current.isScreenRound) 36.dp else 16.dp),
        fontSize = 13.sp,
        textAlign = TextAlign.Center,
        color = Color.White,
    )
}

/**
 * Desfazer o ponto do topo: a faixa inferior inteira, um toque, sem confirmação,
 * como no site. Diz de qual equipe é o ponto (CV5.DS4.US1).
 */
@Composable
private fun UndoBar(enabled: Boolean, label: String, spoken: String, modifier: Modifier, onTap: () -> Unit) =
    BottomBar(label, enabled, modifier, spoken, onTap = onTap)

/** Tempo para o segundo toque confirmar "Nova" (CV5.DS4.US1). */
internal const val NEW_MATCH_CONFIRM_MS = 3_000L

/**
 * Partida encerrada (CV3.DS2.US3): a faixa se divide em desfazer e nova partida.
 * No mostrador redondo, cada texto encosta no meio, onde a faixa é larga.
 */
@Composable
private fun UndoAndNewBar(
    canUndo: Boolean, canStart: Boolean, undoSpoken: String, modifier: Modifier,
    onUndo: () -> Unit, onStart: () -> Unit, onArm: () -> Unit,
) {
    // "Nova" em dois toques (CV5.DS4.US1): colada ao desfazer, um toque só
    // zerava a partida de quem queria corrigir um ponto com a mão suada.
    var armed by remember { mutableStateOf(false) }
    LaunchedEffect(armed) {
        if (armed) { delay(NEW_MATCH_CONFIRM_MS); armed = false }
    }
    Row(modifier.fillMaxWidth().height(52.dp)) {
        SplitHalf("↶ Desfazer", canUndo, undoSpoken, Alignment.TopEnd, Modifier.weight(1f)) { armed = false; onUndo() }
        Box(Modifier.fillMaxHeight().width(2.dp).background(Color.Black))
        SplitHalf(
            if (armed) "Tocar de novo" else "▶ Nova", canStart,
            if (armed) "Tocar de novo para começar a partida nova" else "Nova partida com os mesmos times e regras. Dois toques.",
            Alignment.TopStart, Modifier.weight(1f), highlight = armed,
        ) {
            if (armed) { armed = false; onStart() } else { armed = true; onArm() }
        }
    }
}

@Composable
private fun SplitHalf(
    label: String, enabled: Boolean, description: String, align: Alignment, modifier: Modifier,
    highlight: Boolean = false, onTap: () -> Unit,
) {
    Box(
        modifier
            .fillMaxHeight()
            .background(if (highlight) Color(0xFF8A5A00) else if (enabled) Color(0xFF3A3A3A) else Color(0xFF1A1A1A))
            .clickable(enabled = enabled, onClick = onTap)
            .semantics { contentDescription = description },
        contentAlignment = align,
    ) {
        Text(
            label,
            Modifier.padding(top = 8.dp, start = 8.dp, end = 8.dp),
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            color = Color.White.copy(alpha = if (enabled) 1f else 0.3f),
        )
    }
}

@Composable
private fun HeldOverlay(reason: String, count: Int, onDiscard: () -> Unit) {
    var confirming by remember { mutableStateOf(false) }
    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.94f)), contentAlignment = Alignment.Center) {
        Column(
            Modifier.fillMaxWidth().padding(horizontal = 30.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(reason, fontSize = 13.sp, textAlign = TextAlign.Center, color = Color.White)
            val lances = if (count == 1) "1 lance retido" else "$count lances retidos"
            if (!confirming) {
                Text("$lances fora do placar.", fontSize = 13.sp, textAlign = TextAlign.Center, color = Color.LightGray)
                Chip(onClick = { confirming = true }, label = { Text("Descartar") },
                    colors = ChipDefaults.secondaryChipColors())
            } else {
                Text("Descartar $lances? Eles não entram no placar.", fontSize = 13.sp,
                    textAlign = TextAlign.Center, color = Color(0xFFFFD27A))
                Chip(onClick = onDiscard, label = { Text("Confirmar descarte") },
                    colors = ChipDefaults.primaryChipColors(backgroundColor = Color(0xFFB3261E)))
                Chip(onClick = { confirming = false }, label = { Text("Voltar") },
                    colors = ChipDefaults.secondaryChipColors())
            }
        }
    }
}

/** A fila gravada não pôde ser lida (CV5.DS2.TS1): lances antigos podem faltar. */
@Composable
private fun LostQueueOverlay(onDismiss: () -> Unit) {
    Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.94f)), contentAlignment = Alignment.Center) {
        Column(
            Modifier.fillMaxWidth().padding(horizontal = 30.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                "Lances antigos ilegíveis no relógio. Confira o placar no telefone.",
                fontSize = 13.sp, textAlign = TextAlign.Center, color = Color(0xFFFFD27A),
            )
            Chip(onClick = onDismiss, label = { Text("Entendi") }, colors = ChipDefaults.secondaryChipColors())
        }
    }
}
