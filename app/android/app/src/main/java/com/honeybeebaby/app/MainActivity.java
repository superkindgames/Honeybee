package com.honeybeebaby.app;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(HoneyNativePlugin.class);   // the lock-screen card
        super.onCreate(savedInstanceState);
    }
}
