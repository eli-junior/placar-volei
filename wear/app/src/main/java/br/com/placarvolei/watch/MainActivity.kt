package br.com.placarvolei.watch

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.platform.LocalContext
import android.content.pm.PackageManager
import android.os.Build
import android.util.Log
import androidx.wear.compose.material.MaterialTheme

class MainActivity : ComponentActivity() {
    private lateinit var model: WatchModel
    private lateinit var celular: CelularSessao

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        model = (application as WatchApplication).watchModel()
        celular = (application as WatchApplication).celular
        model.startSession()
        celular.iniciar()
        setContent {
            val context = LocalContext.current
            val requestNotifications = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {}
            LaunchedEffect(model.linked) {
                if (model.linked && Build.VERSION.SDK_INT >= 33 &&
                    context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                    requestNotifications.launch(android.Manifest.permission.POST_NOTIFICATIONS)
                }
            }
            MaterialTheme {
                // O celular decide o modo (CV7.US2): com a sala local aberta lá, o relógio marca a quadra local.
                when {
                    celular.ativa -> ScoreScreen(celular)
                    model.stage == Stage.PLACAR && model.linked && model.score != null -> ScoreScreen(model)
                    else -> LinkScreen(model)
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        Log.i("WatchSession", "placar retomado em primeiro plano")
        model.startSession()
        celular.iniciar()
    }

    override fun onPause() {
        Log.i("WatchSession", "Activity pausada pelo sistema")
        super.onPause()
    }
}
