package br.com.placarvolei.watch

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.ChipDefaults
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.Text

private val Cinza = Color(0xFFB0B0B0)
private val Vermelho = Color(0xFFB3261E)

/** Onde fica o vínculo no site: o ícone do relógio no alto da quadra, ao lado da engrenagem. */
const val DICA_APROVAR = "No telefone, toque no ícone do relógio, ao lado da engrenagem, e digite o código."

/**
 * Telas de vínculo (CV3.DS1.US5, ajustadas no teste físico): conteúdo no centro
 * do mostrador redondo e a ação principal na faixa inferior inteira, como o
 * desfazer do placar. Nada de botão solto no alto da lista.
 */
@Composable
fun LinkScreen(model: WatchModel) {
    when (model.stage) {
        Stage.ABERTURA -> Opening(model)
        Stage.CONFIRMAR_TROCA -> ConfirmSwitch(model)
        Stage.CODIGO_NOVO -> CodeWaiting(model.code, backLabel(model.court)) { model.giveUp() }
        Stage.PLACAR -> when {
            model.linked || model.connecting -> Frame(null, reserveBar = true) {
                Ball()
                Caption(model.notice ?: "Carregando placar…")
            }
            model.code.isNotEmpty() ->
                CodeWaiting(model.code, if (model.busy) "Aguarde…" else "Gerar novo código", !model.busy) { model.generateCode() }
            else -> Frame(Bar(if (model.busy) "Aguarde…" else "Ingressar numa quadra", !model.busy) { model.generateCode() }) {
                Ball()
                model.notice?.let { Caption(it) }
            }
        }
    }
}

@Composable
private fun Opening(model: WatchModel) {
    // Enquanto o servidor não responde, só a bola: sem piscar "Retornar" para
    // um vínculo que pode ter caído (ajuste do segundo teste físico).
    if (model.linkCheck == LinkCheck.VERIFICANDO) {
        Frame(null, reserveBar = true) { Ball() }
        return
    }
    // Gerar exige o servidor: o código novo precisa informar o vínculo que substitui.
    val canPair = model.linkCheck == LinkCheck.VALIDO && !model.busy
    Frame(Bar(if (model.busy) "Aguarde…" else "Parear outra quadra", canPair) { model.requestNewCode() }) {
        ReturnButton(model.court) { model.returnToCourt() }
        val status = model.notice ?: if (model.linkCheck == LinkCheck.SEM_REDE) "Sem conexão. Vínculo guardado." else null
        status?.let { Caption(it) }
    }
}

/** Botão grande do centro: "Retornar" e o nome da quadra, centralizados. */
@Composable
private fun ReturnButton(court: String?, onTap: () -> Unit) {
    Box(
        Modifier.fillMaxWidth().height(78.dp).clip(RoundedCornerShape(39.dp))
            .background(MaterialTheme.colors.primary)
            .clickable(onClick = onTap)
            .semantics { contentDescription = "Retornar" + (court?.let { " para $it" } ?: "") },
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Retornar", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            court?.let {
                Text(it, fontSize = 14.sp, color = Color.Black.copy(alpha = 0.75f), maxLines = 1,
                    overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center)
            }
        }
    }
}

@Composable
private fun ConfirmSwitch(model: WatchModel) {
    Frame(Bar("Voltar", true) { model.backToOpening() }) {
        Text(
            abandonWarning(model.pending.size, model.court).orEmpty(),
            fontSize = 13.sp, textAlign = TextAlign.Center, color = Color.White,
        )
        Chip(
            onClick = { model.startReplacement() },
            enabled = !model.busy,
            label = { Text(if (model.busy) "Aguarde…" else "Parear mesmo assim") },
            colors = ChipDefaults.primaryChipColors(backgroundColor = Vermelho),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun CodeWaiting(code: String, action: String, enabled: Boolean = true, onAction: () -> Unit) {
    Frame(Bar(action, enabled, onAction)) {
        Text(
            code.chunked(4).joinToString(" "),
            fontSize = 30.sp, fontWeight = FontWeight.Bold, color = Color.White,
            modifier = Modifier.semantics { contentDescription = "Código ${code.toList().joinToString(" ")}" },
        )
        Caption(DICA_APROVAR)
    }
}

private class Bar(val label: String, val enabled: Boolean, val onTap: () -> Unit)

/** Centro do mostrador para o conteúdo; a faixa inferior, quando houver, para a ação. */
@Composable
private fun Frame(bar: Bar?, reserveBar: Boolean = false, content: @Composable ColumnScope.() -> Unit) {
    Box(Modifier.fillMaxSize().background(Color.Black)) {
        Column(
            Modifier.fillMaxSize().padding(start = 26.dp, end = 26.dp, top = 24.dp, bottom = if (bar != null || reserveBar) 62.dp else 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp, Alignment.CenterVertically),
            content = content,
        )
        // Faixa mais alta que a do desfazer: o texto sobe para onde o círculo é mais largo.
        bar?.let {
            BottomBar(it.label, it.enabled, Modifier.align(Alignment.BottomCenter), height = 58.dp, fontSize = 14.sp, onTap = it.onTap)
        }
    }
}

@Composable
private fun Caption(text: String) {
    Text(text, fontSize = 12.sp, textAlign = TextAlign.Center, color = Cinza)
}

/** Faixa inferior inteira: no mostrador redondo, o texto fica no alto da faixa, onde ela é larga. */
@Composable
fun BottomBar(
    label: String,
    enabled: Boolean,
    modifier: Modifier,
    description: String = label,
    height: Dp = 52.dp,
    fontSize: TextUnit = 15.sp,
    onTap: () -> Unit,
) {
    Box(
        modifier
            .fillMaxWidth()
            .height(height)
            .background(if (enabled) Color(0xFF3A3A3A) else Color(0xFF1A1A1A))
            .clickable(enabled = enabled, onClick = onTap)
            .semantics { contentDescription = description },
        contentAlignment = Alignment.TopCenter,
    ) {
        Text(
            label,
            Modifier.padding(top = 8.dp),
            fontSize = fontSize,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            color = Color.White.copy(alpha = if (enabled) 1f else 0.3f),
        )
    }
}

/** Bola de vôlei quicando: o app está pronto, esperando o primeiro toque. */
@Composable
private fun Ball() {
    val transition = rememberInfiniteTransition(label = "Bola")
    val bounce by transition.animateFloat(
        initialValue = 0f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(700, easing = LinearEasing), RepeatMode.Reverse),
        label = "Quique",
    )
    // Parábola: devagar no alto, rápida perto do chão.
    val height = 1f - (1f - bounce) * (1f - bounce)
    Box(Modifier.size(64.dp, 72.dp), contentAlignment = Alignment.BottomCenter) {
        Canvas(Modifier.size(34.dp, 6.dp)) {
            drawOval(Color.White.copy(alpha = 0.10f + 0.15f * (1f - height)))
        }
        Canvas(
            Modifier.padding(bottom = 6.dp).size(40.dp)
                .graphicsLayer { translationY = -height * 26.dp.toPx(); rotationZ = bounce * 40f }
                .clip(CircleShape)
        ) {
            val r = size.minDimension / 2
            drawCircle(Color.White, r)
            val stroke = Stroke(width = r * 0.12f)
            // Gomos da bola nas cores das equipes do placar.
            drawArc(Color(0xFFFFB020), 200f, 140f, false, Offset(-r * 0.2f, r * 0.1f), Size(r * 1.6f, r * 1.6f), style = stroke)
            drawArc(Color(0xFF4FC3F7), 20f, 140f, false, Offset(r * 0.6f, -r * 0.7f), Size(r * 1.6f, r * 1.6f), style = stroke)
            drawCircle(Color(0xFF333333), r, style = Stroke(width = r * 0.08f))
        }
    }
}
