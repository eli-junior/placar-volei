package br.com.placarvolei.watch

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContent
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.wear.compose.foundation.lazy.ScalingLazyColumn
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.ChipDefaults
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.Text

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val model: WatchModel = viewModel()
            val lifecycle = LocalLifecycleOwner.current.lifecycle
            LaunchedEffect(lifecycle) {
                lifecycle.repeatOnLifecycle(Lifecycle.State.RESUMED) { model.observeWhileVisible() }
            }
            MaterialTheme {
                when (model.stage) {
                    Stage.ABERTURA, Stage.CONFIRMAR_TROCA, Stage.CODIGO_NOVO -> ChoiceScreen(model)
                    Stage.PLACAR -> LinkOrScore(model)
                }
            }
        }
    }
}

@Composable
private fun LinkOrScore(model: WatchModel) {
    if (model.linked && model.score != null) {
        ScoreScreen(model)
    } else ScalingLazyColumn(modifier = Modifier.padding(horizontal = 12.dp)) {
        item { Text("Placar Vôlei", textAlign = TextAlign.Center) }
        item { AnimatedContent(targetState = model.message, label = "Estado do vínculo") { message ->
            Text(message, textAlign = TextAlign.Center, fontSize = 14.sp)
        } }
        if (model.code.isNotEmpty()) {
            item { Text(model.code.chunked(4).joinToString(" "), fontSize = 24.sp) }
        }
        if (!model.linked) {
            item {
                Chip(onClick = { model.generateCode() }, enabled = !model.busy,
                    label = { Text(if (model.busy) "Aguarde…" else "Gerar código") })
            }
        } else {
            item { Text("Carregando placar…", fontSize = 12.sp, textAlign = TextAlign.Center) }
        }
    }
}

/**
 * Um vínculo por vez (CV3.DS1.US5): retornar à quadra ou gerar um código novo,
 * o aviso dos lances que seriam abandonados e o código à espera de aprovação.
 */
@Composable
private fun ChoiceScreen(model: WatchModel) {
    val back = returnLabel(model.court)
    ScalingLazyColumn(modifier = Modifier.padding(horizontal = 12.dp)) {
        item { Text("Placar Vôlei", textAlign = TextAlign.Center) }
        when (model.stage) {
            Stage.CONFIRMAR_TROCA -> {
                item {
                    Text(abandonWarning(model.pending.size, model.court).orEmpty(),
                        textAlign = TextAlign.Center, fontSize = 14.sp)
                }
                item {
                    Chip(onClick = { model.startReplacement() }, enabled = !model.busy,
                        label = { Text(if (model.busy) "Aguarde…" else "Gerar mesmo assim") },
                        colors = ChipDefaults.primaryChipColors(backgroundColor = Color(0xFFB3261E)))
                }
                item {
                    Chip(onClick = { model.backToOpening() }, label = { Text("Voltar") },
                        colors = ChipDefaults.secondaryChipColors())
                }
            }
            Stage.CODIGO_NOVO -> {
                item { Text(model.message, textAlign = TextAlign.Center, fontSize = 14.sp) }
                item { Text(model.code.chunked(4).joinToString(" "), fontSize = 24.sp) }
                item {
                    Chip(onClick = { model.giveUp() }, label = { Text(returnLabel(model.court, "Voltar")) },
                        colors = ChipDefaults.secondaryChipColors())
                }
            }
            else -> {
                val status = model.notice ?: when (model.linkCheck) {
                    LinkCheck.VERIFICANDO -> "Verificando vínculo…"
                    LinkCheck.VALIDO -> "Vinculado."
                    LinkCheck.SEM_REDE -> "Sem conexão. Vínculo guardado."
                }
                item {
                    AnimatedContent(targetState = status, label = "Estado do vínculo") { text ->
                        Text(text, textAlign = TextAlign.Center, fontSize = 14.sp)
                    }
                }
                item { Chip(onClick = { model.returnToCourt() }, label = { Text(back) }) }
                item {
                    // Gerar exige o servidor: o código novo precisa informar o vínculo que substitui.
                    Chip(onClick = { model.requestNewCode() },
                        enabled = model.linkCheck == LinkCheck.VALIDO && !model.busy,
                        label = { Text(if (model.busy) "Aguarde…" else "Gerar novo código") },
                        colors = ChipDefaults.secondaryChipColors())
                }
            }
        }
    }
}
