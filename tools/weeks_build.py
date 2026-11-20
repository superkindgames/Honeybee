# Run: python3 tools/weeks_build.py weeks.json docs/week-guide-sources.md
"""Goldfox week-by-week guide, weeks 1-52 (soft version, no checklist). Every line is tied to a source id in SOURCES (checked against the source text
in Nov 2026). Writes weeks.json (for the app) and the sources document (for future reference)."""
import json,sys
OUT_JSON=sys.argv[1];OUT_MD=sys.argv[2]

SOURCES={
 'CDC':{'name':'CDC "Learn the Signs. Act Early." milestone checklists (2021 revision): 2, 4, 6, 9 and 12 months, incl. parent tips',
  'url':'https://www.cdc.gov/wic-guide/media/pdfs/FULL-LIST-CDC_LTSAE-Checklists2021_Eng_FNL2_508.pdf',
  'note':'Milestones that MOST children (at least 75%) are expected to meet by each age. Not a screening tool.'},
 'CDC-HELP':{'name':'CDC Milestones by age, "How you can help your baby learn and grow" (2 months, 4 months, 6 months, 9 months, 1 year)',
  'url':'https://www.cdc.gov/act-early/milestones/2-months.html · /4-months.html · /6-months.html · /9-months.html · /1-year.html',
  'note':'Activity and interaction ideas per age, e.g. respond to sounds to teach turn-taking; cuddle (you cannot spoil a baby by holding); tummy time with toys at eye level; peek-a-boo; copy sounds; drop-and-return game; my turn/your turn; quick cheerful goodbyes; talk about what you are doing; respond with words when baby points.'},
 'WHO-MM':{'name':'WHO Multicentre Growth Reference Study Group. WHO Motor Development Study: windows of achievement for six gross motor development milestones. Acta Paediatr Suppl 2006;450:86-95',
  'url':'https://pubmed.ncbi.nlm.nih.gov/16817682/ · table: https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/motor-development-milestones/mm_windows_table.pdf',
  'note':'1st-99th percentile windows (months): sitting without support 3.8-9.2; standing with assistance 4.8-11.4; hands-and-knees crawling 5.2-13.5; walking with assistance 5.9-13.7; standing alone 6.9-16.9; walking alone 8.2-17.6. 4.3% of children never crawled on hands and knees.'},
 'WOLKE':{'name':'Wolke D, Bilgin A, Samara M. Systematic review and meta-analysis: fussing and crying durations and prevalence of colic in infants. J Pediatr 2017;185:55-61. doi:10.1016/j.jpeds.2017.02.020',
  'url':'https://pubmed.ncbi.nlm.nih.gov/28385295/',
  'note':'Fuss/cry 117-133 min/day (mean) in the first 6 weeks, about 68 min/day by 10-12 weeks; significant drop after 8-9 weeks; no evidence of a universal peak at 6 weeks; colic 17-25% in first 6 weeks, 11% at 8-9 weeks, 0.6% at 10-12 weeks.'},
 'GALLAND':{'name':'Galland BC, Taylor BJ, Elder DE, Herbison P. Normal sleep patterns in infants and children: a systematic review of observational studies. Sleep Med Rev 2012;16:213-222. doi:10.1016/j.smrv.2011.06.001',
  'url':'https://pubmed.ncbi.nlm.nih.gov/21784676/',
  'note':'Infant sleep 12.8 h/day on average (range 9.7-15.9); night wakings 0-3.4 per night at 0-2 months.'},
 'WHO-PA':{'name':'WHO guidelines on physical activity, sedentary behaviour and sleep for children under 5 years of age (2019)',
  'url':'https://www.who.int/news/item/24-04-2019-to-grow-up-healthy-children-need-to-sit-less-and-play-more',
  'note':'Infants: active several times a day, floor-based play; at least 30 min tummy time spread through the day while awake; not restrained more than 1 h at a time; screen time not recommended; reading and storytelling encouraged; sleep 14-17 h (0-3 months), 12-16 h (4-11 months) incl. naps; 1-2 years 11-14 h.'},
 'AAP-SLEEP':{'name':'Moon RY, Carlin RF, Hand I; AAP Task Force on SIDS. Sleep-related infant deaths: updated 2022 recommendations for reducing infant deaths in the sleep environment. Pediatrics 2022;150(1):e2022057990',
  'url':'https://pubmed.ncbi.nlm.nih.gov/35726558/',
  'note':'Back to sleep; firm, flat (non-inclined) surface; room sharing without bed sharing; no soft bedding; avoid overheating; human milk feeding, immunisation and a pacifier lower risk.'},
 'AAP-VITD':{'name':'Wagner CL, Greer FR; AAP. Prevention of rickets and vitamin D deficiency in infants, children, and adolescents. Pediatrics 2008;122:1142-1152',
  'url':'https://pubmed.ncbi.nlm.nih.gov/18977996/',
  'note':'All infants, including exclusively breastfed, need at least 400 IU of vitamin D a day beginning soon after birth.'},
 'NIAID-PEANUT':{'name':'Togias A, et al. Addendum guidelines for the prevention of peanut allergy in the United States (NIAID expert panel). J Allergy Clin Immunol 2017;139:29-44',
  'url':'https://pubmed.ncbi.nlm.nih.gov/28065278/',
  'note':'Peanut allergy can be prevented by introducing peanut-containing foods in infancy; separate guidance by risk level.'},
 'AAP-MEDIA':{'name':'AAP Council on Communications and Media. Media and young minds. Pediatrics 2016;138(5):e20162591',
  'url':'https://pubmed.ncbi.nlm.nih.gov/27940793/','note':'Guidance on screen media for children 0-5; emphasises shared use and time for other healthy activities.'},
 'AAP-READ':{'name':'High PC, Klass P; AAP. Literacy promotion: an essential component of primary care pediatric practice. Pediatrics 2014;134:404-409',
  'url':'https://pubmed.ncbi.nlm.nih.gov/24962987/','note':'Reading aloud from infancy supports brain development, language and the parent-child relationship.'},
 'NHS-SOLIDS':{'name':'NHS: Your baby\'s first solid foods','url':'https://www.nhs.uk/baby/weaning-and-feeding/babys-first-solid-foods/',
  'note':'Start solids around 6 months; allergens (peanut, egg, gluten, fish) from around 6 months one at a time; no added salt or sugar; avoid whole nuts, raw carrot/apple; quarter grapes and cherry tomatoes; cows\' milk not a main drink before 1 year.'},
 'NHS-TEETH':{'name':'NHS: Baby teething symptoms','url':'https://www.nhs.uk/baby/babys-development/teething/baby-teething-symptoms/',
  'note':'Most babies start teething around 6 months; some before 4 months, some after 12 months; temperature may be slightly raised but under 38 C; no evidence teething causes diarrhoea.'},
 'NHS-FEVER':{'name':'NHS: High temperature (fever) in children','url':'https://www.nhs.uk/symptoms/fever-in-children/',
  'note':'High temperature is 38 C or more. Get urgent advice if under 3 months with 38 C or higher, or 3-6 months with 39 C or higher. No paracetamol under 2 months; no ibuprofen under 3 months or under 5 kg.'},
 'NHS-SLEEP':{'name':'NHS: Helping your baby to sleep','url':'https://www.nhs.uk/baby/caring-for-a-newborn/helping-your-baby-to-sleep/',
  'note':'Every baby\'s pattern differs; teach night vs day (low lights, quiet, little play at night); same room as you for at least the first 6 months.'},
 'SG-NCIS':{'name':'Singapore National Childhood Immunisation Schedule (NCIS), effective 1 Nov 2020 (SingHealth Polyclinics copy). MOH published an update dated 1 Apr 2026 that could not be read automatically; check it before relying on dose timing.',
  'url':'https://polyclinic.singhealth.com.sg/content/dam/singhealth-web/shp/patient-services/pdfs/national-childhood-immunisation-schedule-ncis.pdf · update: https://isomer-user-content.by.gov.sg/18/9459eb0d-6797-466d-8d85-274916ebd27e/NCIS_1%20Apr%202026.pdf',
  'note':'Birth: BCG, HepB 1. 2 m: DTaP-IPV-Hib-HepB (6-in-1) dose 1. 4 m: DTaP-IPV-Hib dose 2 + PCV 1. 6 m: 6-in-1 dose 3 (HepB 3) + PCV 2. Influenza yearly 6 months to <5 years. 12 m: MMR 1, varicella 1, PCV booster. 15 m: MMRV. 18 m: DTaP-IPV-Hib booster.'},
}

SOURCES.update({
 'AAP-VISION':{'name':'AAP HealthyChildren.org: Infant vision development: what can babies see? (adapted from Caring for Your Baby and Young Child, 8th ed., 2024)',
  'url':'https://www.healthychildren.org/English/ages-stages/baby/Pages/Babys-Vision-Development.aspx',
  'note':'Newborns see light, shapes, faces and movement; see best at 20-30 cm; eyes may wander or cross, settling by 2-3 months. By 3 months focus on faces and close objects and follow a moving object. By 4 months better colour vision, interest in round patterns, reach for close objects. By 6 months see differences between objects.'},
 'AAP-EYES':{'name':'Hill D (AAP). Newborn eye color: what parents should know. HealthyChildren.org, updated 2021',
  'url':'https://www.healthychildren.org/English/ages-stages/baby/Pages/Newborn-Eye-Color.aspx',
  'note':'Eye colour takes about a year to settle (change slows after 6 months). Crossing can be normal for the first 6 months. By week 4 the baby focuses on your face when cradled. Until 2 months may lose track of a face crossing the midline; by 2 months tracks side to side. From 6 months, an eye that does not look the same way as the other should be checked by a doctor.'},
 'AAP-HEAR':{'name':'AAP HealthyChildren.org: Hearing and making sounds (adapted from Caring for Your Baby and Young Child), updated 2021',
  'url':'https://www.healthychildren.org/English/ages-stages/baby/Pages/Hearing-and-Making-Sounds.aspx',
  'note':'Babies prefer the human voice, especially high-pitched, slow, exaggerated speech; by one month identify a parent by voice; about 2 months cooing and vowel sounds; by 4 months babble routinely and are more sensitive to tone of voice.'},
 'AAP-FUSSY':{'name':'AAP HealthyChildren.org: Colic relief tips for parents, updated 2024',
  'url':'https://www.healthychildren.org/English/ages-stages/baby/crying-colic/Pages/Colic.aspx',
  'note':'Regular fussy period, often 6 pm to midnight; carrier, rocking, white noise, pacifier, swaddling may help; it is OK to put the baby down safely and leave the room for a few minutes; never shake a baby.'},
 'AAP-COG':{'name':'AAP HealthyChildren.org: Cognitive development: 8 to 12 months (adapted from Caring for Your Baby and Young Child), updated 2023',
  'url':'https://www.healthychildren.org/English/ages-stages/baby/Pages/Cognitive-Development-8-to-12-Months.aspx',
  'note':'Attention 2-3 minutes per toy at 8 months, up to 15 minutes by 12 months; drops, rolls and throws things to learn how they behave; object permanence (searches under a scarf at 8 months, keeps looking by 10 months); peekaboo variations; household objects make the best toys; secure hazardous drawers; near 12 months uses props like a toy phone, hairbrush or cup the way adults do.'},
 'NHS-REFLUX':{'name':'NHS: Reflux in babies (reviewed June 2025)','url':'https://www.nhs.uk/conditions/reflux-in-babies/',
  'note':'Bringing up milk during or shortly after feeds is very common; usually starts before 8 weeks and gets better by age 1 as the food-pipe muscle strengthens; hold upright during and after feeds, burp regularly, keep sleep flat on the back. See a GP if reflux starts after 6 months; urgent advice for green/yellow or bloody vomit, projectile vomiting, blood in poo, swollen tummy, refusing feeds.'},
 'NHS-COLIC':{'name':'NHS: Colic (reviewed April 2022)','url':'https://www.nhs.uk/conditions/colic/',
  'note':'Colic usually stops by 3-4 months; hold upright during feeds, wind after feeds, gentle rocking, warm bath, white noise; see a GP if symptoms continue after 4 months; urgent help for a weak or high-pitched cry or a cry that does not sound like their usual cry.'},
})
# Writing rules (Nov 2026): talk to the parent about their own baby. No "most babies", "many babies", "typical" or other
# comparisons. "It's highly likely you'll see…" is used ONLY for CDC milestones (met by at least 3 in 4 children by that age);
# anything that varies more uses "you may…". Pronoun tokens are filled in by the app from the baby's sex:
# {she} {She} {her} (him) {pos} {Pos} (his) {she's} {She's}; with no sex set they read "your baby" / "your baby's".
T_KEYS=['feel','talk','mind','eyes','tummy','body','sleep','care']
W=[]
def wk(n,stage,title,head,t,play,watch,src):
    for k in t:assert k in T_KEYS,(n,k)
    W.append(dict(w=n,stage=stage,title=title,head=head,t=[[k,t[k]] for k in T_KEYS if k in t],play=play,watch=watch,src=src))
HL='It’s highly likely you’ll '
DOC='You know {her} best. If something worries you, or {she} stops doing something {she} could do before, bring it up with your doctor.'
FEV3='Under 3 months, a temperature of 38 °C or higher needs urgent medical advice.'
FEV6='From 3 to 6 months, get urgent advice for 39 °C or higher, or a high temperature with other signs of illness.'

wk(1,'newborn','Hello, little one','These first days are all about feeding, sleeping and getting to know each other.',
 {'sleep':'Expect lots of sleep in short stretches, day and night: 14–17 hours in every 24 for the first 3 months.',
  'eyes':'{She} sees light, shapes and faces, and sees best about 20–30 cm away. That’s about the distance to your face during a feed.',
  'tummy':'Hunger signs: hands to mouth, turning towards the breast or bottle, smacking lips. Breast milk or formula is all {she} needs for now.',
  'care':'Every sleep: on {pos} back, on a firm flat surface, in {pos} own cot in your room, with nothing soft in it.'},
 ['Hold {her} close and talk softly. By one month {she} will know your voice.','Cuddle and hold {her} often. You can’t spoil a baby by holding or responding to them.'],
 [FEV3],['WHO-PA','AAP-VISION','CDC','AAP-SLEEP','NHS-SLEEP','AAP-HEAR','CDC-HELP','NHS-FEVER'])
wk(2,'newborn','Crying is talking','Crying is how {she} tells you something: hungry, tired, too hot, or wanting a cuddle.',
 {'sleep':'Fussing and crying can add up to about 2 hours a day in these early weeks. That’s normal, and it eases after 8–9 weeks.',
  'eyes':'{Pos} eyes may sometimes wander or cross. That’s normal while {she} learns to use both eyes together.',
  'tummy':'You may notice a little milk coming back up during or after feeds. It’s very common and nothing to worry about while {she’s} happy and gaining weight.',
  'care':'Ask your doctor about vitamin D drops: 400 IU a day from soon after birth, breastfed babies included.'},
 ['Try holding, gentle rocking, a walk in the carrier, or soft background noise.','If you need a break, put {her} down safely on {pos} back and step away for a few minutes. That’s okay.'],
 ['A weak or high-pitched cry, or a cry that doesn’t sound like {pos} usual cry, needs urgent help.'],['WOLKE','AAP-VISION','NHS-REFLUX','AAP-VITD','AAP-FUSSY','NHS-COLIC'])
wk(3,'newborn','Talk, read, sing','Talking, reading and singing from day one helps {her} understand language later.',
 {'talk':'{She} loves your voice most of all, especially when it’s a little higher, slower and sing-song.',
  'feel':'You may notice {her} watching your face closely during feeds and cuddles.',
  'tummy':'Signs {she’s} full: closing {pos} mouth or turning {pos} head away. If {she} isn’t hungry, it’s fine to stop.',
  'sleep':'Some days feel fussier than others, and evenings are often the hardest, usually between 6 pm and midnight.'},
 ['Read anything out loud, even your own book.','Sing to {her}, any song you know.'],
 [],['AAP-HEAR','CDC','AAP-FUSSY','AAP-READ','CDC-HELP'])
wk(4,'newborn','Tummy time begins','Short spells of tummy time while {she’s} awake build neck and shoulder strength.',
 {'body':'You may see short head lifts while {she’s} on {pos} tummy, and arms and legs moving a lot.',
  'eyes':'Around now, {she} will focus on your face when you cradle {her}.',
  'talk':'By one month, {she} can pick out your voice, even from another room.',
  'care':'Tummy time is only for awake, watched play. Sleep is always on {pos} back.'},
 ['Lay {her} tummy-down on a play mat for a minute or two, a few times a day, while you watch. Build up to 30 minutes a day in total.','During tummy time, put a toy at eye level in front of {her} to encourage lifting {pos} head.'],
 [FEV3],['CDC','AAP-EYES','AAP-HEAR','AAP-SLEEP','WHO-PA','CDC-HELP','NHS-FEVER'])
wk(5,'newborn','Looking at you','Faces are {pos} favourite thing to look at, and yours is the best of all.',
 {'feel':HL+'see {her} look at your face and calm down when you talk to {her} or pick {her} up, by 2 months.',
  'eyes':'{She} may follow your face a little way, then lose it as it crosses from one side to the other. That’s expected until about 2 months.',
  'mind':'You may notice {her} watching you as you move around the room.',
  'care':'Keep {her} in the same room as you for every sleep, day and night, for at least the first 6 months.'},
 ['Get close, face to face, and make slow, big expressions.','Watch {pos} signals: eye contact and sounds mean “play with me”; turning away, yawning or fussing mean “I need a break”.'],
 [],['CDC','AAP-EYES','NHS-SLEEP','AAP-SLEEP','CDC-HELP'])
wk(6,'smiles','Hello, smiles',HL+'see {pos} first real smiles around now.',
 {'feel':HL+'see {her} smile back when you talk or smile at {her}, by 2 months. {She} may seem happy to see you when you walk up.',
  'eyes':'{She} sees you best about 20–30 cm away. If {pos} eyes wander now and then, that’s normal and usually settles by 2–3 months.',
  'tummy':'You may notice a little milk coming back up after feeds. It usually settles by {pos} first birthday as the muscle at the top of {pos} tummy gets stronger.',
  'body':HL+'see {her} hold {pos} head up during tummy time, by 2 months.',
  'sleep':'Evenings may be fussier for now. Crying runs at about 2 hours a day in the first 6 weeks and eases after 8–9 weeks.'},
 ['Smile and talk, then pause. Give {her} time to answer with a look or a sound.','Put your phone away during play, so you notice and answer {pos} signals.'],
 [],['CDC','AAP-VISION','NHS-REFLUX','WOLKE','CDC-HELP'])
wk(7,'smiles','First sounds','Soft sounds other than crying start to appear.',
 {'talk':HL+'hear sounds other than crying, and see {her} react to loud sounds, by 2 months.',
  'tummy':'Coughing, hiccups or gulping during feeds can be part of reflux. Holding {her} upright during and after feeds, and burping during feeds, can help.',
  'sleep':'Help {her} learn night from day: lights low and voices quiet at night; curtains open and play in the day.'},
 ['Copy {pos} sounds back, like a little conversation.','Talk and play during feeding, dressing and bath time.'],
 ['Green or yellow sick, very forceful (projectile) vomiting, or blood in sick or poo needs an urgent appointment.'],['CDC','NHS-REFLUX','NHS-SLEEP','CDC-HELP'])
wk(8,'smiles','Strong neck','Head control is building fast.',
 {'body':HL+'see {her} hold {pos} head up on {pos} tummy, move both arms and legs, and open {pos} hands briefly, by 2 months.',
  'eyes':'Around 2 months, {she} will start following your face from one side to the other and back again.',
  'care':'Keep naps safe too: on {pos} back, on a firm flat surface.'},
 ['Hold a rattle to one side of {pos} head, shake it, and see if {she} looks for the sound.','Keep up tummy time, a little more each day.'],
 [FEV3],['CDC','AAP-EYES','AAP-SLEEP','CDC-HELP','WHO-PA','NHS-FEVER'])
wk(9,'smiles','2-month check-up','A nice week to jot down questions for {pos} 2-month check-up.',
 {'mind':HL+'see {her} look at a toy for several seconds and watch you as you move, by 2 months.',
  'talk':'You may hear {her} coo, repeating vowel sounds like “ah-ah-ah” and “ooh-ooh-ooh”.',
  'care':'2-month vaccines (Singapore): the 6-in-1 (DTaP-IPV-Hib-HepB), dose 1.'},
 ['When {she’s} upset, stay calm: talk softly, hold, rock or sing.','Look after yourself too. It’s easier to enjoy {her} when you feel okay.'],
 [DOC],['CDC','AAP-HEAR','SG-NCIS','CDC-HELP'])
wk(10,'smiles','Calmer days ahead','Fussing and crying tend to ease from around now.',
 {'sleep':'Crying tends to drop after 8–9 weeks, to about 1 hour a day by 10–12 weeks.',
  'feel':'You may see {her} look at you, move or make sounds to get your attention.',
  'tummy':'If {she} cries a lot but is otherwise well, colic usually stops by 3–4 months. Holding {her} upright during feeds and burping afterwards can help.'},
 ['Short walks outside: point at things and name them.','Notice what {she} reacts to, so you learn what {she} likes and doesn’t like.'],
 [],['WOLKE','CDC','NHS-COLIC','CDC-HELP'])
wk(11,'smiles','Cooing conversations','Coos like “oooo” and “aahh” are coming.',
 {'talk':HL+'hear {her} coo and make sounds back when you talk, by 4 months.',
  'eyes':'{She’s} learning to focus on faces and close objects.',
  'sleep':'Steady routines for sleep and feeds can help the days feel calmer.'},
 ['Talk, wait, and answer each coo. This back-and-forth builds language.','Use {pos} name often so {she} learns it.'],
 [],['CDC','AAP-VISION','CDC-HELP'])
wk(12,'smiles','Following with the eyes','Moving things are fascinating right now.',
 {'eyes':'By 3 months, {she} will follow a moving object with {pos} eyes, and focus on faces and close objects.',
  'sleep':'Crying has usually settled to around an hour a day by now.',
  'care':'No screen time is recommended at this age. Talking and reading are better for {her}.'},
 ['Lay {her} on {pos} back and move a bright toy slowly from side to side, and up and down.','Lay {her} on a blanket with safe toys to reach for and kick at.'],
 [],['AAP-VISION','WOLKE','WHO-PA','CDC-HELP'])
wk(13,'smiles','Smiling to get your attention','{She’s} starting conversations now, not just answering.',
 {'feel':HL+'see {her} smile on {pos} own to get your attention, and chuckle when you play, by 4 months.',
  'mind':'You may notice {her} looking at {pos} hands with interest.',
  'care':'Naps count too: always on {pos} back, flat and firm.'},
 ['Play simple face games and see what makes {her} chuckle.','Play peek-a-boo: cover your eyes, uncover them and say “peek-a-boo!”'],
 [],['CDC','AAP-SLEEP','CDC-HELP'])
wk(14,'grab','Reaching out','Hands are getting busy.',
 {'body':HL+'see {her} hold a toy you put in {pos} hand and swing at toys, by 4 months.',
  'eyes':'{Pos} colour vision is getting better, and round shapes like faces, spirals and bull’s-eyes are extra interesting.',
  'care':'Try not to keep {her} in a swing, bouncer or pram for more than 1 hour at a time.'},
 ['Hang or hold a toy within reach so {she} can bat at it.','Give easy-to-hold toys, like a rattle or a cloth book.'],
 [],['CDC','AAP-VISION','WHO-PA','CDC-HELP'])
wk(15,'grab','Hands to mouth','Exploring with the mouth is how {she} learns.',
 {'body':HL+'see {her} bring {pos} hands to {pos} mouth, by 4 months.',
  'talk':'{She’s} more tuned in to your tone of voice now. An upbeat voice may get a smile or a coo.',
  'care':'Offer safe things to mouth: nothing sharp, hot, or small enough to choke on.'},
 ['Sing while you gently move {pos} arms and legs, a little baby workout.','Copy {pos} sounds and see how long you can keep the back-and-forth going.'],
 [],['CDC','AAP-HEAR','CDC-HELP'])
wk(16,'grab','Mini push-ups','Tummy time is turning into mini push-ups.',
 {'body':HL+'see {her} push up onto {pos} elbows on {pos} tummy, and hold {pos} head steady when you hold {her}, by 4 months.',
  'talk':'You may hear lots of babbling, like “muh-muh” and “bah-bah”.',
  'sleep':'From 4 months, 12–16 hours of sleep in 24, naps included, is a healthy amount.'},
 ['Get down on the floor at eye level during tummy time.','Hold {her} under the arms with {pos} feet on your lap and let {her} bounce.'],
 [FEV6],['CDC','AAP-HEAR','WHO-PA','CDC-HELP','NHS-FEVER'])
wk(17,'grab','4-month check-up','A nice week to note questions for {pos} 4-month check-up.',
 {'mind':HL+'see {her} open {pos} mouth at the breast or bottle when hungry, by 4 months.',
  'eyes':HL+'see {her} turn {pos} head towards your voice, by 4 months.',
  'care':'4-month vaccines (Singapore): DTaP-IPV-Hib dose 2 and pneumococcal (PCV) dose 1.'},
 ['Make time for floor play several times a day.','Share a picture book: point at the pictures and name them.'],
 [DOC,'If colic-like crying carries on after 4 months, mention it to your doctor.'],['CDC','SG-NCIS','WHO-PA','AAP-READ','NHS-COLIC'])
wk(18,'grab','Laughing together','Real laughs are on the way.',
 {'feel':HL+'hear {her} laugh, and see {her} know familiar people, by 6 months.',
  'tummy':'Breast milk or formula is still all {she} needs. Chewing fists, waking more at night or wanting extra feeds don’t mean {she’s} ready for solids.'},
 ['Find the games that make {her} laugh, and repeat them.','Back-and-forth play: when {she} smiles, smile back; when {she} makes sounds, copy them.'],
 [],['CDC','NHS-SOLIDS','CDC-HELP'])
wk(19,'grab','Teething may start','First teeth can come any time in the first year, often around 6 months.',
 {'body':'Signs of teething: sore red gums, more dribbling, chewing on things, one flushed cheek, rubbing an ear, fussier sleep.',
  'care':'Teething can raise {pos} temperature slightly, but not to 38 °C. There’s no evidence it causes diarrhoea.'},
 ['Note teething signs in Goldfox so you can spot a pattern.','Share a book every day: reading together builds language and closeness.'],
 [FEV6],['NHS-TEETH','NHS-FEVER','AAP-READ'])
wk(20,'grab','Raspberries and squeals','{She’s} playing with sounds.',
 {'talk':HL+'hear {her} take turns making sounds with you, blow raspberries and squeal, by 6 months.',
  'care':'Reading together every day supports language and closeness.'},
 ['Blow raspberries back and take turns.','“Read” by talking about colourful pictures, and answer {pos} babble: “Yes, that’s the doggy!”'],
 [],['CDC','AAP-READ','CDC-HELP'])
wk(21,'grab','Grab and explore','Reaching is getting accurate.',
 {'mind':HL+'see {her} reach for a toy {she} wants, and put things in {pos} mouth to explore, by 6 months.',
  'eyes':'{Pos} eye colour may still be changing. It can keep shifting until about {pos} first birthday.',
  'care':'Check toys aren’t small enough to choke on.'},
 ['Put toys just out of reach to encourage rolling and reaching.','When {she} looks at something, point to it and talk about it.'],
 [],['CDC','AAP-EYES','CDC-HELP'])
wk(22,'sit','Rolling over','Rolling opens up a new way to move.',
 {'body':HL+'see {her} roll from tummy to back, by 6 months. Sitting without support can come any time from about 4 to 9 months.'},
 ['Give lots of floor play, several times a day.','Hold {her} sitting up with toys to look at while {she} learns to balance.'],
 [FEV6],['CDC','WHO-MM','WHO-PA','CDC-HELP','NHS-FEVER'])
wk(23,'sit','Mirror, mirror','{She’s} getting curious about faces, including {pos} own.',
 {'feel':HL+'see {her} enjoy looking in a mirror, by 6 months.',
  'eyes':'By 6 months, {she} can tell objects apart by how they look.',
  'body':'Standing with your help can start any time from about 5 to 11 months.'},
 ['Sit together in front of a mirror and name body parts.','Try whispers, claps and funny noises, and see which ones {she} likes.'],
 [],['CDC','AAP-VISION','WHO-MM','CDC-HELP'])
wk(24,'sit','Getting ready for food','First foods come at around 6 months, not before.',
 {'body':HL+'see {her} push up on straight arms on {pos} tummy, and lean on {pos} hands when sitting, by 6 months.',
  'tummy':'Signs {she’s} ready for food: sitting up with a steady head, picking food up and bringing it to {pos} mouth, and swallowing food rather than spitting it out.',
  'care':'Ask your doctor about starting solids, especially if {she} was born early.'},
 ['Let {her} sit with you at family meals to see how eating works.','Hold {her} under the arms to stand, look around together and name what you see.'],
 [],['CDC','NHS-SOLIDS','CDC-HELP'])
wk(25,'sit','Hungry or full?','Learning {pos} food signals makes mealtimes easier.',
 {'tummy':'Hungry: opening {pos} mouth for the spoon, getting excited about food. Full: pushing food away, closing {pos} mouth, turning away.',
  'care':'Peanut foods given in infancy can help prevent peanut allergy. If {she} has eczema or a food allergy, ask your doctor first.'},
 ['Follow {pos} lead. Getting used to eating matters more than how much.','When {she} drops a toy, pick it up and give it back. This game teaches cause and effect.'],
 [],['CDC','NHS-SOLIDS','NIAID-PEANUT','CDC-HELP'])
wk(26,'sit','Half a year!','Six months: first foods, new vaccines and lots of new sounds.',
 {'mind':HL+'see {her} close {pos} lips to show {she} doesn’t want more food, by 6 months.',
  'eyes':'By now {pos} eyes should stay lined up together, even if one is briefly covered.',
  'tummy':'Start with small amounts alongside breast milk or formula.',
  'care':'6-month vaccines (Singapore): 6-in-1 dose 3 and PCV dose 2. A flu vaccine is recommended every year from 6 months to under 5 years.'},
 ['Sing to {her} and play music.','Read {pos} mood: if {she’s} happy, keep going; if {she’s} upset, take a break and comfort {her}.'],
 [DOC,'From 6 months, if one eye doesn’t always look the same way as the other, tell {pos} doctor.'],['CDC','AAP-EYES','NHS-SOLIDS','SG-NCIS','CDC-HELP'])
wk(27,'sit','First tastes','Variety from the start helps later eating.',
 {'tummy':'Breast milk or formula still gives {her} most of {pos} energy. Offer vegetables, including less sweet ones, not just carrot and sweet potato.',
  'body':'Front teeth are usually the first to come through, around 6 months.',
  'care':'No added salt or sugar, including stock cubes and gravy. Cows’ milk can go in food, but not as a main drink until 1 year.'},
 ['Let {her} touch, hold and squish food. It’s all learning.','Keep mealtimes calm, with no TV, phone or tablet at the table.'],
 ['Reflux that starts for the first time after 6 months is worth a visit to your doctor.'],['NHS-SOLIDS','NHS-TEETH','NHS-REFLUX'])
wk(28,'sit','Naming the world','{She’s} starting to link words with things.',
 {'feel':HL+'see {her} look when you call {pos} name, by 9 months.',
  'tummy':'Egg, peanut, gluten and fish can be offered from around 6 months, one at a time, so you can spot any reaction.'},
 ['On walks, point at cars, trees and animals and name them.','Repeat {pos} sounds and add a word: “bababa… book!”'],
 [],['CDC','NHS-SOLIDS','CDC-HELP'])
wk(29,'sit','Safe finger foods','Food safety matters as textures get bigger.',
 {'tummy':'Gagging, with watery eyes, tongue pushed forward and retching, is part of learning to eat. If {she} prefers smooth food for now, keep offering lumpier textures and {she} will get used to them.',
  'care':'Avoid whole nuts and hard foods like raw carrot or apple. Cut small round foods like grapes into quarters.'},
 ['Try soft finger foods {she} can pick up.','Stay close while {she} explores, so {she} knows you’re near.'],
 [],['NHS-SOLIDS','CDC-HELP'])
wk(30,'crawl','Peekaboo!','Hiding and finding games are a hit.',
 {'feel':HL+'see {her} smile or laugh when you play peekaboo, by 9 months.',
  'mind':'{She’s} learning that things still exist when they’re out of sight.',
  'body':'Standing alone can come any time from about 7 to 17 months.'},
 ['Play peekaboo with a cloth over your head and see if {she} pulls it off.','Hide behind a door and leave a foot in view as a clue.'],
 [],['CDC','AAP-COG','WHO-MM','CDC-HELP'])
wk(31,'crawl','Mama-ma, ba-ba-ba','Babbling chains are coming.',
 {'talk':HL+'hear lots of different sounds like “mamamama” and “babababa”, by 9 months.',
  'body':'The teeth either side of the front ones usually follow, around 8 months.'},
 ['Babble back and add the real word: “ba-ba… yes, ball!”','Keep reading every day and let {her} touch the pages.'],
 [],['CDC','NHS-TEETH','AAP-READ','CDC-HELP'])
wk(32,'crawl','Bang, bang!','Making noise is how {she} experiments.',
 {'mind':HL+'see {her} bang two things together, by 9 months. Two or three minutes with one toy is plenty right now.',
  'body':HL+'see {her} pass things from one hand to the other, by 9 months.',
  'care':'Keep anything small enough to choke on out of reach.'},
 ['Dump blocks out of a container and put them back in together.','Give pots, pans or a small drum and let {her} make noise.'],
 [],['CDC','AAP-COG','CDC-HELP'])
wk(33,'crawl','A little shy','Shyness with new people is a sign of {pos} bond with you.',
 {'feel':HL+'see {her} get shy or clingy around strangers, and react when you leave, by 9 months. It shows how much {she} trusts you.'},
 ['Let {her} warm up to new people from your lap.','Say a quick, cheerful goodbye instead of sneaking away, and say hello when you’re back.'],
 [],['CDC','CDC-HELP'])
wk(34,'crawl','Where did it go?','{She} knows things still exist when they’re out of sight.',
 {'mind':HL+'see {her} look for things dropped out of sight, like a spoon or a toy, by 9 months.',
  'care':'Screen time still isn’t recommended under 1 year. Reading and storytelling are better.'},
 ['Hide a toy under a cloth while {she} watches, then let {her} find it.','Play “my turn, your turn” by passing a toy back and forth.'],
 [],['CDC','AAP-COG','WHO-PA','AAP-MEDIA','CDC-HELP'])
wk(35,'crawl','On the move','Crawling can start any time from about 5 to 13½ months, and skipping it is fine too.',
 {'body':HL+'see {her} sit without support, by 9 months. If {she} goes straight from sitting to standing without crawling, that’s fine.',
  'care':'Clear a safe floor space, and move sharp or breakable things out of reach.'},
 ['Put toys a little out of reach and cheer when {she} gets there by crawling, scooting or rolling.','Teach waving bye-bye and simple baby signs, so {she} can tell you what {she} wants.'],
 [],['CDC','WHO-MM','CDC-HELP'])
wk(36,'crawl','Little self-feeder','Messy eating is learning.',
 {'body':HL+'see {her} “rake” food towards {her} with {pos} fingers, by 9 months. Walking alone can come any time from about 8 to 18 months, so there’s no rush.',
  'tummy':'Let {her} practise finger foods and sips from an open cup. Expect spills.'},
 ['Sit and eat together. {She} learns by watching you.','Point to pictures in books and name them.'],
 [],['CDC','WHO-MM','NHS-SOLIDS','CDC-HELP'])
wk(37,'crawl','Pick me up!','{She} can ask with gestures now.',
 {'talk':HL+'see {her} lift {pos} arms to be picked up, by 9 months.',
  'feel':HL+'see several expressions, like happy, sad, angry and surprised, by 9 months.',
  'tummy':'Keep offering new tastes and textures. It can take many tries before a food is liked.'},
 ['Name feelings as you see them: “You look surprised!”','When {she} reaches or points, answer with words: “Up? Here we go!”'],
 [],['CDC','NHS-SOLIDS','CDC-HELP'])
wk(38,'crawl','Sitting up solo','New positions, new views.',
 {'body':HL+'see {her} get into a sitting position on {pos} own, by 9 months.',
  'mind':'{She} loves dropping, rolling and throwing things to see what happens. It’s how {she} learns how the world works.'},
 ['Say what you’d like {her} to do: “time to sit” rather than “don’t stand”.','Everyday things make great toys: wooden spoons, egg boxes, plastic tubs.'],
 [],['CDC','AAP-COG','CDC-HELP'])
wk(39,'stand','9-month check-up','A nice week to note questions for {pos} 9-month check-up. A general development check is recommended around now.',
 {'feel':HL+'see {her} react when you leave the room, by looking, reaching for you or crying, by 9 months.',
  'care':'Ask about the 9-month developmental screening at {pos} visit.'},
 ['Keep up daily floor play, reading and songs.','Stay close while {she} explores, so {she} knows you’re near.'],
 [DOC],['CDC','WHO-PA','AAP-READ','CDC-HELP'])
wk(40,'stand','Bye-bye!','Gestures are words before words.',
 {'talk':HL+'see {her} wave bye-bye, by 12 months.',
  'mind':'{She} will keep searching for a hidden toy, sure it’s still there somewhere.',
  'tummy':'Keep offering foods {she} turned down before. Tastes change.'},
 ['Wave hello and bye-bye to people, pets and even the bathwater.','Talk or sing about what you’re doing: “This is the way we wash our hands.”'],
 [],['CDC','AAP-COG','NHS-SOLIDS','CDC-HELP'])
wk(41,'stand','Understanding “no”','{She} understands more than {she} can say.',
 {'talk':HL+'see {her} understand “no”, pausing or stopping when you say it, by 12 months.',
  'care':'Try not to keep {her} strapped in (pram, high chair, carrier) for more than 1 hour at a time.'},
 ['Use short, clear words, and show what to do instead.','Show the behaviour you want and praise it with words and hugs.'],
 [],['CDC','WHO-PA','CDC-HELP'])
wk(42,'stand','Pulling up','Furniture becomes a climbing frame.',
 {'body':HL+'see {her} pull up to stand, by 12 months.',
  'mind':'{Pos} attention span is growing. By 12 months {she} may stay with one toy for up to 15 minutes.',
  'care':'Check that what {she} pulls up on is stable.'},
 ['Place toys along the sofa to encourage cruising.','Play together with blocks and other toys that get little hands working.'],
 [],['CDC','AAP-COG','CDC-HELP'])
wk(43,'stand','Cruising','First steps, holding on.',
 {'body':HL+'see {her} walk holding on to furniture, by 12 months. Walking with your help can start any time from about 6 to 14 months.',
  'care':'Being active several times a day is good for {her}; more is better.'},
 ['Point out interesting things you see, like a bus, a bird or a dog.','Share books with flaps to lift or things to touch.'],
 [],['CDC','WHO-MM','WHO-PA','CDC-HELP'])
wk(44,'stand','Pincer grasp','Tiny fingers, tiny bits.',
 {'body':HL+'see {her} pick things up between thumb and pointer finger, like small bits of food, by 12 months.',
  'care':'Cut small round foods like grapes and cherry tomatoes into quarters.'},
 ['Offer soft, small finger foods to practise.','Hand {her} a hairbrush, cup or spoon and watch {her} copy you.'],
 [],['CDC','NHS-SOLIDS','AAP-COG'])
wk(45,'stand','Mama or dada','A special name for you is coming.',
 {'talk':HL+'hear {her} call you “mama”, “dada” or another special name, by 12 months.',
  'mind':'{She} may start using things the way you do, like holding a toy phone to {pos} ear.'},
 ['Build on what {she} says: if {she} says “ta”, say “Yes, a truck!”','Talk through everyday tasks. Every word counts.'],
 [],['CDC','AAP-COG','CDC-HELP'])
wk(46,'stand','In and out','Putting things in containers is a big thinking step.',
 {'mind':HL+'see {her} put something in a container, like a block in a cup, by 12 months.',
  'care':'Floor play several times a day is how {she} practises new skills.'},
 ['Play “in and out” with blocks and a box.','With a new caregiver, give {her} time to get to know them, and bring a favourite toy or blanket.'],
 [],['CDC','WHO-PA','CDC-HELP'])
wk(47,'stand','Hide and seek','{She} remembers where things went.',
 {'mind':HL+'see {her} look for things {she} saw you hide, like a toy under a blanket, by 12 months.',
  'body':'The first back teeth (molars) usually come through around 12 months.'},
 ['Hide a toy under one of two cups and let {her} find it.','Let {her} choose the bedtime book.'],
 [],['CDC','NHS-TEETH','AAP-READ','CDC-HELP'])
wk(48,'stand','Baby-proofing, round two','A busier explorer needs a safer home.',
 {'mind':'{She} may empty drawers and bins to see what’s inside. That’s curiosity at work, so add safety locks where needed.',
  'care':'Move sharp or breakable things out of reach, and lock away medicines, chemicals and cleaning products. Save your local poison or emergency number in your phone.'},
 ['Get down to {pos} height and look for hazards.','Show {her} how to stroke a soft toy or a pet gently, and praise {her} when {she} does.'],
 [],['AAP-COG','CDC','CDC-HELP'])
wk(49,'stand','Cup practice','Drinking skills are developing.',
 {'body':HL+'see {her} drink from an open cup while you hold it, by 12 months.',
  'tummy':'Drinks: water, breast milk or formula. No sugary drinks; juice isn’t needed.'},
 ['Offer water in an open cup with meals.','Let {her} hold a spoon of {pos} own at mealtimes.'],
 [],['CDC','NHS-SOLIDS'])
wk(50,'stand','Pat-a-cake','Games with rhythm and rules.',
 {'feel':HL+'see {her} play games with you, like pat-a-cake, by 12 months.',
  'care':'Screen time still isn’t recommended. Shared reading, songs and play are best.'},
 ['Sing action songs and pause before the clap so {she} can join in.','Read together every day, and let {her} turn the pages.'],
 [],['CDC','WHO-PA','AAP-MEDIA','AAP-READ','CDC-HELP'])
wk(51,'stand','Sleep before one','{Pos} sleep pattern is {pos} own. Up to 12 months, 12–16 hours a day, naps included, is a healthy amount.',
 {'sleep':'From 1 to 2 years, 11–14 hours a day is a healthy amount.'},
 ['Keep the bedtime routine the same each night: bath, book, song.','Bedtime routines are lovely one-to-one time together.'],
 [],['WHO-PA','NHS-SLEEP'])
wk(52,'stand','Happy first birthday!','One year! Look back at how far {she’s} come.',
 {'body':HL+'see {her} pull up to stand and cruise along furniture by now. Walking alone can come any time up to about 18 months.',
  'talk':HL+'see {her} wave bye-bye and understand “no” by now.',
  'eyes':'{Pos} eye colour has mostly settled by now.',
  'care':'12-month vaccines (Singapore): MMR dose 1, chickenpox (varicella) dose 1 and the PCV booster. Cows’ milk can now be a main drink.'},
 ['Celebrate with {pos} favourite song and a photo for Moments.','Look back at photos from week 1 together.'],
 [DOC],['CDC','WHO-MM','AAP-EYES','SG-NCIS','NHS-SOLIDS'])

# fix up apostrophes inside tokens written with a curly quote
import re as _re
def _fix(s):return s.replace('{she’s}',"{she's}").replace('{She’s}',"{She's}")
for x in W:
    x['title']=_fix(x['title']);x['head']=_fix(x['head']);x['t']=[[k,_fix(v)] for k,v in x['t']];x['play']=[_fix(p) for p in x['play']];x['watch']=[_fix(p) for p in x['watch']]
# checks: every week, every source, no comparisons, only known tokens
BAN=_re.compile(r'\b(most|many|some) (babies|children|kids)\b|\btypical\b|\bnormal range\b|\baverage\b',_re.I)
OKTOK={'{she}','{She}','{her}','{pos}','{Pos}',"{she's}","{She's}"}
assert len(W)==52 and [x['w'] for x in W]==list(range(1,53))
for x in W:
    for s in x['src']:assert s in SOURCES,(x['w'],s)
    txts=[x['title'],x['head']]+[v for k,v in x['t']]+x['play']+x['watch']
    for s in txts:
        assert not BAN.search(s),(x['w'],s)
        for tok in _re.findall(r'\{[^}]*\}',s):assert tok in OKTOK,(x['w'],tok)
    assert 2<=len(x['play'])<=3 and len(x['t'])>=1,x['w']
json.dump({'v':2,'sources':{k:{'name':v['name'],'url':v['url']} for k,v in SOURCES.items()},'weeks':W},open(OUT_JSON,'w'),ensure_ascii=False,separators=(',',':'))
L=['# Goldfox week-by-week guide: sources','','Every line in `weeks.json` names the sources it comes from (`src`). Each source below was read and checked',
   'in November 2026. Only these sources are used; nothing is taken from general memory.','',
   '## How it is written','',
   '- It talks to you about your own baby. No "most babies", "many babies", "typical" or other comparisons with other children.',
   '- "It\'s highly likely you\'ll see…" is used only for CDC milestones, which at least 3 in 4 children reach by that age.',
   '  Things that vary more say "you may…", or give the full healthy age range (WHO motor windows).',
   '- No checklists or scores: nothing to pass or fail.',
   '- The doctor box appears only for real warning signs (fever under 6 months, urgent crying or vomiting signs, eye alignment',
   '  from 6 months, colic after 4 months) and at the check-up weeks.','',
   'Deliberately left out: "Wonder Weeks" / predictable developmental leaps. The idea comes from small studies, and attempts to',
   'replicate it have been mixed and disputed. So leaps are not presented as fact.','',
   'Also note: the widely repeated "crying peaks at 6 weeks" is not supported by the largest meta-analysis (Wolke 2017); the guide',
   'says crying stays around 2 hours a day for the first 6 weeks and falls after 8-9 weeks instead.','','## Sources','']
for k,v in SOURCES.items():
    L+=['### '+k,'- '+v['name'],'- '+v['url'],'- Key facts used: '+v['note'],'']
L+=['## Where each source is used','']
use={}
for x in W:
    for s in x['src']:use.setdefault(s,[]).append(x['w'])
for k in SOURCES:L.append('- '+k+': weeks '+(', '.join(map(str,use[k])) if k in use else '(none this version)'))
L+=['','## To check before relying on vaccine timing','- The Singapore schedule here is the version effective 1 Nov 2020. MOH published an update dated 1 Apr 2026; confirm dose ages against it.','']
open(OUT_MD,'w').write('\n'.join(L))
print('weeks',len(W),'sources',len(SOURCES),'topics',sum(len(x['t']) for x in W))
