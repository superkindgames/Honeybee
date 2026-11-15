package com.honeybeebaby.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Receives taps on the lock-screen card and saves them in the background. */
public class QuickReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        final String kind = intent.getStringExtra("kind");
        if (kind == null) return;
        final Context app = context.getApplicationContext();
        final PendingResult done = goAsync();
        new Thread(() -> {
            try { HoneyLive.run(app, kind); } finally { done.finish(); }
        }).start();
    }
}
