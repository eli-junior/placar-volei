package br.com.placarvolei.watch

import android.animation.ValueAnimator
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer

/** Mesma bola da abertura, escalável; o marcador repete seu giro sem sair do lugar. */
@Composable
internal fun Volleyball(modifier: Modifier, animated: Boolean = false) {
    val angle = if (animated && ValueAnimator.areAnimatorsEnabled()) {
        rememberInfiniteTransition(label = "Bola do último ponto").animateFloat(
            initialValue = 0f, targetValue = 40f,
            animationSpec = infiniteRepeatable(tween(700, easing = LinearEasing), RepeatMode.Reverse),
            label = "Giro da bola",
        )
    } else remember { mutableStateOf(0f) }
    Canvas(modifier.graphicsLayer { rotationZ = angle.value }.clip(CircleShape)) {
        val r = size.minDimension / 2
        drawCircle(Color.White, r)
        val stroke = Stroke(width = r * 0.12f)
        drawArc(Color(0xFFFFB020), 200f, 140f, false,
            Offset(-r * 0.2f, r * 0.1f), Size(r * 1.6f, r * 1.6f), style = stroke)
        drawArc(Color(0xFF4FC3F7), 20f, 140f, false,
            Offset(r * 0.6f, -r * 0.7f), Size(r * 1.6f, r * 1.6f), style = stroke)
        drawCircle(Color(0xFF333333), r, style = Stroke(width = r * 0.08f))
    }
}
