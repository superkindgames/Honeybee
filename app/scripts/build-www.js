/* Builds the app's web files (app/www) from the family web app (../index.html).
   The App Store version must never touch the family database, so the Firebase
   settings are replaced with the app's own (app/firebase-config.json). Until that
   file exists, the app saves everything on the phone only. */
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..','..'),www=path.join(__dirname,'..','www');
fs.mkdirSync(www,{recursive:true});
let s=fs.readFileSync(path.join(root,'index.html'),'utf8');
const swap=(re,to,name)=>{if(!re.test(s))throw new Error('build-www: could not find '+name);s=s.replace(re,to)};

// 1. own database (or none yet)
const cfgFile=path.join(__dirname,'..','firebase-config.json');
const cfg=fs.existsSync(cfgFile)?fs.readFileSync(cfgFile,'utf8').trim():'null';
swap(/const FIREBASE_CONFIG=\{[\s\S]*?\};/,'const FIREBASE_CONFIG='+cfg+';   // App Store version: its own database, never the family one','Firebase config');

// 2. no web "check for a newer version" reload inside the app (updates come from the App Store)
swap(/async function checkUpdate\(\)\{/,'async function checkUpdate(){return;','checkUpdate');

// 3. bees fly by rarely, not every 5 seconds
s=s.replace('const BEE_TEST=true;','const BEE_TEST=false;');

// 4. friendlier note while sharing isn't switched on yet
s=s.replace('Setup isn’t finished, so entries are saved on this phone only.','Test version: everything is saved on this phone. Sharing with your partner comes in the next update.');

// 5. app shell niceties
s=s.replace('<head>','<head>\n<meta name="format-detection" content="telephone=no">');
fs.writeFileSync(path.join(www,'index.html'),s);
for(const f of ['aid-choking.jpg','aid-cpr.jpg','bee-180.png','bee-192.png','bee-512.png','manifest.webmanifest','version.json'])
  if(fs.existsSync(path.join(root,f)))fs.copyFileSync(path.join(root,f),path.join(www,f));
console.log('www built:',Math.round(s.length/1024)+'KB', cfg==='null'?'(phone-only mode)':'(own database)');
