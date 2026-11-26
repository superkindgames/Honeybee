# Partner notifications: one-time setup

What it does: when someone in the family logs something, the other iPhones get a very soft bell
("🍼 Mama Fox · Formula · 50 ml"). Between 00:00 and 08:00 (each phone's own clock) it still shows, but silently.
Each person turns it on in **Settings → Partner notifications**.

How it works: a small program on Firebase (`functions/index.js`) notices each new entry and asks Apple to deliver
the ping to the other phones. The app saves each phone's Apple push address in `families/<code>/devices/<id>`.
The GitHub workflow **Notifications deploy** installs it automatically once the steps below are done.

## Steps for the owner (about 10 minutes)

1. **Blaze plan** (Firebase needs it for server code; a family stays inside the free allowance)
   console.firebase.google.com → project *honeybee-33b2d* → bottom-left **Upgrade** → Blaze.
   Then: Usage and billing → Details & settings → **Budget alert** at $1.
2. **Apple push key**
   developer.apple.com → Certificates, IDs & Profiles → **Keys** → ＋ → name "Goldfox push" →
   tick **Apple Push Notifications service (APNs)** → Continue → Register → **Download** the `.p8` file
   (it can only be downloaded once) and note the **Key ID** (10 characters).
3. **Firebase key for installing**
   console.firebase.google.com → ⚙ Project settings → **Service accounts** → **Generate new private key** (a `.json` file).
   In console.cloud.google.com → IAM, give that service account these roles: Cloud Functions Admin,
   Service Account User, Secret Manager Admin, Cloud Build Editor, Artifact Registry Administrator, Firebase Admin.
4. **GitHub Secrets** (github.com/superkindgames/Honeybee → Settings → Secrets and variables → Actions → New):
   - `FIREBASE_SERVICE_ACCOUNT` = the whole `.json` file contents
   - `APNS_KEY` = the whole `.p8` file contents
   - `APNS_KEY_ID` = the Key ID from step 2
5. Run **Actions → Notifications deploy → Run workflow**. Then on each iPhone: update Goldfox from TestFlight and
   switch on **Settings → Partner notifications**.

Never paste these keys into a chat; they only go into GitHub Secrets.

## Android
Not included yet. It needs Firebase's Android setup file (`google-services.json`); add it later if the family uses Android.
