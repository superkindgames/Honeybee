/* Goldfox partner notifications.
   When a new entry lands in families/<code>/events, every OTHER phone in that family that switched notifications on
   (families/<code>/devices/<id>, written by the app) gets a soft ping from Apple: "🍼 Mama Fox · Formula · 50 ml".
   - The phone that logged it is skipped (the entry carries its device id in `dev`; older entries fall back to the name).
   - 00:00–08:00 on each phone's own clock: the notification still shows, but silently.
   - Only fresh entries notify (not back-filled days or old copies), and edits/deletes never do.
   Secrets (set once by the deploy workflow): APNS_KEY (the .p8 key text), APNS_KEY_ID, APPLE_TEAM_ID. */
const http2 = require('http2');
const crypto = require('crypto');

const BUNDLE = 'com.honeybeebaby.app';
const SOUND = 'ping.caf';
const QUIET_FROM = 0, QUIET_TO = 8;               // 00:00–08:00, no sound
const FRESH_MS = 2 * 3600e3;                      // only entries for roughly "now" notify

let REGION = 'us-central1';
try { REGION = require('./region.json').region || REGION } catch (e) {}

/* ---------- pure helpers (tested in functions/test.js) ---------- */
function dur(min) { min = Math.max(0, Math.round(min)); const h = Math.floor(min / 60), m = min % 60; return h ? h + 'h' + (m ? ' ' + m + 'm' : '') : m + 'm' }
function describe(e) {
  const ml = e.ml ? ' · ' + Math.round(+e.ml) + ' ml' : '';
  switch (e.cat) {
    case 'feeding':
      if (e.type === 'breastfeed') { const t = ((+e.l || 0) + (+e.r || 0)) / 6e4; return ['🤱', 'Breastfeed' + (t ? ' · ' + dur(t) : '')] }
      return ['🍼', (e.type === 'formula' ? 'Formula' : e.type === 'breastmilk' ? 'Breastmilk' : 'Feeding') + ml];
    case 'diaper': return ['🧷', 'Diaper · ' + ({ wet: 'Pee', dirty: 'Poop', both: 'Pee + Poop' }[e.kind] || 'Changed')];
    case 'nap': return ['🌙', e.end ? 'Sleep · ' + dur((e.end - e.at) / 6e4) : 'Fell asleep'];
    case 'pump': return ['💛', 'Pumped' + (e.ml ? ' ' + Math.round(+e.ml) + ' ml' : '')];
    case 'custom': case 'hyg': case 'med': return ['⭐', String(e.label || 'Care') + (e.temp != null ? ' · ' + String(e.temp).replace('.', ',') + ' °C' : '')];
    case 'photo': return ['📷', 'Added a photo'];
    case 'milestone': return ['🌟', String(e.label || 'A new milestone')];
    default: return ['🦊', 'New entry'];
  }
}
function hourIn(tz, now) {
  try { return +new Intl.DateTimeFormat('en-GB', { hour: 'numeric', hourCycle: 'h23', timeZone: tz || 'Asia/Singapore' }).format(now) }
  catch (e) { return +new Intl.DateTimeFormat('en-GB', { hour: 'numeric', hourCycle: 'h23', timeZone: 'Asia/Singapore' }).format(now) }
}
const isQuiet = (tz, now) => { const h = hourIn(tz, now); return h >= QUIET_FROM && h < QUIET_TO };
function payload(e, quiet) {
  const [em, what] = describe(e);
  const aps = { alert: { title: em + ' ' + (e.by || 'Your partner'), body: what }, 'thread-id': 'goldfox-log' };
  if (quiet) aps['interruption-level'] = 'passive'; else aps.sound = SOUND;
  return { aps };
}
/* who gets it: notifications on, an Apple push address, and not the phone (or person) that logged it */
function recipients(devs, e) {
  return devs.filter(d => d.token && d.notify !== false && d.platform === 'ios' &&
    (e.dev ? d.id !== e.dev : (d.name || '') !== (e.by || '')));
}
const shouldNotify = (e, now) => !!e && e.cat && Math.abs(now - (e.at || 0)) <= FRESH_MS;

/* ---------- Apple push (token auth, HTTP/2) ---------- */
let jwtCache = null;
function apnsJwt(keyPem, keyId, teamId, now) {
  if (jwtCache && now - jwtCache.at < 40 * 60e3) return jwtCache.t;
  const b64 = o => Buffer.from(JSON.stringify(o)).toString('base64url');
  const head = b64({ alg: 'ES256', kid: keyId }), body = b64({ iss: teamId, iat: Math.floor(now / 1000) });
  const sig = crypto.sign('sha256', Buffer.from(head + '.' + body), { key: keyPem, dsaEncoding: 'ieee-p1363' }).toString('base64url');
  jwtCache = { at: now, t: head + '.' + body + '.' + sig };
  return jwtCache.t;
}
function apnsSend(host, jwt, token, body, opts) {
  return new Promise(resolve => {
    const c = http2.connect('https://' + host, opts || {});
    c.on('error', err => resolve({ status: 0, err: String(err) }));
    const r = c.request({ ':method': 'POST', ':path': '/3/device/' + token, authorization: 'bearer ' + jwt,
      'apns-topic': BUNDLE, 'apns-push-type': 'alert', 'apns-priority': body.aps.sound ? '10' : '5', 'content-type': 'application/json' });
    let status = 0, data = '';
    r.on('response', h => { status = h[':status'] });
    r.on('data', d => { data += d });
    r.on('end', () => { c.close(); resolve({ status, data }) });
    r.on('error', err => { c.close(); resolve({ status: 0, err: String(err) }) });
    r.end(JSON.stringify(body));
  });
}

module.exports = { describe, isQuiet, hourIn, payload, recipients, shouldNotify, apnsJwt, apnsSend };

/* ---------- the Firebase trigger (only loaded when deployed) ---------- */
if (!process.env.GOLDFOX_TEST) {
  const { onDocumentCreated } = require('firebase-functions/v2/firestore');
  const { defineSecret } = require('firebase-functions/params');
  const admin = require('firebase-admin');
  admin.initializeApp();
  const APNS_KEY = defineSecret('APNS_KEY'), APNS_KEY_ID = defineSecret('APNS_KEY_ID'), APPLE_TEAM_ID = defineSecret('APPLE_TEAM_ID');
  exports.partnerPing = onDocumentCreated({ document: 'families/{fam}/events/{id}', region: REGION, secrets: [APNS_KEY, APNS_KEY_ID, APPLE_TEAM_ID], memory: '256MiB', maxInstances: 3 }, async ev => {
    const e = ev.data && ev.data.data(), now = Date.now();
    if (!shouldNotify(e, now)) return;
    const snap = await admin.firestore().collection('families/' + ev.params.fam + '/devices').get();
    const devs = recipients(snap.docs.map(d => Object.assign({ id: d.id }, d.data())), e);
    if (!devs.length) return;
    const jwt = apnsJwt(APNS_KEY.value(), APNS_KEY_ID.value().trim(), APPLE_TEAM_ID.value().trim(), now);
    await Promise.all(devs.map(async d => {
      const res = await apnsSend('api.push.apple.com', jwt, d.token, payload(e, isQuiet(d.tz, now)));
      if (res.status === 410 || /BadDeviceToken|Unregistered/.test(res.data || '')) await snap.docs.find(x => x.id === d.id).ref.update({ token: admin.firestore.FieldValue.delete() });
      else if (res.status !== 200) console.warn('apns', d.id, res.status, res.data || res.err);
    }));
  });
}
