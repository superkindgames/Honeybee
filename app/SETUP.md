# Honey Bee app: setup steps for Stefan

This folder is the App Store / Google Play version of Honey Bee. It is built from the family app
(`../index.html`) but **never uses the family database**: until its own database is set up, everything
is saved on the phone only.

## 1. Create the app ID (5 min)

developer.apple.com/account → **Certificates, IDs & Profiles** → **Identifiers** → **+** → **App IDs** → **App**

- Description: `Honey Bee Baby Tracker`
- Bundle ID: **Explicit** → `com.honeybeebaby.app`
- Continue → **Register**

## 2. Create the app in App Store Connect (5 min)

appstoreconnect.apple.com → **Apps** → **+** → **New App**

- Platform: iOS · Name: `Honey Bee Baby Tracker` · Language: English (U.S.)
- Bundle ID: `com.honeybeebaby.app` · SKU: `HONEYBEE001` · Full Access → **Create**

## 3. Create the upload key (5 min)

appstoreconnect.apple.com → **Users and Access** → **Integrations** → **App Store Connect API** → **+**

- Name: `Honey Bee builder`
- Access: **Admin** (needed so the cloud builder can make its own signing certificate)
- **Download the .p8 file** (Apple only lets you do this once). Note the **Key ID** and the **Issuer ID** on that page.

Also find your **Team ID**: developer.apple.com/account → **Membership details** → *Team ID* (10 letters/numbers).

## 4. Save the key in GitHub Secrets (5 min). Never paste it into a chat.

github.com/superkindgames/Honeybee → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Add four:

| Name | What to paste |
|---|---|
| `ASC_KEY_ID` | the Key ID |
| `ASC_ISSUER_ID` | the Issuer ID |
| `ASC_PRIVATE_KEY` | open the .p8 file in a text editor and paste **everything**, including the BEGIN and END lines |
| `APPLE_TEAM_ID` | your Team ID |

## 5. Build

github.com/superkindgames/Honeybee → **Actions** → **App build** → **Run workflow**.

About 10–15 minutes later the build appears in App Store Connect → **TestFlight**. Add yourself (and your wife) under
**Internal Testing**, install the free **TestFlight** app on the iPhone, and Honey Bee installs like a normal app.

The same run also makes an **Android test file** (bottom of the run page → *HoneyBee-android-test*) that can be
installed directly on an Android phone.

## Later

- Own secure database (Firebase project + invisible sign-in) so partners can share in the app version.
- Move this folder to its own private GitHub project.
- Native extras: home-screen widget, lock-screen sleep timer, reminders, Apple Watch.
