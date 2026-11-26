// Run: cd functions && npm test   (no Firebase or Apple needed: a stand-in push server runs locally)
process.env.GOLDFOX_TEST = '1';
const F = require('./index.js'), crypto = require('crypto'), http2 = require('http2'), { execSync } = require('child_process'), fs = require('fs'), os = require('os'), path = require('path');
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++ };
const at = (h, m) => Date.parse('2026-11-26T' + String(h).padStart(2, '0') + ':' + String(m || 0).padStart(2, '0') + ':00+08:00');   // Singapore time

// what it says
ok(F.describe({ cat: 'feeding', type: 'formula', ml: 50 })[1] === 'Formula · 50 ml', 'formula: "Formula · 50 ml"');
ok(F.describe({ cat: 'diaper', kind: 'both' })[1] === 'Diaper · Pee + Poop', 'diaper: "Diaper · Pee + Poop"');
ok(F.describe({ cat: 'nap', at: 0, end: 80 * 6e4 })[1] === 'Sleep · 1h 20m', 'finished sleep: "Sleep · 1h 20m"');
ok(F.describe({ cat: 'custom', label: 'Temperature', temp: 36.9 })[1] === 'Temperature · 36,9 °C', 'temperature: "Temperature · 36,9 °C"');
const p1 = F.payload({ cat: 'feeding', type: 'breastmilk', ml: 70, by: 'Mama Fox' }, false);
ok(p1.aps.alert.title === '🍼 Mama Fox' && p1.aps.alert.body === 'Breastmilk · 70 ml' && p1.aps.sound === 'ping.caf', 'daytime: "🍼 Mama Fox / Breastmilk · 70 ml" with the soft bell');

// quiet hours on each phone's own clock
ok(F.isQuiet('Asia/Singapore', at(0, 0)) && F.isQuiet('Asia/Singapore', at(3, 30)) && F.isQuiet('Asia/Singapore', at(7, 59)), '00:00, 03:30 and 07:59 in Singapore: quiet');
ok(!F.isQuiet('Asia/Singapore', at(8, 0)) && !F.isQuiet('Asia/Singapore', at(23, 59)), '08:00 and 23:59: sound on');
ok(!F.isQuiet('Europe/London', at(3, 30)), 'a phone set to London time at 03:30 Singapore (19:30 there): sound on');
const p2 = F.payload({ cat: 'diaper', kind: 'wet', by: 'Papa Fox' }, true);
ok(!p2.aps.sound && p2.aps['interruption-level'] === 'passive' && p2.aps.alert, 'quiet: still shows, no sound');

// who gets it
const devs = [{ id: 'mama', token: 't1', platform: 'ios', name: 'Mama Fox', notify: true }, { id: 'papa', token: 't2', platform: 'ios', name: 'Papa Fox', notify: true },
  { id: 'old', platform: 'ios', name: 'Grandma' }, { id: 'off', token: 't3', platform: 'ios', name: 'Auntie', notify: false }];
ok(F.recipients(devs, { by: 'Papa Fox', dev: 'papa' }).map(d => d.id).join() === 'mama', 'Papa logs: only Mama’s phone is pinged (not Papa’s own, not phones without notifications)');
ok(F.recipients(devs, { by: 'Mama Fox' }).map(d => d.id).join() === 'papa', 'older entry without a phone id: skips by name');
const now = at(14);
ok(F.shouldNotify({ cat: 'feeding', at: now - 60e3 }, now) && !F.shouldNotify({ cat: 'custom', at: now - 3 * 864e5 }, now), 'fresh entries notify; filling in a day 3 days ago does not');

// Apple push: signed request to a stand-in server
(async () => {
  const { privateKey, publicKey } = crypto.generateKeyPairSync('ec', { namedCurve: 'P-256' });
  const pem = privateKey.export({ type: 'pkcs8', format: 'pem' });
  const jwt = F.apnsJwt(pem, 'ABC123DEFG', 'TEAM123456', now);
  const [h, b, sg] = jwt.split('.');
  ok(crypto.verify('sha256', Buffer.from(h + '.' + b), { key: publicKey, dsaEncoding: 'ieee-p1363' }, Buffer.from(sg, 'base64url')) &&
     JSON.parse(Buffer.from(b, 'base64url')).iss === 'TEAM123456', 'sign-in token for Apple is valid');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'apns'));
  execSync('openssl req -x509 -newkey rsa:2048 -nodes -subj /CN=localhost -keyout ' + dir + '/k.pem -out ' + dir + '/c.pem -days 1 2>/dev/null');
  const got = [];
  const srv = http2.createSecureServer({ key: fs.readFileSync(dir + '/k.pem'), cert: fs.readFileSync(dir + '/c.pem') }, (req, res) => {
    let d = ''; req.on('data', x => d += x); req.on('end', () => { got.push({ h: req.headers, body: JSON.parse(d) }); res.writeHead(req.url.endsWith('/gone') ? 410 : 200); res.end(req.url.endsWith('/gone') ? '{"reason":"Unregistered"}' : '') });
  });
  await new Promise(r => srv.listen(0, r));
  const host = 'localhost:' + srv.address().port, opt = { ca: fs.readFileSync(dir + '/c.pem') };
  const r1 = await F.apnsSend(host, jwt, 'abc', p1, opt), r2 = await F.apnsSend(host, jwt, 'gone', p1, opt);
  const g = got[0];
  ok(r1.status === 200 && g.h[':path'] === '/3/device/abc' && g.h['apns-topic'] === 'com.honeybeebaby.app' && g.h.authorization === 'bearer ' + jwt && g.body.aps.sound === 'ping.caf', 'sends to Apple with the right app, sign-in and sound');
  ok(r2.status === 410, 'a phone that deleted the app is noticed (its address gets cleared)');
  srv.close(); console.log(fails ? fails + ' FAILED' : 'all passed'); process.exit(fails ? 1 : 0);
})();
