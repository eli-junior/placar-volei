package br.com.placarvolei.watch

import android.app.Application
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModelStoreOwner
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import java.io.File

/** Mantém uma única fila/socket enquanto Activity e serviço compartilham o processo. */
class WatchApplication : Application(), ViewModelStoreOwner {
    override val viewModelStore = ViewModelStore()
    private val provider by lazy {
        ViewModelProvider(this, ViewModelProvider.AndroidViewModelFactory.getInstance(this))
    }

    fun watchModel(): WatchModel = provider[WatchModel::class.java]

    /** O relógio na quadra local do celular (CV7.US2): fila própria, separada da do servidor. */
    val celular: CelularSessao by lazy {
        CelularSessao(
            CommandQueue(File(filesDir, "fila-celular.json")),
            CelularLink(this),
            CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate),
        )
    }

    override fun onTerminate() {
        viewModelStore.clear()
        super.onTerminate()
    }
}
