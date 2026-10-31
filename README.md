# Little Log

A simple shared baby tracker: feeding, diapers, naps and custom entries, each in about three taps.

- `index.html` is the whole app (hosted with GitHub Pages).
- Entries are stored in Firebase Firestore under `families/<family code>/`.
- `firestore.rules` holds the database rules (paste them into the Firebase console under Firestore → Rules).
- Open the app with your family link (`?f=<family code>`) once; each phone remembers it after that.
