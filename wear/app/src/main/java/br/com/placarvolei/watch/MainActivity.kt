package br.com.placarvolei.watch

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContent
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.KeyboardType
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
                        if (model.code.isEmpty()) {
                            item { Text("Endereço do placar\nToque no campo para digitar", textAlign = TextAlign.Center, fontSize = 12.sp) }
                            item {
                                BasicTextField(value = model.server, onValueChange = { model.server = it },
                                    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)
                                        .border(1.dp, MaterialTheme.colors.primary, RoundedCornerShape(12.dp)).padding(12.dp),
                                    textStyle = TextStyle(color = Color.White, fontSize = 12.sp),
                                    decorationBox = { field ->
                                        Box {
                                            if (model.server.isBlank()) {
                                                Text("https://seu-placar", fontSize = 12.sp, color = Color.LightGray)
                                            }
                                            field()
                                        }
                                    },
                                    enabled = !model.busy,
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri))
                            }
                        }
                        item {
                            Chip(onClick = { model.generateCode() }, enabled = !model.busy && model.server.isNotBlank(),
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
