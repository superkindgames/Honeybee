# CLAUDE.md

Guidance for Claude when working on Honey Bee: Baby Tracker.

## How to reply
- Be concise. Plain English, no unexplained jargon (the owner has no coding background).
- End every reply with a sign-off line that includes a timestamp in Singapore time:
  `✅ TASK COMPLETE (HH:MM SGT): one-line summary`
  Get the time with `TZ=Asia/Singapore date '+%H:%M'`; don't guess it.
- Suggest a commit message for every change.
- For any visual or design change, show mockups first and wait for the owner's pick before building it.
- Apply every design or feature change consistently across the whole product: app screens (light and dark), lock screen / Live Activity, widgets, website and mockups. Never leave one place on the old look.
- Anything ongoing or highlighted (running sleep, breastfeed, live tiles, ongoing rows, timers) always gets the soft breathing glow plus the moving shine, everywhere it appears.

## Performance (battery, data, cost) — from the start, on every change
- Build every feature light from the start, without lowering quality, visuals or feel:
  - Continuous animations only change `opacity` or `transform` (fade a pre-drawn glow layer; never animate box-shadow, size, colour or position).
  - The screen updates in place (`patchHTML`); don't rebuild with `innerHTML` or restart animations needlessly.
  - Timers and animations do nothing while the app is in the background (`document.hidden`, `html.bg`).
  - Download only what's needed: Firestore reads are the main cost. Use the live 3-day window plus the phone's saved copy (`liveCol`); no new full-collection listeners.
  - Lock-screen and native code update only when something changes.
- After every change, run `node tools/perf-check.js HEAD 20`, which compares with the last commit. It must say "Performance check passed": no heavy animations, memory flat, no errors. Report the before/after numbers in plain words.
