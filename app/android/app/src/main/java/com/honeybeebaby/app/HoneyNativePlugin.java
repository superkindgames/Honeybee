package com.honeybeebaby.app;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;

import androidx.core.app.ActivityCompat;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import org.json.JSONObject;

/** The app's bridge to the Android lock-screen card (same calls as on iPhone). */
@CapacitorPlugin(name = "HoneyNative")
public class HoneyNativePlugin extends Plugin {
    private static boolean asked = false;

    /** items: [{kind:"hub", hub:{…}, quick:{…}}] — shows or updates the card, or removes it when there's nothing to show */
    @PluginMethod
    public void liveSync(PluginCall call) {
        Context ctx = getContext();
        JSObject res = new JSObject();
        try {
            JSArray items = call.getArray("items");
            JSONObject hub = null, quick = null;
            if (items != null) for (int i = 0; i < items.length(); i++) {
                JSONObject it = items.optJSONObject(i);
                if (it != null && "hub".equals(it.optString("kind"))) { hub = it.optJSONObject("hub"); quick = it.optJSONObject("quick"); }
            }
            if (!HoneyLive.canNotify(ctx) && Build.VERSION.SDK_INT >= 33 && !asked && getActivity() != null) {
                asked = true;   // Android 13+: ask once for permission to show the card
                ActivityCompat.requestPermissions(getActivity(), new String[]{Manifest.permission.POST_NOTIFICATIONS}, 7311);
            }
            if (hub != null && quick != null) {
                JSONObject c = new JSONObject(quick.toString());
                c.put("hub", hub);
                HoneyLive.save(ctx, c);
                HoneyLive.show(ctx, hub);
                res.put("running", 1);
            } else {
                HoneyLive.cancel(ctx);
                res.put("running", 0);
            }
            res.put("enabled", HoneyLive.canNotify(ctx) || !asked);
        } catch (Exception e) {
            res.put("error", String.valueOf(e.getMessage()));
        }
        call.resolve(res);
    }

    @PluginMethod
    public void takeAction(PluginCall call) {
        JSObject r = new JSObject();
        r.put("action", "");
        call.resolve(r);
    }

    /** opens Goldfox's notification settings (where the lock-screen card is switched on) */
    @PluginMethod
    public void openSettings(PluginCall call) {
        try {
            Intent i;
            if (Build.VERSION.SDK_INT >= 26) {
                i = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, getContext().getPackageName());
            } else {
                i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getContext().getPackageName()));
            }
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(i);
        } catch (Exception e) { /* nothing to open */ }
        call.resolve();
    }
}
