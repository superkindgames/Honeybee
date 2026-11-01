# Honey Bee

A simple shared baby tracker: feeding, diapers, naps and custom entries, each in about three taps.

- `index.html` is the whole app (hosted with GitHub Pages).
- Entries are stored in Firebase Firestore under `families/<family code>/`.
- `firestore.rules` holds the database rules (paste them into the Firebase console under Firestore → Rules).
- Open the app with your family link (`?f=<family code>`) once; each phone remembers it after that.

## Releasing an update
Bump `VERSION` in `index.html` and `v` in `version.json` to the same new value. Open apps notice the new version and reload themselves.
