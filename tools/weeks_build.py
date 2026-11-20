# Run: python3 tools/weeks_build.py weeks.json docs/week-guide-sources.md
"""Goldfox week-by-week guide, weeks 1-52. Every line is tied to a source id in SOURCES (checked against the source text
in Nov 2026). Writes weeks.json (for the app) and the sources document (for future reference)."""
import json,sys
OUT_JSON=sys.argv[1];OUT_MD=sys.argv[2]

SOURCES={
 'CDC':{'name':'CDC "Learn the Signs. Act Early." milestone checklists (2021 revision): 2, 4, 6, 9 and 12 months, incl. parent tips',
  'url':'https://www.cdc.gov/wic-guide/media/pdfs/FULL-LIST-CDC_LTSAE-Checklists2021_Eng_FNL2_508.pdf',
  'note':'Milestones that MOST children (at least 75%) are expected to meet by each age. Not a screening tool.'},
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

# stage colour/illustration key: newborn, smiles, grab, sit, crawl, stand
W=[]
def wk(n,stage,title,head,notice,tryit,care,watch,src):W.append(dict(w=n,stage=stage,title=title,head=head,notice=notice,tryit=tryit,care=care,watch=watch,src=src))
M2='By 2 months, most babies (3 in 4)';M4='By 4 months, most babies';M6='By 6 months, most babies';M9='By 9 months, most babies';M12='By 12 months, most babies'
DOC='If your baby misses several milestones, loses a skill they had, or you are worried, talk to your doctor and ask about developmental screening.'
FEV3='Under 3 months, a temperature of 38 °C or higher needs urgent medical advice.'
FEV6='From 3 to 6 months, get urgent advice for 39 °C or higher, or a high temperature with other signs of illness.'

wk(1,'newborn','Hello, little one','Your baby sleeps most of the day and night: 14–17 hours in 24 hours is typical for the first 3 months.',
 ['Sleep comes in short stretches, day and night.','Feeding signs: hands to mouth, turning towards the breast or bottle, smacking lips.'],
 ['Hold your baby close and talk softly.'],
 ['Feed only breast milk or formula; babies need no water or other drinks for about the first 6 months.','Every sleep: on the back, on a firm flat surface, in their own space in your room, with nothing soft in it.'],
 [FEV3],['WHO-PA','CDC','AAP-SLEEP','NHS-FEVER'])
wk(2,'newborn','Crying is talking','Fussing and crying add up to about 2 hours a day on average in the first 6 weeks. That is normal.',
 ['Crying is how your baby tells you they are hungry, tired, too hot or need a cuddle.','Some days are much fussier than others.'],
 ['Try holding, gentle rocking or a walk; take a break if you need one (put baby down safely first).'],
 ['Ask your doctor about vitamin D drops: all babies need 400 IU a day from soon after birth, including breastfed babies.'],
 [],['WOLKE','AAP-VITD','CDC'])
wk(3,'newborn','Talk, read, sing','Talking, reading and singing to your baby from day one helps them understand language later.',
 ['Your baby listens to your voice and watches your face.','Feeding signs of being full: closing the mouth or turning the head away.'],
 ['Read anything out loud, even your own book.','Sing to your baby.'],
 ['If your baby isn’t hungry, it’s fine to stop feeding.'],
 [],['CDC','AAP-READ'])
wk(4,'newborn','Tummy time begins','Short tummy-time spells while awake build neck and shoulder strength. Work up to 30 minutes a day, spread out.',
 ['Short lifts of the head while on the tummy.','Arms and legs moving a lot.'],
 ['Lay your baby tummy-down on your chest or a play mat for a minute or two, several times a day, while you watch.'],
 ['Tummy time is for awake, watched play only; sleep is always on the back.'],
 [FEV3],['WHO-PA','AAP-SLEEP','NHS-FEVER'])
wk(5,'newborn','Looking at you','Faces are your baby’s favourite thing to look at.',
 [M2+' look at your face and calm down when spoken to or picked up.','Your baby may watch you as you move around.'],
 ['Get close, face to face, and make slow, big expressions.'],
 ['Keep your baby in the same room as you for sleep for at least the first 6 months, in their own cot.'],
 [],['CDC','NHS-SLEEP','AAP-SLEEP'])
wk(6,'smiles','First real smiles','Many babies start smiling back at you around now.',
 [M2+' smile when you talk to or smile at them.','Your baby may seem happy to see you when you walk up.'],
 ['Smile and talk, then pause: give your baby time to answer with a look or a sound.'],
 ['Crying still runs at about 2 hours a day for many babies; it usually eases after 8–9 weeks.'],
 [],['CDC','WOLKE'])
wk(7,'smiles','First sounds','Soft sounds other than crying start to appear.',
 [M2+' make sounds other than crying and react to loud sounds.'],
 ['Copy your baby’s sounds back to them, like a little conversation.'],
 ['At night keep lights low and voices quiet; in the day open curtains and play. Babies slowly learn night is for sleep.'],
 [],['CDC','NHS-SLEEP'])
wk(8,'smiles','Strong neck','Head control is building fast.',
 [M2+' hold their head up when on the tummy, move both arms and both legs, and open their hands briefly.'],
 ['Keep up tummy time, a little more each day.'],
 ['First vaccines are due at 2 months (Singapore: 6-in-1, which includes hepatitis B dose 2).'],
 [FEV3],['CDC','SG-NCIS','NHS-FEVER'])
wk(9,'smiles','2-month check-in','Time to look back at the 2-month milestones and bring questions to your baby’s check-up.',
 [M2+' look at a toy for several seconds and watch you as you move.'],
 ['Take care of yourself too: parenting is hard work, and it is easier to enjoy your baby when you feel okay.'],
 ['2-month vaccines: 6-in-1 (DTaP-IPV-Hib-HepB) dose 1.'],
 [DOC],['CDC','SG-NCIS'])
wk(10,'smiles','Calmer days ahead','For most babies, fussing and crying start to drop after 8–9 weeks.',
 ['Longer awake times with more looking around.'],
 ['Short walks outside: name what you see.'],
 ['Colic (long bouts of crying) becomes much less common after 9 weeks.'],
 [],['WOLKE','CDC'])
wk(11,'smiles','Cooing conversations','Coos like “oooo” and “aahh” are coming.',
 [M4+' coo and make sounds back when you talk.'],
 ['Talk, wait, and answer each coo; this back-and-forth builds language.'],
 ['Set steady routines for sleeping and feeding.'],
 [],['CDC'])
wk(12,'smiles','Following with the eyes','Your baby tracks things that move.',
 ['Crying is now about 1 hour a day on average (10–12 weeks).'],
 ['Lay your baby on their back and move a bright toy slowly left to right and up and down.'],
 ['Babies need no screen time at this age; talking and reading are better.'],
 [],['WOLKE','CDC','WHO-PA'])
wk(13,'smiles','Smiling to get your attention','Your baby starts to start the conversation.',
 [M4+' smile on their own to get your attention and chuckle (not yet a full laugh).'],
 ['Play simple face games; see what makes your baby chuckle.'],
 ['Keep sleep safe at naps too: on the back, flat and firm.'],
 [],['CDC','AAP-SLEEP'])
wk(14,'grab','Reaching out','Hands are getting busy.',
 [M4+' hold a toy you put in their hand and swing their arm at toys.'],
 ['Hang or hold a toy within reach so your baby can bat at it.'],
 ['Don’t keep your baby in swings, bouncers or strollers for too long: no more than 1 hour at a time.'],
 [],['CDC','WHO-PA'])
wk(15,'grab','Hands to mouth','Exploring with the mouth is how babies learn.',
 [M4+' bring their hands to their mouth and look at their hands with interest.'],
 ['Offer safe things to mouth: nothing sharp, hot or small enough to choke on.'],
 ['Putting things in the mouth is how babies learn.'],
 [],['CDC'])
wk(16,'grab','Push-ups','Tummy time is turning into mini push-ups.',
 [M4+' push up onto their elbows or forearms on the tummy and hold their head steady when you hold them.'],
 ['Get down on the floor at eye level during tummy time.'],
 ['From 4 months, 12–16 hours of sleep in 24 hours (including naps) is typical.'],
 [FEV6],['CDC','WHO-PA','NHS-FEVER'])
wk(17,'grab','4-month check-in','A good week to review the 4-month milestones.',
 [M4+' open their mouth when they see the breast or bottle if hungry, and turn their head towards your voice.'],
 ['Make time for floor play several times a day.'],
 ['4-month vaccines (Singapore): DTaP-IPV-Hib dose 2 and pneumococcal (PCV) dose 1.'],
 [DOC],['CDC','SG-NCIS','WHO-PA'])
wk(18,'grab','Laughing together','Real laughs are on the way.',
 [M6+' know familiar people and laugh.'],
 ['Find the games that make your baby laugh and repeat them.'],
 ['Breast milk or formula is still all your baby needs to eat or drink.'],
 [],['CDC'])
wk(19,'grab','Teething may start','Most babies start teething around 6 months, but some start before 4 months and some after 12 months.',
 ['Possible signs: sore red gums, more dribbling, chewing on things, a flushed cheek, fussier sleep.'],
 ['Note teething signs in Goldfox so you can spot a pattern.'],
 ['Teething can raise the temperature slightly, but not to 38 °C. There is no evidence teething causes diarrhoea.'],
 [FEV6],['NHS-TEETH','NHS-FEVER'])
wk(20,'grab','Raspberries and squeals','Your baby plays with sounds.',
 [M6+' take turns making sounds with you, blow raspberries and squeal.'],
 ['Blow raspberries back and take turns. Share a picture book and name what you see.'],
 ['Reading together every day supports language and bonding.'],
 [],['CDC','AAP-READ'])
wk(21,'grab','Grab and explore','Reaching is getting accurate.',
 [M6+' reach to grab a toy they want and put things in their mouth to explore.'],
 ['Put toys just out of reach, on the tummy or back, to encourage rolling and reaching.'],
 ['Check toys aren’t small enough to choke on.'],
 [],['CDC'])
wk(22,'sit','Rolling over','Rolling opens up a new way to move.',
 [M6+' roll from tummy to back.'],
 ['Give lots of floor play several times a day.'],
 ['The healthy age range for sitting without support starts around 3.8 months and runs to 9.2 months.'],
 [FEV6],['CDC','WHO-MM','WHO-PA','NHS-FEVER'])
wk(23,'sit','Mirror, mirror','Your baby is becoming interested in faces, including their own.',
 [M6+' like to look at themselves in a mirror.'],
 ['Sit together in front of a mirror and name body parts.'],
 ['Some babies start standing with help from about 4.8 months; the normal range runs to 11.4 months.'],
 [],['CDC','WHO-MM'])
wk(24,'sit','Getting ready for food','Solids usually start around 6 months, not before.',
 [M6+' push up with straight arms on the tummy and lean on their hands when sitting.'],
 ['Let your baby sit with you at family meals to watch how eating works.'],
 ['Talk to your doctor about when to start solids and which foods are choking risks. If your baby was premature, ask for specific advice.'],
 [],['CDC','NHS-SOLIDS'])
wk(25,'sit','Hungry or full?','Learning your baby’s food signals makes mealtimes easier.',
 ['Hungry: opening the mouth for a spoon, getting excited about food. Full: pushing food away, closing the mouth, turning away.'],
 ['Follow your baby’s lead; how much they eat at first matters less than getting used to eating.'],
 ['Introducing peanut-containing foods in infancy can help prevent peanut allergy. If your baby has eczema or a food allergy, ask your doctor first.'],
 [],['CDC','NHS-SOLIDS','NIAID-PEANUT'])
wk(26,'sit','Half a year!','Six months: first foods, new vaccines and lots of sounds.',
 [M6+' close their lips to show they don’t want more food.'],
 ['Start with small amounts alongside breast milk or formula; getting used to eating matters more than how much.'],
 ['6-month vaccines (Singapore): 6-in-1 dose 3 and PCV dose 2. The flu vaccine is recommended every year from 6 months to under 5 years.'],
 [DOC],['CDC','SG-NCIS','NHS-SOLIDS'])
wk(27,'sit','First tastes','Variety from the start helps later eating.',
 ['Most energy still comes from breast milk or formula.'],
 ['Offer vegetables, including less sweet ones, not just carrot and sweet potato.'],
 ['No added salt or sugar (including stock cubes and gravy). Cows’ milk can go in food, but not as a main drink until 1 year.'],
 [],['NHS-SOLIDS'])
wk(28,'sit','Naming the world','Your baby is starting to link words with things.',
 [M9+' look when you call their name.'],
 ['On walks, point at cars, trees and animals and name them.'],
 ['Allergens like egg, peanut, gluten and fish can be offered from around 6 months, one at a time, so you can spot any reaction.'],
 [],['CDC','NHS-SOLIDS'])
wk(29,'sit','Safe finger foods','Food safety matters as textures get bigger.',
 ['Gagging (watery eyes, tongue pushed forward, retching) is part of learning to eat.'],
 ['Try soft finger foods your baby can pick up.'],
 ['Avoid whole nuts and hard foods like raw carrot or apple. Cut small round foods like grapes into quarters.'],
 [],['NHS-SOLIDS','CDC'])
wk(30,'crawl','Peekaboo!','Games of hiding and finding are a hit.',
 [M9+' smile or laugh when you play peekaboo.'],
 ['Play peekaboo with your hands or a cloth.'],
 ['Some babies stand alone from about 6.9 months; the normal range runs to 16.9 months.'],
 [],['CDC','WHO-MM'])
wk(31,'crawl','Mama-ma, ba-ba-ba','Babbling chains are coming.',
 [M9+' make sounds like “mamamama” and “babababa”.'],
 ['Babble back and add the real word: “ba-ba… yes, ball!”'],
 ['Keep reading every day; let your baby touch the pages.'],
 [],['CDC','AAP-READ'])
wk(32,'crawl','Bang, bang!','Making noise is science.',
 [M9+' bang two things together and move things from one hand to the other.'],
 ['Dump blocks out of a container and put them back in together.'],
 ['Keep anything small enough to choke on out of reach.'],
 [],['CDC'])
wk(33,'crawl','A little shy','Stranger shyness is a normal sign of attachment.',
 [M9+' are shy, clingy or fearful around strangers, and react when you leave.'],
 ['Let your baby warm up to new people from your lap.'],
 ['Shyness with strangers at this age is expected, not a problem.'],
 [],['CDC'])
wk(34,'crawl','Where did it go?','Your baby knows things still exist when out of sight.',
 [M9+' look for things dropped out of sight, like a spoon or toy.'],
 ['Hide a toy under a cloth while your baby watches, then let them find it.'],
 ['Screen time is still not recommended under 1 year; reading and storytelling are encouraged instead.'],
 [],['CDC','WHO-PA','AAP-MEDIA'])
wk(35,'crawl','On the move','Crawling has a wide healthy range: 5.2 to 13.5 months.',
 [M9+' sit without support.','Some babies never crawl on hands and knees (about 4 in 100) and go straight to standing.'],
 ['Clear a safe floor space for exploring.'],
 ['Give your baby safe places to explore: move sharp or breakable things out of reach.'],
 [],['CDC','WHO-MM'])
wk(36,'crawl','Feeding themselves','Messy eating is learning.',
 [M9+' use their fingers to “rake” food towards themselves.'],
 ['Let your baby practise finger foods and a cup with a little water. Sit together and expect spills.'],
 ['Walking alone has a healthy range from 8.2 to 17.6 months, so there is no rush.'],
 [],['CDC','WHO-MM'])
wk(37,'crawl','Pick me up!','Your baby can ask with gestures.',
 [M9+' lift their arms up to be picked up and show several facial expressions.'],
 ['Name feelings as you see them: “You look surprised!”'],
 ['Keep offering new tastes and textures; it can take many tries before a food is liked.'],
 [],['CDC'])
wk(38,'crawl','Sitting up solo','New positions, new views.',
 [M9+' get to a sitting position by themselves.'],
 ['Ask for what you want to see: “time to sit” rather than “don’t stand”.'],
 ['Smooth, mashed or finely chopped foods all count as variety.'],
 [],['CDC'])
wk(39,'stand','9-month check-in','Review the 9-month milestones; a general developmental screening is recommended at 9 months.',
 [M9+' look when you call their name and bang two things together.'],
 ['Keep up daily floor play, reading and songs.'],
 ['Ask about the 9-month developmental screening at your next visit.'],
 [DOC],['CDC'])
wk(40,'stand','Bye-bye!','Gestures are words before words.',
 [M12+' wave “bye-bye”.'],
 ['Wave hello and bye-bye to people, pets and even the bathwater.'],
 ['Keep offering foods your baby rejected before; tastes change.'],
 [],['CDC'])
wk(41,'stand','Understanding “no”','Your baby understands more than they can say.',
 [M12+' understand “no” (they pause briefly or stop when you say it).'],
 ['Use short, clear words, and show what to do instead.'],
 ['Babies should not be strapped in (pram, high chair, carrier) for more than 1 hour at a time.'],
 [],['CDC','WHO-PA'])
wk(42,'stand','Pulling up','Furniture becomes a climbing frame.',
 [M12+' pull up to stand.','Standing with help has a healthy range from 4.8 to 11.4 months.'],
 ['Make sure what they pull up on is stable.'],
 ['Keep giving your baby safe places to explore.'],
 [],['CDC','WHO-MM'])
wk(43,'stand','Cruising','First steps holding on.',
 [M12+' walk while holding on to furniture.','Walking with help ranges from 5.9 to 13.7 months.'],
 ['Place toys along the sofa to encourage cruising.'],
 ['Being active several times a day is good for babies; more is better.'],
 [],['CDC','WHO-MM','WHO-PA'])
wk(44,'stand','Pincer grasp','Tiny fingers, tiny bits.',
 [M12+' pick things up between thumb and pointer finger, like small bits of food.'],
 ['Offer soft small finger foods to practise.'],
 ['Cut small round foods like grapes and cherry tomatoes into quarters.'],
 [],['CDC','NHS-SOLIDS'])
wk(45,'stand','Mama or dada','A special name for you is coming.',
 [M12+' call a parent “mama”, “dada” or another special name.'],
 ['Build on what your baby says: if they say “ta”, say “Yes, a truck!”'],
 ['Talk through everyday tasks; every word counts.'],
 [],['CDC'])
wk(46,'stand','In and out','Putting things in containers is a big thinking step.',
 [M12+' put something in a container, like a block in a cup.'],
 ['Play “in and out” with blocks and a box.'],
 ['Floor play several times a day is how babies practise new skills.'],
 [],['CDC','WHO-PA'])
wk(47,'stand','Hide and seek','Your baby remembers where things went.',
 [M12+' look for things they see you hide, like a toy under a blanket.'],
 ['Hide a toy under one of two cups and let your baby find it.'],
 ['Keep reading together daily; let your baby choose the book.'],
 [],['CDC','AAP-READ'])
wk(48,'stand','Baby-proofing round two','A mobile baby needs a safer home.',
 ['New reach: shelves, cupboards, bins.'],
 ['Get down to baby height and look for hazards.'],
 ['Move sharp or breakable things out of reach; lock away medicines, chemicals and cleaning products. Save your local poison or emergency number in your phone.'],
 [],['CDC'])
wk(49,'stand','Cup practice','Drinking skills are developing.',
 [M12+' drink from a cup without a lid while you hold it.'],
 ['Offer water in an open cup with meals.'],
 ['Drinks: water, breast milk or formula. No sugary drinks; juice isn’t needed.'],
 [],['CDC','NHS-SOLIDS'])
wk(50,'stand','Pat-a-cake','Games with rules and rhythm.',
 [M12+' play games with you, like pat-a-cake.'],
 ['Sing action songs and pause before the clap so your baby can join in.'],
 ['Still no screen time recommended; shared reading, songs and play are best.'],
 [],['CDC','WHO-PA','AAP-MEDIA'])
wk(51,'stand','Sleep before one','12–16 hours of sleep a day (including naps) is typical up to 12 months.',
 ['Every baby’s sleep is different, and Asian babies on average sleep a little less in studies.'],
 ['Keep the bedtime routine the same each night: bath, book, song.'],
 ['From 1 to 2 years, 11–14 hours a day is typical.'],
 [],['WHO-PA','GALLAND','NHS-SLEEP'])
wk(52,'stand','Happy first birthday!','One year! Look back at how far your baby has come.',
 [M12+' pull up to stand, wave bye-bye and understand “no”.','Many babies walk alone after their first birthday; the healthy range runs to 17.6 months.'],
 ['Celebrate with your baby’s favourite song and a photo for Moments.'],
 ['12-month vaccines (Singapore): MMR dose 1, chickenpox (varicella) dose 1 and the PCV booster. Cows’ milk can now be a main drink.'],
 [DOC],['CDC','WHO-MM','SG-NCIS','NHS-SOLIDS'])

assert len(W)==52 and [x['w'] for x in W]==list(range(1,53))
for x in W:
    for s in x['src']:assert s in SOURCES,(x['w'],s)
json.dump({'v':1,'sources':{k:{'name':v['name'],'url':v['url']} for k,v in SOURCES.items()},'weeks':W},open(OUT_JSON,'w'),ensure_ascii=False,separators=(',',':'))
# the reference document
L=['# Goldfox week-by-week guide: sources','','Every line in `weeks.json` names the sources it comes from (`src`). Each source below was read and checked',
   'in November 2026. Only these sources are used; nothing is taken from general memory.','',
   'Deliberately left out: "Wonder Weeks" / predictable developmental leaps. The idea comes from small studies, and attempts to',
   'replicate it have been mixed and disputed (secondary reports describe a replication by de Weerth and colleagues that found no',
   'regression periods; that paper was not read directly). So leaps are not presented as fact.','',
   'Also note: the widely repeated "crying peaks at 6 weeks" is not supported by the largest meta-analysis (Wolke 2017); the guide',
   'says crying stays around 2 hours a day for the first 6 weeks and falls after 8-9 weeks instead.','','## Sources','']
for k,v in SOURCES.items():
    L+=['### '+k,'- '+v['name'],'- '+v['url'],'- Key facts used: '+v['note'],'']
L+=['## Where each source is used','']
use={}
for x in W:
    for s in x['src']:use.setdefault(s,[]).append(x['w'])
for k in SOURCES:L.append('- '+k+': weeks '+', '.join(map(str,use.get(k,[]))))
L+=['','## To check before relying on vaccine timing','- The Singapore schedule here is the version effective 1 Nov 2020. MOH published an update dated 1 Apr 2026; confirm dose ages against it.','']
open(OUT_MD,'w').write('\n'.join(L))
print('weeks',len(W),'sources',len(SOURCES))
