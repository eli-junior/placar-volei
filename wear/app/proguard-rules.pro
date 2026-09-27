# Placar Vôlei (Wear OS), release com R8 (CV5.DS2.TS4).
# OkHttp traz as próprias regras no AAR; org.json é do Android.
# Health Services usa AIDL/Parcelable: manter as classes do cliente.
-keep class androidx.health.services.client.** { *; }
-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**
