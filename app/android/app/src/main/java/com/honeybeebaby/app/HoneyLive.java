package com.honeybeebaby.app;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.SystemClock;
import android.view.View;
import android.widget.RemoteViews;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.security.SecureRandom;
import java.text.DateFormat;
import java.util.Date;
import java.util.Iterator;

/**
 * Goldfox's lock-screen card on Android: a pinned notification that looks like the iPhone card
 * (Feed · Diaper · Pump · Sleep tiles, the sleeping bar, breastfeeding Left / Right / Done) and
 * saves taps straight to the family log, without opening the app.
 */
public class HoneyLive {
    static final String PREFS = "hb", KEY = "quick", CHANNEL = "live";
    static final int NID = 4711;
    static String lastErr = "";
    static String idTok = ""; static long idExp = 0;

    /** a short-lived pass for this phone (made from the sign-in the app saved), so lock-screen saves count as this phone */
    static String idToken(JSONObject c) {
        if (!idTok.isEmpty() && idExp > System.currentTimeMillis() + 120000) return idTok;
        String r = c.optString("refresh", ""), k = c.optString("apiKey", "");
        if (r.isEmpty() || k.isEmpty()) return null;
        HttpURLConnection con = null;
        try {
            con = (HttpURLConnection) new URL("https://securetoken.googleapis.com/v1/token?key=" + URLEncoder.encode(k, "UTF-8")).openConnection();
            con.setRequestMethod("POST"); con.setDoOutput(true); con.setConnectTimeout(10000); con.setReadTimeout(10000);
            con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            try (OutputStream os = con.getOutputStream()) { os.write(("grant_type=refresh_token&refresh_token=" + URLEncoder.encode(r, "UTF-8")).getBytes("UTF-8")); }
            if (con.getResponseCode() >= 300) return null;
            java.io.InputStream in = con.getInputStream(); java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[4096]; int n; while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
            JSONObject o = new JSONObject(bo.toString("UTF-8"));
            idTok = o.optString("id_token", ""); idExp = System.currentTimeMillis() + Long.parseLong(o.optString("expires_in", "3600")) * 1000L;
            return idTok.isEmpty() ? null : idTok;
        } catch (Exception e) { return null; }
        finally { if (con != null) con.disconnect(); }
    }

    // ---------- saved settings (family, name, what one tap logs, and the card's current state) ----------
    static synchronized JSONObject config(Context c) {
        try { return new JSONObject(c.getSharedPreferences(PREFS, 0).getString(KEY, "{}")); } catch (Exception e) { return new JSONObject(); }
    }
    static synchronized void save(Context c, JSONObject o) {
        c.getSharedPreferences(PREFS, 0).edit().putString(KEY, o.toString()).apply();
    }
    static void cancel(Context c) { NotificationManagerCompat.from(c).cancel(NID); }

    static boolean canNotify(Context c) {
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(c, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return false;
        return NotificationManagerCompat.from(c).areNotificationsEnabled();
    }

    // ---------- helpers ----------
    static long num(JSONObject h, String k) { return h.has(k) && !h.isNull(k) ? h.optLong(k, 0) : 0; }
    static String str(JSONObject h, String k) { return h.has(k) && !h.isNull(k) ? h.optString(k, null) : null; }
    static long base(long sinceMs) { return SystemClock.elapsedRealtime() - (System.currentTimeMillis() - sinceMs); }
    static String clock(long ms) { return DateFormat.getTimeInstance(DateFormat.SHORT).format(new Date(ms)); }
    static String mmss(long ms) {
        long s = Math.max(0, ms / 1000), h = s / 3600, m = (s % 3600) / 60, ss = s % 60;
        return h > 0 ? String.format("%d:%02d:%02d", h, m, ss) : String.format("%d:%02d", m, ss);
    }
    static int id(Context c, String name) { return c.getResources().getIdentifier(name, "id", c.getPackageName()); }
    static int dr(Context c, String name) { return c.getResources().getIdentifier(name, "drawable", c.getPackageName()); }

    static PendingIntent tap(Context c, String kind) {
        Intent i = new Intent(c, QuickReceiver.class).setAction("hb.quick." + kind).putExtra("kind", kind);
        return PendingIntent.getBroadcast(c, kind.hashCode(), i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
    static PendingIntent openApp(Context c) {
        Intent i = new Intent(c, MainActivity.class).setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(c, 1, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    // ---------- the card ----------
    static void show(Context c, JSONObject h) {
        if (!canNotify(c)) return;
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm.getNotificationChannel(CHANNEL) == null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Lock-screen card", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Feed, Diaper, Pump and Sleep buttons and timers on your lock screen");
            ch.setSound(null, null); ch.enableVibration(false); ch.setShowBadge(false);
            ch.setLockscreenVisibility(NotificationCompat.VISIBILITY_PUBLIC);
            nm.createNotificationChannel(ch);
        }
        NotificationCompat.Builder b = new NotificationCompat.Builder(c, CHANNEL)
                .setSmallIcon(R.drawable.ic_stat_paw)
                .setColor(0xFFF5A524)
                .setContentTitle("Goldfox")
                .setOngoing(true).setOnlyAlertOnce(true).setSilent(true).setShowWhen(false)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setCategory(NotificationCompat.CATEGORY_STATUS)
                .setContentIntent(openApp(c))
                .setStyle(new NotificationCompat.DecoratedCustomViewStyle())
                .setCustomContentView(small(c, h))
                .setCustomBigContentView(big(c, h));
        try { NotificationManagerCompat.from(c).notify(NID, b.build()); } catch (SecurityException e) { /* notifications switched off */ }
    }

    static RemoteViews big(Context c, JSONObject h) {
        if (str(h, "bfSide") != null) return bf(c, h);
        String pick = str(h, "pick");
        if ("feed".equals(pick)) return pickFeed(c, h);
        if ("diaper".equals(pick)) return pickDiaper(c, h);
        if ("pump".equals(pick)) return pickPump(c, h);
        return grid(c, h);
    }

    static String act(JSONObject h, String k) { return h.optBoolean("oneTap", false) ? k : "pick:" + k; }
    static String note(JSONObject h, String k) { return k.equals(str(h, "flashKind")) ? str(h, "flash") : null; }

    /** one tile: name, a counting-up time since it last happened, the "just logged" note and gold glow */
    static void tile(Context c, RemoteViews v, JSONObject h, String cat, String key, String atKey, String kind, String fallbackNote) {
        long at = num(h, atKey);
        String n = note(h, key);
        boolean done = n != null && n.startsWith("✓");
        if (at > 0) {
            v.setViewVisibility(id(c, "c_" + cat), View.VISIBLE); v.setViewVisibility(id(c, "d_" + cat), View.GONE);
            v.setChronometer(id(c, "c_" + cat), base(at), null, true);
        } else {
            v.setViewVisibility(id(c, "c_" + cat), View.GONE); v.setViewVisibility(id(c, "d_" + cat), View.VISIBLE);
        }
        String shown = n != null ? n : fallbackNote;
        if (shown != null) { v.setTextViewText(id(c, "x_" + cat), shown); v.setViewVisibility(id(c, "x_" + cat), View.VISIBLE); }
        v.setInt(id(c, "t_" + cat), "setBackgroundResource", dr(c, "tile_" + cat + (done ? "_gold" : "")));
        v.setOnClickPendingIntent(id(c, "t_" + cat), tap(c, kind));
    }

    static RemoteViews grid(Context c, JSONObject h) {
        long sleepAt = num(h, "sleepAt");
        if (sleepAt > 0) {
            RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_sleep);
            tile(c, v, h, "feed", "feed", "feedAt", act(h, "feed"), null);
            tile(c, v, h, "diaper", "diaper", "diaperAt", act(h, "diaper"), null);
            tile(c, v, h, "pump", "pump", "pumpAt", act(h, "pump"), null);
            v.setChronometer(R.id.c_sleep, base(sleepAt), null, true);
            String n = note(h, "sleep");
            if (n != null) { v.setTextViewText(R.id.x_sleep, n); v.setViewVisibility(R.id.x_sleep, View.VISIBLE); }
            v.setOnClickPendingIntent(R.id.wake, tap(c, "sleep"));
            return v;
        }
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_grid);
        tile(c, v, h, "feed", "feed", "feedAt", act(h, "feed"), null);
        tile(c, v, h, "diaper", "diaper", "diaperAt", act(h, "diaper"), null);
        tile(c, v, h, "pump", "pump", "pumpAt", act(h, "pump"), null);
        tile(c, v, h, "nap", "sleep", "wakeAt", "sleep", "Tap: start sleep");
        long nf = num(h, "napFrom"), nt = num(h, "napTo");
        if (nf > 0 && nt > 0) {   // thin gold bar above the buttons: the next nap (the app's estimate)
            boolean now = h.optBoolean("napNow", false);
            boolean late = h.optBoolean("napLate", false);
            v.setTextViewText(R.id.napline, late ? "✨ NAP TIME NOW" : now ? "😴 Getting tired now · nap by " + clock(nt) : "🌙 Next nap ~" + clock(nf) + " – " + clock(nt));
            v.setTextViewTextSize(R.id.napline, android.util.TypedValue.COMPLEX_UNIT_SP, late ? 17 : 14);
            v.setInt(R.id.napline, "setBackgroundResource", now ? R.drawable.napbar_now : R.drawable.napbar);
            v.setViewVisibility(R.id.napline, View.VISIBLE);
        }
        String n = note(h, "sleep");
        if (n != null && n.startsWith("✓")) {   // just woke up: Goldie's awake face in a gold ring
            v.setImageViewResource(R.id.i_nap, R.drawable.goldie_awake_gold);
            v.setInt(R.id.i_nap, "setBackgroundResource", 0);
            v.setViewPadding(R.id.i_nap, 0, 0, 0, 0);
        }
        return v;
    }

    static RemoteViews bf(Context c, JSONObject h) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_bf);
        String side = str(h, "bfSide");
        long seg = num(h, "bfSeg"), l = num(h, "bfL"), r = num(h, "bfR");
        if (seg <= 0) seg = System.currentTimeMillis();
        v.setChronometer(R.id.c_total, base(seg - l - r), null, true);
        for (String s : new String[]{"L", "R"}) {
            boolean on = s.equals(side);
            long done = s.equals("L") ? l : r;
            int chrono = id(c, "sc_" + s), text = id(c, "st_" + s);
            if (on) {
                v.setViewVisibility(chrono, View.VISIBLE); v.setViewVisibility(text, View.GONE);
                v.setChronometer(chrono, base(seg - done), null, true);
            } else {
                v.setViewVisibility(chrono, View.GONE); v.setViewVisibility(text, View.VISIBLE);
                v.setTextViewText(text, mmss(done));
            }
            int ink = 0xFF1A2133, white = 0xFFFFFFFF;
            v.setTextColor(chrono, on ? ink : white); v.setTextColor(text, on ? ink : white);
            v.setTextColor(id(c, "sl_" + s), on ? ink : 0xD9FFFFFF);
            v.setTextColor(id(c, "sh_" + s), on ? 0xCC1A2133 : 0xBFFFFFFF);
            v.setTextViewText(id(c, "sh_" + s), on ? "feeding now" : "tap to switch");
            v.setInt(id(c, "side_" + s), "setBackgroundResource", on ? R.drawable.side_on : R.drawable.side_off);
            v.setOnClickPendingIntent(id(c, "side_" + s), tap(c, "bf:" + s));
        }
        v.setOnClickPendingIntent(R.id.done, tap(c, "bf:done"));
        return v;
    }

    static JSONArray arr(JSONObject h, String k) { JSONArray a = h.optJSONArray(k); return a == null ? new JSONArray() : a; }

    /** Feed card: Formula | Breastmilk tabs on top (remembers the last type), one row of amounts; nothing is
     *  highlighted until you tap, then that button turns green with ✓ while it saves */
    static RemoteViews pickFeed(Context c, JSONObject h) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_pick_feed);
        JSONArray ml = arr(h, "feedMl"), lb = arr(h, "feedLbls");
        String last = str(h, "lastFeed"), ft = str(h, "feedType"), chosen = str(h, "chosen");
        if (ft == null) ft = last != null && last.contains(":") ? last.substring(0, last.indexOf(':')) : "formula";
        String[][] tabs = {{"tab_fo", "formula"}, {"tab_bm", "breastmilk"}};
        for (String[] t : tabs) {
            int tid = id(c, t[0]);
            boolean on = t[1].equals(ft);
            v.setInt(tid, "setBackgroundResource", on ? R.drawable.tab_on : R.drawable.tab_off);
            v.setTextColor(tid, on ? 0xFF1A2133 : 0xBFFFFFFF);
            v.setOnClickPendingIntent(tid, tap(c, "ftype:" + t[1]));
        }
        for (int i = 0; i < 3; i++) {
            int vid = id(c, "fa" + i);
            if (i >= ml.length()) { v.setViewVisibility(vid, View.INVISIBLE); continue; }
            int m = ml.optInt(i);
            String a = "feed:" + ft + ":" + m, label = i < lb.length() ? lb.optString(i) : m + " ml";
            choice(c, v, vid, a, label, chosen, R.drawable.tile_feed);
        }
        v.setOnClickPendingIntent(R.id.close, tap(c, "pick:none"));
        return v;
    }

    /** one choice button: plain until tapped; the one just tapped is green with ✓ */
    static void choice(Context c, RemoteViews v, int vid, String action, String label, String chosen, int bg) {
        boolean done = action.equals(chosen);
        v.setTextViewText(vid, done ? "✓ " + label : label);
        v.setInt(vid, "setBackgroundResource", done ? R.drawable.tile_done : bg);
        v.setTextColor(vid, done ? 0xFF1A2133 : 0xFFFFFFFF);
        v.setOnClickPendingIntent(vid, tap(c, action));
    }

    static RemoteViews pickDiaper(Context c, JSONObject h) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_pick_diaper);
        String[][] o = {{"wet", "Pee"}, {"dirty", "Poop"}, {"both", "Both\nPee + Poop"}};
        String chosen = str(h, "chosen");
        for (int i = 0; i < 3; i++) choice(c, v, id(c, "dc" + i), "diaper:" + o[i][0], o[i][1], chosen, R.drawable.tile_diaper);
        v.setOnClickPendingIntent(R.id.close, tap(c, "pick:none"));
        return v;
    }

    static RemoteViews pickPump(Context c, JSONObject h) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_pick_pump);
        JSONArray ml = arr(h, "pumpMl"), lb = arr(h, "pumpLbls");
        String side = str(h, "pumpSide"), chosen = str(h, "chosen");
        for (int i = 0; i < 4; i++) {
            int vid = id(c, "pc" + i);
            if (i >= ml.length()) { v.setViewVisibility(vid, View.INVISIBLE); continue; }
            int m = ml.optInt(i);
            choice(c, v, vid, "pump:" + m, (i < lb.length() ? lb.optString(i) : m + " ml") + (side != null ? "\n" + side : ""), chosen, R.drawable.tile_pump);
        }
        v.setOnClickPendingIntent(R.id.close, tap(c, "pick:none"));
        return v;
    }

    /** the one-line card (when the notification is folded) */
    static RemoteViews small(Context c, JSONObject h) {
        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_small);
        String side = str(h, "bfSide");
        long sleepAt = num(h, "sleepAt");
        if (side != null) {
            long seg = num(h, "bfSeg"), done = "L".equals(side) ? num(h, "bfL") : num(h, "bfR");
            v.setTextViewText(R.id.sm_t, "BREASTFEEDING · " + ("L".equals(side) ? "LEFT" : "RIGHT"));
            v.setChronometer(R.id.sm_c, base(seg - done), null, true);
            v.setTextViewText(R.id.sm_btn, "Done"); v.setViewVisibility(R.id.sm_btn, View.VISIBLE);
            v.setInt(R.id.sm_btn, "setBackgroundResource", R.drawable.pill_rose);
            v.setOnClickPendingIntent(R.id.sm_btn, tap(c, "bf:done"));
        } else if (sleepAt > 0) {
            v.setImageViewResource(R.id.sm_img, R.drawable.goldie_sleepy_round);
            v.setTextViewText(R.id.sm_t, "SLEEPING NOW");
            v.setChronometer(R.id.sm_c, base(sleepAt), null, true);
            v.setTextViewText(R.id.sm_btn, "Woke up"); v.setViewVisibility(R.id.sm_btn, View.VISIBLE);
            v.setTextColor(R.id.sm_btn, 0xFF5B3FD9);
            v.setOnClickPendingIntent(R.id.sm_btn, tap(c, "sleep"));
        } else {
            long feedAt = num(h, "feedAt");
            v.setTextViewText(R.id.sm_t, feedAt > 0 ? "SINCE LAST FEED · tap and hold for more" : "GOLDFOX");
            if (feedAt > 0) v.setChronometer(R.id.sm_c, base(feedAt), null, true);
            else v.setViewVisibility(R.id.sm_c, View.GONE);
        }
        return v;
    }

    // ---------- saving to the family log (Firestore REST, the same way the iPhone lock screen does) ----------
    static JSONObject value(Object v) throws Exception {
        JSONObject o = new JSONObject();
        if (v instanceof String) o.put("stringValue", v);
        else if (v instanceof Boolean) o.put("booleanValue", v);
        else if (v instanceof Integer || v instanceof Long) o.put("integerValue", String.valueOf(((Number) v).longValue()));
        else if (v instanceof Number) {
            double d = ((Number) v).doubleValue();
            if (d == Math.rint(d)) o.put("integerValue", String.valueOf((long) d)); else o.put("doubleValue", d);
        } else o.put("nullValue", JSONObject.NULL);
        return o;
    }

    static String newId() {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        SecureRandom r = new SecureRandom(); StringBuilder b = new StringBuilder();
        for (int i = 0; i < 20; i++) b.append(chars.charAt(r.nextInt(chars.length())));
        return b.toString();
    }

    static boolean write(JSONObject c, String docId, JSONObject fields, String[] mask) {
        HttpURLConnection con = null;
        try {
            String p = c.optString("project", ""), fam = c.optString("family", "");
            if (fam.isEmpty() || p.isEmpty()) { lastErr = "no family"; return false; }
            StringBuilder u = new StringBuilder("https://firestore.googleapis.com/v1/projects/" + p + "/databases/(default)/documents/families/" + URLEncoder.encode(fam, "UTF-8") + "/events/" + docId + "?");
            if (c.has("apiKey")) u.append("key=").append(URLEncoder.encode(c.optString("apiKey"), "UTF-8")).append("&");
            if (mask != null) { for (String m : mask) u.append("updateMask.fieldPaths=").append(m).append("&"); u.append("currentDocument.exists=true"); }
            JSONObject f = new JSONObject();
            for (Iterator<String> it = fields.keys(); it.hasNext(); ) { String k = it.next(); f.put(k, value(fields.isNull(k) ? null : fields.get(k))); }
            byte[] body = new JSONObject().put("fields", f).toString().getBytes("UTF-8");
            con = (HttpURLConnection) new URL(u.toString()).openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("X-HTTP-Method-Override", "PATCH");   // Android's URL connection has no PATCH; Google APIs accept this
            con.setRequestProperty("Content-Type", "application/json");
            String tok = idToken(c);
            if (tok != null) con.setRequestProperty("Authorization", "Bearer " + tok);
            con.setConnectTimeout(10000); con.setReadTimeout(10000); con.setDoOutput(true);
            try (OutputStream os = con.getOutputStream()) { os.write(body); }
            int code = con.getResponseCode();
            if (code >= 300) lastErr = "error " + code;
            return code < 300;
        } catch (Exception e) { lastErr = "offline"; return false; }
        finally { if (con != null) con.disconnect(); }
    }

    static JSONObject copy(JSONObject o) { try { return new JSONObject(o.toString()); } catch (Exception e) { return new JSONObject(); } }

    /** a tap on the card: show the result straight away, then save in the background (put it back and say why if that fails) */
    static synchronized void run(Context ctx, String kind) {
        try {
            JSONObject c = config(ctx);
            JSONObject hub = c.optJSONObject("hub"); if (hub == null) hub = new JSONObject();
            long ms = System.currentTimeMillis();
            String me = c.optString("me", "");
            String[] part = kind.split(":");

            if ("pick".equals(part[0])) {   // open or close a tile's choices (nothing is logged)
                String p = part.length > 1 ? part[1] : "none";
                if ("none".equals(p)) hub.remove("pick"); else hub.put("pick", p);
                hub.remove("flash");
                c.put("hub", hub); save(ctx, c); show(ctx, hub);
                return;
            }

            if ("ftype".equals(part[0])) {   // Feed card tab: switch Formula / Breastmilk (nothing is logged)
                hub.put("feedType", part.length > 1 ? part[1] : "formula");
                hub.remove("flash");
                c.put("hub", hub); save(ctx, c); show(ctx, hub);
                return;
            }

            if ("bf".equals(part[0])) {   // breastfeeding: bf:L / bf:R switch side, bf:done ends the feed
                String action = part.length > 1 ? part[1] : "done";
                JSONObject bf = c.optJSONObject("bf"); if (bf == null) return;
                String docId = bf.optString("id", ""); if (docId.isEmpty()) return;
                String side = bf.optString("side", "L");
                if (action.equals(side)) return;
                long l = bf.optLong("l", 0), r = bf.optLong("r", 0), seg = bf.optLong("segAt", ms);
                if ("L".equals(side)) l += Math.max(0, ms - seg); else r += Math.max(0, ms - seg);
                JSONObject before = copy(hub);
                boolean ok;
                if ("done".equals(action)) {
                    for (String k : new String[]{"bfSide", "bfL", "bfR", "bfSeg", "bfAt"}) hub.remove(k);
                    hub.put("feedAt", bf.optLong("at", ms));
                    hub.put("flash", "✓ Logged " + clock(ms) + " · tap to edit"); hub.put("flashKind", "feed"); hub.remove("pick");
                    show(ctx, hub);
                    ok = write(c, docId, new JSONObject().put("l", l).put("r", r).put("end", ms).put("segAt", JSONObject.NULL), new String[]{"l", "r", "end", "segAt"});
                    if (ok) c.remove("bf");
                } else {
                    hub.put("bfSide", action); hub.put("bfL", l); hub.put("bfR", r); hub.put("bfSeg", ms);
                    hub.remove("flash"); hub.remove("pick");
                    show(ctx, hub);
                    ok = write(c, docId, new JSONObject().put("l", l).put("r", r).put("side", action).put("segAt", ms), new String[]{"l", "r", "side", "segAt"});
                    if (ok) { bf.put("l", l); bf.put("r", r); bf.put("side", action); bf.put("segAt", ms); c.put("bf", bf); }
                }
                if (!ok) { hub = before; hub.put("flash", "Couldn’t save (" + lastErr + ") · open app"); hub.put("flashKind", "feed"); }
                c.put("hub", hub); save(ctx, c); show(ctx, hub);
                return;
            }

            String key = part[0];
            if (!key.equals("sleep") && !key.equals("feed") && !key.equals("diaper") && !key.equals("pump")) key = "diaper";
            JSONObject before = copy(hub);
            String napId = c.optString("napId", "");
            boolean napOpen = !napId.isEmpty();
            if (key.equals("sleep")) { if (napOpen) { hub.remove("sleepAt"); hub.put("wakeAt", ms); } else hub.put("sleepAt", ms); }
            else hub.put(key + "At", ms);
            // a choice from an opened card (60 ml, Poop…) turns green with ✓ right away; the card closes once it's saved
            boolean picked = hub.has("pick") && !hub.isNull("pick") && part.length >= 2;
            if (picked) hub.put("chosen", kind);
            else { hub.put("flash", "✓ Logged " + clock(ms) + " · tap to edit"); hub.put("flashKind", key); hub.remove("pick"); }
            show(ctx, hub);
            long shownAt = System.currentTimeMillis();

            boolean ok;
            if (key.equals("sleep")) {
                if (napOpen) {
                    ok = write(c, napId, new JSONObject().put("end", ms), new String[]{"end"});
                    if (ok) c.put("napId", "");
                } else {
                    String nid = newId();
                    ok = write(c, nid, new JSONObject().put("cat", "nap").put("at", ms).put("by", me).put("end", JSONObject.NULL).put("quick", true), null);
                    if (ok) c.put("napId", nid);
                }
            } else {
                String cat = key.equals("feed") ? "feeding" : key;
                JSONObject tpl = c.optJSONObject("tpl");
                JSONObject f = tpl != null && tpl.optJSONObject(key) != null ? copy(tpl.optJSONObject(key)) : new JSONObject();
                if (key.equals("feed") && part.length >= 3) f = new JSONObject().put("type", part[1]).put("ml", Integer.parseInt(part[2]));
                if (key.equals("diaper") && part.length >= 2) f = new JSONObject().put("kind", part[1]);
                if (key.equals("pump") && part.length >= 2) f.put("ml", Integer.parseInt(part[1]));
                f.put("cat", cat).put("at", ms).put("by", me).put("quick", true);
                ok = write(c, newId(), f, null);
            }
            if (picked && ok) {
                long wait = 800 - (System.currentTimeMillis() - shownAt);   // keep the green ✓ up long enough to see
                if (wait > 0) try { Thread.sleep(wait); } catch (InterruptedException ignored) {}
                hub.remove("chosen"); hub.remove("pick");
                hub.put("flash", "✓ Logged " + clock(ms) + " · tap to edit"); hub.put("flashKind", key);
                if (key.equals("feed") && part.length >= 3) hub.put("feedType", part[1]);
            }
            if (!ok) { hub = before; hub.put("flash", "Couldn’t save (" + lastErr + ") · open app"); hub.put("flashKind", key); hub.remove("pick"); }
            c.put("hub", hub); save(ctx, c); show(ctx, hub);
        } catch (Exception e) {
            lastErr = String.valueOf(e.getMessage());
        }
    }
}
