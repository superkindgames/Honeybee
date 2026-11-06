# Honey Bee roadmap

Ideas and decisions to remember. Nothing here is built yet unless it says so.

## Design rules (check every new feature against these)

Learned from trying Huckleberry, which feels bloated: Reports opens on a graph instead of a list, Sleep Plans, an "Insights" tab of quotes, a Child tab full of settings and questionnaires, and an AI tab.

1. The log opens as a list (newest first). Charts and stats are one tap away, never the first view.
2. No sleep plans or coaching programs; only gentle hints (like the next-sleep window).
3. No filler content (quotes, generic "insights"). Every screen must do something.
4. The baby's page is about the baby: name, age, growth, moments. Not settings or questionnaires.
5. No questionnaires. If we ask anything, it is one tap on a preset and optional.
6. No AI tab.
7. At most four places to go: Home (log fast), Log (look back), Baby (growth, goals, moments), SOS.
8. Logging any event stays 3 taps or fewer.
9. **The app grows with the child.** Show only what fits the baby's age right now; new things appear when they become relevant (with a gentle "new for this age" note), and things that no longer fit quietly step back. Never make a parent of a newborn scroll past toddler or school-age features. Nothing is ever lost: older or future features stay findable, and the parent can always override (keep a tile, hide a tile).

## Grows with your child (core idea, noted 2026-11-04)

Positioning: "Honey Bee cradles you like you cradle your baby." Competitors show every feature from day one (e.g. teeth charts on day 20). Honey Bee evolves by age without the parent having to think about it.

Already working this way: milestone guide stages and the age-aware milestone checklist (v56), "New stage" badge (v46), age-based achievements, care presets and reminders.

Next steps to build it out:
- **Age-aware home tiles:** e.g. Pumping and cord care fade out of focus as feeding changes; Solids / first foods appears around 6 months; Teeth around 6–10 months; Potty around 2 years. Always with a one-tap "keep it" / "hide it".
- **"New for this age" moments:** a short, friendly card when something new unlocks ("Luna is 6 months: first foods tracking is now on your Home screen").
- **Settings stay simple:** an "All features" page lists everything for parents who want to look ahead.
- Focus now: the 0–4 year journey. Later the same app can grow into a tool for older children (school, activities, health records up to ~12 years) and would look very different at that age.
- Marketing: "The app that grows with your baby" on the landing page and store listing.

## From looking at Huckleberry (noted 2026-11-03)

- **Home-screen widget + install help.** Map out what a widget shows (for example last feed, awake time, next-sleep hint, one-tap log buttons) and add a short, friendly "how to install" guide for iPhone and Android.
- **ml or oz by region.** Pick ml or fl oz automatically from the phone's region (US uses oz), with a manual switch. Presets need sensible oz values too (for example 0.5, 1, 1.5 … 3 oz).
- **Language / localization.** Prepare for translations if the app goes international (all text in one place, dates and numbers in local format). Swedish could be an early second language.
- **Milestones ("Moments").** Their app has a milestones tab (first eye contact, first smile …). Ours: preset "firsts" grouped by age (eye contact, bath, social smile, coo, laugh, head up, rolls over, first tooth, sits, crawls, first word, first steps), tap to save with today's date, edit date with the wheels, optional note, "+ Add your own", warm timeline showing her age at each moment, optional photos later, feeds the keepsake export. Never say a baby is "late" or "behind"; link to the CDC Milestone Tracker for development checks. Entry point: a "Moments" button on the Growth page.
- **Lock-screen sleep timer (native app only).** Huckleberry shows a running sleep timer with On/Off buttons on the lock screen. Ours: iPhone Live Activity + Dynamic Island ("Violetta sleeping · 42m" [Woke up]; when awake "Awake 35m · next sleep ~14:10" [Fell asleep]), Android ongoing notification with action buttons. Not possible in the web app; needs the Capacitor/App Store version with a small native extension. Together with widgets and reminders, a main reason to go native.
- **Sleep banner (built v47) → next: widget + lock screen.** The web app now shows a sleep banner on top of every page while a sleep is running (Woke up, woke up earlier, change start, remove by mistake; turns orange on a very long sleep). The native version should mirror it with a home-screen widget and a lock-screen timer, both with Start / Stop buttons.
- **Smartwatch support (Apple Watch + Android / Wear OS watches), native app only.** Log from the wrist in 1–2 taps while holding the baby: Fell asleep / Woke up, feed (last type + preset ml), Pee / Poop. Show the running sleep timer and "last feed 2h 10m ago" as a watch face complication. Reminders (care due, next sleep) as gentle wrist taps. Syncs with the shared log like the phones. Builds on the App Store version: Apple Watch app via a small watchOS extension (SwiftUI), Wear OS app for Android watches. Competitor note: Vivi Baby already advertises Apple Watch.
- **Sleep reminders.** Huckleberry's SweetSpot only starts at 2 months; it can remind you 15 min before the ideal sleep time. Ours: our next-sleep hint already works from birth (keep the wording humble under ~8 weeks). Add a setting "Remind me X min before next sleep" (default 15, on/off). In the App Store version use on-phone local notifications (no server). In the current web app it would need web push from a server (Firebase Cloud Functions + pay-as-you-go plan).
- **Their AI assistant asks 10–15 questions with no preset answers.** If we ever ask questions (onboarding or otherwise), always offer tap-to-answer presets. Stefan will try their assistant to see what it actually does.

## Ideas discussed, not built yet

- 📌 **Guiding parents (pinned for later):** an informative "Care routine" guide on the Baby tab for new parents who aren't sure what to do once home (what to wash, how often, nails, cord care, nose…), changing with the baby's age like the Milestones guide. Logging and on-screen reminders for these already exist via the Add Custom presets (v52).
- **Achievements ideas for later:** first trip out, first night at grandparents', first holiday; weekly "family recap" card to share between parents.

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
- **Pricing decided (2026-11-04): $4.99 / month or $24.99 lifetime (one-time; lowered from $49.99 on 2026-11-06).** One purchase covers both parents (and future siblings). **10-day free trial** (decided 2026-11-04) with no card, no sign-up and no automatic billing, and no banners; one gentle reminder 2 days before it ends; friendly screen on the last day. After the trial, data always stays readable and exportable (never lock families out of their history, the thing that upset Nara users). Use Apple / Google regional pricing (lower in e.g. Malaysia/Indonesia). Optional launch offer for "founding parents". Competitor context: Nara $9.99/mo or $99.99 lifetime (paid since 2026, read-only without paying), Huckleberry Plus ~$59/yr, Premium ~$120/yr. (Earlier plan was $10 once.)
- Payments: App Store / Google Play in-app purchase (Face ID / fingerprint, no card typing), via RevenueCat.
- Name decision (2026-11-04): **stay with Honey Bee** for now.
- Tagline / copy idea: **"An app for busy bees"** (also: "For busy bee parents", "Made for busy bees"). Use "busy bee" only in copy, not as the app name: Busy Bees is a large childcare chain with its own parent apps (also in Singapore/Malaysia), and the App Store already has several "Busy Bee(s)" apps.
- **Chosen tagline:** "Feeds, naps & diapers in 3 taps. An app for busy bees." (store promo text / screenshots / website). App Store subtitle max 30 characters, so there use "Feeds, naps & diapers, 3 taps" (29).
- Other name ideas from brainstorming (unchecked): Honeycomb, Baby Hive, Busy Hive, Buzzy Baby, Milk & Moon, Two Bees, Tag Team Baby.
- Name idea saved for later (not in use): **Baby Bee Tracker**. Check first: Burt's Bees sells a baby skincare line called "Baby Bee", so there is a trademark risk in the same baby space.
- Store name: **Honey Bee Baby Tracker**, subtitle "Feeds, naps & diapers for two", home-screen label "Honey Bee".
- Before charging: check the choking/CPR picture's licence/source (its hand technique matches the 2025 AHA/AAP guidance: heel of one hand or 2-thumb encircling; the old 2-finger method was dropped), and re-check first-aid text whenever guidelines update, check WHO growth data licence (or use CDC copies), check the location lookup service's terms, add medical disclaimers, privacy policy, in-app account/data deletion.
- **Developer account decision (2026-11-04): start as an individual (seller name "Stefan Linde")** for TestFlight testing and the first launch; convert the same Apple account to an organisation later (Apple Developer Support, "Account Updates and Renewals"), which keeps the listing, ratings, reviews and users. Note: in the EU App Store an individual trader's contact details are shown publicly.
- EP rules (MOM): being a director or registering a business needs a Letter of Consent; easy only for companies related to the employer, otherwise assessed by the industry's government agency. Other routes: ONE Pass (if eligible), or the Dependant's Pass business-owner LOC (≥30% shares + 1 local hire on CPF).
- Company: Singapore Pte Ltd (seller name e.g. "Humble Bee Pte. Ltd.") after written OK from employer and advice on Employment Pass rules.
- Validate first: 5–10 test couples for 2–4 weeks; key question is whether they still log in week 3.

## Milestone guide: grow it with the baby

Built (v46): the guide picks its stage from the baby's age by itself, the Baby page shows "New stage" when she moves into the next one, and past the last stage it says more guidance is coming. Adding a stage = adding one entry to `STAGES` in index.html; it reaches both phones through the normal auto-update.

Done (v56): stages written and live for **15–18 months** (Little explorer), **18–24 months** (Busy toddler) and **2–3 years** (Little chatterbox), each with what to expect, play, care & hygiene, safety and health checks. The milestone checklist got three matching groups (20 new milestones from the CDC 2022 "Learn the Signs. Act Early." list), now 39 in total. The checklist only shows age groups the baby has reached (plus the next ~2 months); later ones are behind "Show later milestones". Past 3 years the guide says more is coming.

Still to do:
- **3–4 years stage** (and checklist) before the first users' children reach ~3 (preschool, toilet independence, pea-sized toothpaste, scooter/bike safety, eye test).
- Have the stage texts reviewed by a health professional (nurse / paediatrician) before the public launch.
- Check the existing stages against current WHO / NHS / AAP advice once a year.

## App Store / Google Play app (started 2026-11-04)

- Lives in `app/` (Capacitor 7, app ID `com.honeybeebaby.app`, name "Honey Bee"). Built from the family web app by `app/scripts/build-www.js`, which swaps in the app's own database settings, so the app can never touch the family database. Until its own Firebase project exists, the app saves everything on the phone only.
- Cloud build: `.github/workflows/app-build.yml`. iPhone → TestFlight once the four Apple secrets are saved (see `app/SETUP.md`); Android → downloadable test APK on every run.
- Security rules for the app's own database are ready in `app/firestore.rules` (invisible sign-in, members only, one-time expiring invites).
- Next: Stefan adds the Apple key; create the app's Firebase project; build "Start a family / Join with invite" + invisible sign-in; move `app/` to its own private GitHub project; native widget, lock-screen sleep timer, reminders.
