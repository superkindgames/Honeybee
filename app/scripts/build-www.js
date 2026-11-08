/* Builds the app's web files (app/www) from the family web app (../index.html).
   Database settings come from app/firebase-config.json (no file = phone-only mode).
   TestFlight family build (Nov 2026): uses the family database, so the app and the
   web app share one live log. Each phone joins with its family link (never built in).
   Before a PUBLIC App Store release, switch this file to the app's own database. */
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..','..'),www=path.join(__dirname,'..','www');
fs.mkdirSync(www,{recursive:true});
let s=fs.readFileSync(path.join(root,'index.html'),'utf8');
const swap=(re,to,name)=>{if(!re.test(s))throw new Error('build-www: could not find '+name);s=s.replace(re,to)};

// 1. own database (or none yet)
const cfgFile=path.join(__dirname,'..','firebase-config.json');
const cfg=fs.existsSync(cfgFile)?fs.readFileSync(cfgFile,'utf8').trim():'null';
swap(/const FIREBASE_CONFIG=\{[\s\S]*?\};/,'const FIREBASE_CONFIG='+cfg+';   // from app/firebase-config.json','Firebase config');

// 2. no web "check for a newer version" reload inside the app (updates come from the App Store)
swap(/async function checkUpdate\(\)\{/,'async function checkUpdate(){return;','checkUpdate');

// 3. bees fly by rarely, not every 5 seconds
s=s.replace('const BEE_TEST=true;','const BEE_TEST=false;');

// 4. friendlier note while sharing isn't switched on yet
// (connecting to the family is done in the app: paste the family link once)

// 5. app shell niceties
s=s.replace('<head>','<head>\n<meta name="format-detection" content="telephone=no">');
fs.writeFileSync(path.join(www,'index.html'),s);
for(const f of ['aid-choking.jpg','aid-cpr.jpg','bee-180.png','bee-192.png','bee-512.png','manifest.webmanifest','version.json'])
  if(fs.existsSync(path.join(root,f)))fs.copyFileSync(path.join(root,f),path.join(www,f));
console.log('www built:',Math.round(s.length/1024)+'KB', cfg==='null'?'(phone-only mode)':'(shared database)');
