package br.com.placarvolei.watch

import android.app.Application
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModelStoreOwner

/** Mantém uma única fila/socket enquanto Activity e serviço compartilham o processo. */
class WatchApplication : Application(), ViewModelStoreOwner {
    override val viewModelStore = ViewModelStore()
    private val provider by lazy {
        ViewModelProvider(this, ViewModelProvider.AndroidViewModelFactory.getInstance(this))
    }

    fun watchModel(): WatchModel = provider[WatchModel::class.java]

    override fun onTerminate() {
        viewModelStore.clear()
        super.onTerminate()
    }
}
