package br.com.placarvolei.watch

import android.view.HapticFeedbackConstants
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontVariation
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.TextUnit
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
@OptIn(androidx.compose.ui.text.ExperimentalTextApi::class)
private val ScoreFont = FontFamily(Font(R.font.teko, weight = FontWeight.Bold,
    variationSettings = FontVariation.Settings(FontVariation.weight(700))))

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
        // Cabeçalho, aviso e ações têm espaço próprio: o placar ocupa só o que sobra.
        // Conteúdo recuado para dentro do aro de conexão (CV6.DS2.US2).
        Column(Modifier.fillMaxSize().padding(RING_INSET)) {
            // Estado da conexão lido junto do cabeçalho: a cor do aro sozinha não informa.
            val status = statusLine(model.connection, pending)
            Row(
                Modifier.align(Alignment.CenterHorizontally).height(22.dp + 16.dp).padding(top = 16.dp)
                    .semantics(mergeDescendants = true) { contentDescription = status },
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                if (heart.granted) HeartText(heart.bpm)
                if (pending > 0) PendingText(pending)
            }
            Spacer(Modifier.height(4.dp))
            if (model.controlled && reason != null) {
                ReasonText(reason, Modifier.fillMaxWidth())
            }
            Row(Modifier.fillMaxWidth().weight(1f)) {
                TeamHalf(rotuloA, pontosA, CorNos, reason == null, pending > 0, Modifier.weight(1f)) { tap("A") }
                Box(Modifier.fillMaxHeight().width(2.dp).background(Color(0xFF333333)))
                TeamHalf(rotuloB, pontosB, CorEles, reason == null, pending > 0, Modifier.weight(1f)) { tap("B") }
            }
            if (model.controlled) {
                if (model.showNewMatch) {
                    UndoAndNewBar(
                        model.canUndo, model.canStartNewMatch, model.undoSpoken, Modifier.fillMaxWidth(),
                        ::undo, ::newMatch, onArm = { view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK) },
                    )
                } else {
                    UndoBar(model.canUndo, UNDO_LABEL, model.undoSpoken, Modifier.fillMaxWidth(), ::undo)
                }
            } else if (reason != null) {
                // Mede também a quebra de linha com fonte ampliada antes de distribuir o placar.
                ReasonText(reason, Modifier.fillMaxWidth().padding(top = 8.dp, bottom = 22.dp))
            } else {
                Spacer(Modifier.height(52.dp))
            }
        }
        ConnectionRing(signal(model.connection, pending))
        if (model.lostQueue) LostQueueOverlay(model::dismissLostQueue)
        model.discardNotice?.let { DiscardNotice(it, model::dismissDiscardNotice) }
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

/** Estado da conexão para leitores de tela: a cor sozinha não informa. */
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
        Column(Modifier.fillMaxSize().padding(horizontal = 6.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            FittedText(label, 22.sp, color, Modifier.fillMaxWidth().height(28.dp))
            AnimatedContent(
                targetState = points,
                modifier = Modifier.fillMaxWidth().weight(1f),
                // Ponto sobe; ponto desfeito desce, para ser visivelmente desfeito.
                transitionSpec = {
                    val up = if (targetState >= initialState) 1 else -1
                    (slideInVertically { up * it / 3 } + fadeIn()) togetherWith (slideOutVertically { -up * it / 3 } + fadeOut())
                },
                label = "Pontos $label",
            ) { value ->
                // Número previsto (ainda não confirmado) fica mais apagado e sublinhado por um traço.
                FittedText(
                    value.toString(), 96.sp,
                    if (predicted) Color.White.copy(alpha = 0.7f) else Color.White,
                    Modifier.fillMaxSize(), ScoreFont,
                )
            }
            Spacer(
                Modifier.width(28.dp).height(3.dp)
                    .background(if (predicted) color.copy(alpha = 0.8f) else Color.Transparent)
            )
        }
    }
}

/** Mede o texto antes de desenhar: três dígitos e fonte ampliada cabem na área reservada. */
@Composable
private fun FittedText(
    text: String, preferredSize: TextUnit, color: Color, modifier: Modifier,
    family: FontFamily = FontFamily.Default,
) {
    val measurer = rememberTextMeasurer()
    val density = LocalDensity.current
    BoxWithConstraints(modifier, contentAlignment = Alignment.Center) {
        val bounds = with(density) { Constraints(maxWidth = maxWidth.roundToPx(), maxHeight = maxHeight.roundToPx()) }
        val style = remember(text, preferredSize, family, bounds, density) {
            var low = 1f
            var high = preferredSize.value
            repeat(10) {
                val size = (low + high) / 2
                val candidate = TextStyle(fontFamily = family, fontWeight = FontWeight.Bold,
                    fontSize = size.sp, lineHeight = size.sp, textAlign = TextAlign.Center)
                val measured = measurer.measure(text, candidate, maxLines = 1, softWrap = false, constraints = bounds)
                if (measured.hasVisualOverflow) high = size else low = size
            }
            TextStyle(fontFamily = family, fontWeight = FontWeight.Bold,
                fontSize = low.sp, lineHeight = low.sp, textAlign = TextAlign.Center)
        }
        Text(text, style = style, color = color, maxLines = 1, softWrap = false)
    }
}

/** Traço do aro e folga até a borda; o conteúdo fica recuado dessa medida. */
private val RING_STROKE = 2.dp
private val RING_INSET = 4.dp

internal fun signalColor(signal: Signal) = when (signal) {
    Signal.CONECTADO -> Color(0xFF4CD964)
    Signal.PROCESSANDO -> Color(0xFFFFC83D)
    Signal.DESCONECTADO -> Color(0xFFFF4D4D)
}

/**
 * Aro fino na borda da tela com a cor da conexão (CV6.DS2.US2). Só desenha:
 * não recebe toque nem foco, então não bloqueia pontuar, Voltar Ponto ou Nova.
 * O estado para leitor de tela está no cabeçalho.
 */
@Composable
private fun ConnectionRing(signal: Signal) {
    val color by animateColorAsState(signalColor(signal), tween(150), label = "Aro de conexão")
    val round = LocalConfiguration.current.isScreenRound
    Canvas(Modifier.fillMaxSize()) {
        val stroke = RING_STROKE.toPx()
        val half = stroke / 2 + 1.dp.toPx()
        if (round) {
            drawCircle(color, radius = size.minDimension / 2 - half, style = Stroke(stroke))
        } else {
            drawRect(color, Offset(half, half), Size(size.width - 2 * half, size.height - 2 * half), style = Stroke(stroke))
        }
    }
}

/** Lances ainda não confirmados; a quantidade exata vai para o leitor de tela pelo cabeçalho. */
@Composable
private fun PendingText(pending: Int) {
    Text(
        "↑${if (pending > 9) "9+" else pending.toString()}",
        Modifier.clearAndSetSemantics {},
        fontSize = 15.sp,
        fontWeight = FontWeight.Bold,
        maxLines = 1,
        color = signalColor(Signal.PROCESSANDO),
    )
}

/** Batimento centralizado no cabeçalho; fica só no relógio. */
@Composable
private fun HeartText(bpm: Int?) {
    val label = heartLabel(bpm)
    val description = if (label == "♥ --") "Batimento sem leitura" else "Batimento $bpm por minuto"
    Text(
        label,
        Modifier.semantics { contentDescription = description },
        fontSize = 17.sp,
        fontWeight = FontWeight.Bold,
        maxLines = 1,
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
        SplitHalf(UNDO_LABEL, canUndo, undoSpoken, Alignment.TopEnd, Modifier.weight(1f)) { armed = false; onUndo() }
        Box(Modifier.fillMaxHeight().width(2.dp).background(Color.Black))
        SplitHalf(
            if (armed) "Tocar de novo" else "▶ Nova", canStart,
            if (armed) "Tocar de novo para começar a partida nova" else "Nova partida com os mesmos times e regras. Dois toques.",
            Alignment.TopStart, Modifier.weight(1f), highlight = armed, actionColor = Color(0xFF166534),
        ) {
            if (armed) { armed = false; onStart() } else { armed = true; onArm() }
        }
    }
}

@Composable
private fun SplitHalf(
    label: String, enabled: Boolean, description: String, align: Alignment, modifier: Modifier,
    highlight: Boolean = false, actionColor: Color = Color(0xFF3A3A3A), onTap: () -> Unit,
) {
    Box(
        modifier
            .fillMaxHeight()
            .background(if (highlight) Color(0xFF8A5A00) else if (enabled) actionColor else Color(0xFF1A1A1A))
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

/** Aviso do descarte por conflito (CV3.DS1.US4): some sozinho em 3 s ou ao toque. */
internal const val NOTICE_MS = 3_000L

@Composable
private fun DiscardNotice(text: String, onDismiss: () -> Unit) {
    LaunchedEffect(text) {
        delay(NOTICE_MS)
        onDismiss()
    }
    Box(
        Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.94f)).clickable(onClick = onDismiss)
            .semantics { liveRegion = LiveRegionMode.Polite },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text, Modifier.padding(horizontal = 30.dp),
            fontSize = 15.sp, textAlign = TextAlign.Center, color = Color(0xFFFFD27A),
        )
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
