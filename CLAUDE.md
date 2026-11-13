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
