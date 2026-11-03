# Honey Bee roadmap

Ideas and decisions to remember. Nothing here is built yet unless it says so.

## From looking at Huckleberry (noted 2026-11-03)

- **Home-screen widget + install help.** Map out what a widget shows (for example last feed, awake time, next-sleep hint, one-tap log buttons) and add a short, friendly "how to install" guide for iPhone and Android.
- **ml or oz by region.** Pick ml or fl oz automatically from the phone's region (US uses oz), with a manual switch. Presets need sensible oz values too (for example 0.5, 1, 1.5 … 3 oz).
- **Language / localization.** Prepare for translations if the app goes international (all text in one place, dates and numbers in local format). Swedish could be an early second language.
- **Milestones ("Moments").** Their app has a milestones tab (first eye contact, first smile …). Ours: preset "firsts" grouped by age (eye contact, bath, social smile, coo, laugh, head up, rolls over, first tooth, sits, crawls, first word, first steps), tap to save with today's date, edit date with the wheels, optional note, "+ Add your own", warm timeline showing her age at each moment, optional photos later, feeds the keepsake export. Never say a baby is "late" or "behind"; link to the CDC Milestone Tracker for development checks. Entry point: a "Moments" button on the Growth page.
- **Their AI assistant asks 10–15 questions with no preset answers.** If we ever ask questions (onboarding or otherwise), always offer tap-to-answer presets. Stefan will try their assistant to see what it actually does.

## Ideas discussed, not built yet

- **Boy / Girl setting** so wording ("she/her") and WHO growth charts match the baby.
- **Weekly and monthly summaries** (totals, averages, trend vs last week, weight gain).
- **Voice entry without AI** (phone dictation + keyword matching, confirm before saving).
- **Handover summary**: "Since you went to sleep: 2 feeds, 1 wet diaper, slept 2h 10m."
- **Doctor-visit report**: one-page summary of the last 2 weeks.
- **Caregiver access** (grandparent / nanny) with a simple invite.
- **Keepsake export** at the end ("Violetta's first year").

## Public launch plan (separate project, never touching the family app)

- Separate repo, separate Firebase project, separate web address.
- Invisible accounts (no sign-up), invite link for the partner, optional Sign in with Apple/Google for backup.
- Pricing decided: free to use with no card and no banners; one gentle reminder 2 days before the free period ends; friendly screen on the last day; **$10 once (lifetime), no subscription**; one purchase covers both parents. After the free period, data stays readable and exportable.
- Payments: App Store / Google Play in-app purchase (Face ID / fingerprint, no card typing), via RevenueCat.
- Store name: **Honey Bee Baby Tracker**, subtitle "Feeds, naps & diapers for two", home-screen label "Honey Bee".
- Before charging: replace the choking/CPR picture (it shows a whole hand on a baby's chest), check WHO growth data licence (or use CDC copies), check the location lookup service's terms, add medical disclaimers, privacy policy, in-app account/data deletion.
- Company: Singapore Pte Ltd (seller name e.g. "Humble Bee Pte. Ltd.") after written OK from employer and advice on Employment Pass rules.
- Validate first: 5–10 test couples for 2–4 weeks; key question is whether they still log in week 3.
