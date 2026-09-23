package br.com.placarvolei.watch

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContent
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.wear.compose.foundation.lazy.ScalingLazyColumn
import androidx.wear.compose.material.Chip
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
        }
    }
}
