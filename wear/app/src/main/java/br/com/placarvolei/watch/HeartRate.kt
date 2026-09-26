package br.com.placarvolei.watch

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import androidx.core.content.edit
import androidx.health.services.client.HealthServices
import androidx.health.services.client.MeasureCallback
import androidx.health.services.client.data.Availability
import androidx.health.services.client.data.DataPointContainer
import androidx.health.services.client.data.DataType
import androidx.health.services.client.data.DataTypeAvailability
import androidx.health.services.client.data.DeltaDataType
import kotlin.math.roundToInt

/** Rótulo do batimento no topo do placar; leitura fora da faixa do sensor vira "--". */
internal fun heartLabel(bpm: Int?) = if (bpm != null && bpm in 1..250) "♥ $bpm" else "♥ --"

/** Estado do batimento no placar: `granted` falso esconde o rótulo. */
class HeartState(val granted: Boolean, val bpm: Int?)

/**
 * Frequência cardíaca do sensor enquanto o placar está visível (CV3.DS2.US2).
 * `MeasureClient`, não `ExerciseClient`: este encerraria o treino que o
 * Samsung Health está gravando. O valor fica só no relógio.
 */
@Composable
fun rememberHeartRate(): HeartState {
    val context = LocalContext.current
    var granted by remember { mutableStateOf(hasSensorPermission(context)) }
    var bpm by remember { mutableStateOf<Int?>(null) }
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted = it }

    LaunchedEffect(Unit) {
        // Pergunta uma vez só: negar deixa o placar como era, sem insistir.
        val prefs = context.getSharedPreferences("heart-rate", Context.MODE_PRIVATE)
        if (!granted && !prefs.getBoolean("asked", false)) {
            prefs.edit { putBoolean("asked", true) }
            launcher.launch(Manifest.permission.BODY_SENSORS)
        }
    }

    DisposableEffect(granted) {
        if (!granted) return@DisposableEffect onDispose {}
        val client = HealthServices.getClient(context).measureClient
        val callback = object : MeasureCallback {
            override fun onAvailabilityChanged(dataType: DeltaDataType<*, *>, availability: Availability) {
                if (availability is DataTypeAvailability && availability != DataTypeAvailability.AVAILABLE) bpm = null
            }

            override fun onDataReceived(data: DataPointContainer) {
                data.getData(DataType.HEART_RATE_BPM).lastOrNull()?.let { bpm = it.value.roundToInt() }
            }
        }
        runCatching { client.registerMeasureCallback(DataType.HEART_RATE_BPM, callback) }
        onDispose {
            bpm = null
            runCatching { client.unregisterMeasureCallbackAsync(DataType.HEART_RATE_BPM, callback) }
        }
    }
    return HeartState(granted, bpm)
}

private fun hasSensorPermission(context: Context) =
    ContextCompat.checkSelfPermission(context, Manifest.permission.BODY_SENSORS) == PackageManager.PERMISSION_GRANTED
