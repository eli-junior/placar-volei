plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "br.com.placarvolei.watch"
    compileSdk = 35
    defaultConfig {
        applicationId = "br.com.placarvolei.watch"
        minSdk = 30
        targetSdk = 35
        versionCode = 2
        versionName = "0.8.0"
        val serverUrl = providers.gradleProperty("serverUrl").getOrElse("https://placar.elijunior.click")
        require(!serverUrl.contains('"') && !serverUrl.contains('\\') && !serverUrl.contains('\n'))
        buildConfigField("String", "SERVER_URL", "\"$serverUrl\"")
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.wear.compose:compose-material:1.4.1")
    implementation("androidx.wear.compose:compose-foundation:1.4.1")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    testImplementation("junit:junit:4.13.2")
    // org.json do Android é stub nos testes locais da JVM.
    testImplementation("org.json:json:20240303")
}
