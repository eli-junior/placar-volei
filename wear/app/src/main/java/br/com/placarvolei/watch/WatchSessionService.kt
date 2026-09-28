package br.com.placarvolei.watch

import android.app.NotificationChannel
import android.app.Notification
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.wear.ongoing.OngoingActivity

/** Ongoing Activity para o placar ativo: preserva sessão e oferece retorno e parada explícita. */
class WatchSessionService : Service() {
    override fun onCreate() {
        super.onCreate()
        createChannel()
        val notification = notification()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
        (application as WatchApplication).watchModel().startSession()
        Log.i(TAG, "acompanhamento em primeiro plano iniciado")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            Log.i(TAG, "acompanhamento encerrado pela pessoa")
            (application as WatchApplication).watchModel().stopSession()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelfResult(startId)
            return START_NOT_STICKY
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        Log.i(TAG, "serviço encerrado")
        super.onDestroy()
    }

    private fun notification(): Notification {
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_placar)
            .setContentTitle("Placar em acompanhamento")
            .setContentText("Toque para voltar ao placar")
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setContentIntent(activityIntent())
            .addAction(0, "Encerrar acompanhamento", stopIntent())
        OngoingActivity.Builder(this, NOTIFICATION_ID, builder)
            .setStaticIcon(R.drawable.ic_placar)
            .setTouchIntent(activityIntent())
            .setTitle("Placar Vôlei")
            .setStatus(androidx.wear.ongoing.Status.Builder().addPart(
                "status", androidx.wear.ongoing.Status.TextPart("Partida em andamento")
            ).build())
            .build().apply(this)
        return builder.build()
    }

    private fun activityIntent() = PendingIntent.getActivity(
        this, 0, Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private fun stopIntent() = PendingIntent.getService(
        this, 1, Intent(this, WatchSessionService::class.java).setAction(ACTION_STOP),
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            getSystemService(NotificationManager::class.java).createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "Partida em acompanhamento", NotificationManager.IMPORTANCE_LOW)
            )
        }
    }

    companion object {
        private const val CHANNEL_ID = "watch-session"
        private const val NOTIFICATION_ID = 2401
        private const val ACTION_STOP = "br.com.placarvolei.watch.STOP_SESSION"
        private const val TAG = "WatchSession"

        fun start(context: Context) {
            val intent = Intent(context, WatchSessionService::class.java)
            if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(intent) else context.startService(intent)
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, WatchSessionService::class.java))
        }
    }
}
