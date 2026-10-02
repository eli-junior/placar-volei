package br.com.placarvolei;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        // SPIKE CV7.TS3 (descartável): plugin de teste com a tela apagada.
        registerPlugin(SpikePlugin.class);
        super.onCreate(savedInstanceState);
    }
}
