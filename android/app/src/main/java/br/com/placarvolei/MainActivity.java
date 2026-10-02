package br.com.placarvolei;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        // Ponte com o relógio pelo Data Layer (CV7.TS3).
        registerPlugin(PlacarRelogioPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
