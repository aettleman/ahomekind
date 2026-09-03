# Site Review Notes — text density & interactivity pass

Reviewed: index, about, start-here, quiz, impact, scan, shelf, ingredient-check, brand-check, instead-of, money, what-testing-means, food, fashion, shop, and all four journal articles (journal/index + 3 posts — that's the entire journal, not a sample).

## Overall impression

The "too text-heavy" complaint is accurate, but it's concentrated in about six pages, not the whole site. The interactive/tool pages (scan, shelf, ingredient-check, brand-check, quiz, shop) are already lean — they're data-driven UI with a sentence or two of framing, which is exactly the tone to replicate everywhere else. The worst offenders are the long-form explainer pages — **what-testing-means.html** (164 lines, dense factual paragraphs stacked with no visual break) and **about.html** (several 4-6 sentence run-on paragraphs) — plus the entire **journal**, which reads as AI-drafted filler rather than her voice. The site already nails the tone she wants in the homepage myth-vs-reality flip cards, the impact.html slider/preset calculator, and the swap-of-day widget — those are the benchmark: one punchy line of setup, then something you click or drag instead of read.

## Per-page notes

### index.html — mostly good, minor tightening
Word count impression: light. This is close to the target already — hero copy is two short paragraphs, then cards, flip cards, a calculator teaser, swap-of-day. Nothing needs cutting. The one dense spot is the hero paragraph ("Rabbits, dogs, monkeys and countless other non-human animals are still used and abused in unnecessary laboratory testing. It's still legal in much of the world. I want to show you where your money goes, so you can send it somewhere better.") — fine as prose, but consider trimming to two sentences max since it's above the fold. No structural changes needed.

### about.html — dense, needs restructuring, but it's her voice
Word count impression: medium-heavy for a single-page bio — six unbroken paragraphs with no visual break at all until the ko-fi box near the bottom.
- The paragraph "What really grinds my gears: brands calling themselves cruelty-free while still selling in markets that legally require animal testing. Certifications with no real teeth behind them. A bunny logo slapped on a bottle with nobody checking if it means anything." is good, punchy voice — but it's glued directly onto a second paragraph about her personal backstory with no paragraph break in the HTML (`</p> <p>` on one line), so visually it reads as one wall of text.
  - **Fix:** just add proper spacing/breathing room between these two ideas — they're different topics (industry gripe vs. personal history) and currently blur together.
- The opening two paragraphs ("Here's the thing about learning how animals are actually treated... It's not a small thing to sit with" / "I'm not going to put that in front of you here...") could become a single tighter paragraph, freeing up space for a pull-quote treatment (the site already has a `.pull-quote` style used on food.html and fashion.html) on the line "Once you know, you know" — turn that into a large pull-quote instead of burying it in paragraph one.
- **Suggestion:** the vegan-vs-cruelty-free explainer paragraph ("Vegan and cruelty-free get treated as a package deal, but they don't have to be...") duplicates content already told better and more visually on food.html and the journal cruelty-free-vs-vegan post. Cut it here to 1-2 sentences and link out, rather than re-explaining.

### start-here.html — already good
Word count impression: light, well-structured with tappable category cards. No changes needed. This is a second good example of the tone she wants (short intro sentence, then four clickable cards with a 1-line description each).

### quiz.html — already good
This is pure interactive widget territory (branching question flow, no static prose beyond a one-line intro). No changes needed — hold this up as a model for what to build toward elsewhere.

### impact.html — mostly excellent, one section to trim
The calculator itself (presets, sliders, live results, share button) is the best interactive element on the site outside the homepage flip cards. But below the fold, "where these numbers come from" and "the honest bit about supply and demand" run six dense paragraphs of methodology/caveat text back to back.
- The paragraph starting "Strictly, one person not buying a chicken does not mean one fewer chicken is farmed. Supermarkets order on forecasts, and there is slack in the system. Economists who have looked at this reckon the effect is real but less than one-to-one, somewhere in the region of 0.3 to 0.7 of an animal per animal not bought." is a solid, honest point, but it's dense.
  - **Fix:** this whole "where these numbers come from" block (5 sourced paragraphs: land animals, carbon/land, fish, averages, supply-and-demand) is a great candidate for a click-to-reveal accordion group (the site already uses `<details>`/`<summary>` for "why isn't this vegan?" on food.html and "the proof" links section) — four or five collapsed rows like "the land-animal number →", "why fish aren't counted →", "the honest bit about supply and demand →" that expand on tap. Right now someone has to wade through all of it or skip all of it; a toggle lets the curious dig in without punishing everyone else with a wall of text.

### what-testing-means.html — the densest page on the site, still in her voice
Word count impression: heavy — by far the longest sustained block of prose reviewed, roughly 30 paragraphs of unbroken text with only `.section-label` dividers.
- The Draize test description ("A substance is placed directly onto the eye of a conscious rabbit. The rabbit is restrained so it can't move; its eyelids are held open so it can't blink the substance away. It's then observed for up to fourteen days and scored for redness, swelling, ulceration, bleeding and, in some cases, blindness.") is genuinely important content and shouldn't be cut, but it's one of four back-to-back test-type descriptions (Draize, skin, lethal dose, longer studies) all delivered as plain paragraphs.
  - **Fix:** this section ("the tests themselves") is a natural fit for the flip-card component already built for the homepage myth grid — one card per test type, front = test name + one-line description, back = the fuller clinical detail. That keeps the weight of the information but makes engaging with each one optional and visual instead of one forced scroll.
- The UK statistics section ("2.54 million procedures... 1.32 million (52%) were experimental procedures... mice 56%, fish 16%, birds 10%, rats 9%...") is a paragraph of raw numbers that would read far better as 3-4 tappable stat chips or a simple bar breakdown than as prose — right now it's genuinely hard to parse as a sentence.
  - **Fix:** "2.54 million procedures in GB (2025)" as a big number treatment (the site already has this pattern via `.impact-teaser-num` and `.big-num` on impact.html), then the species breakdown as a horizontal bar/chip row underneath rather than a comma-separated list in prose.
- The "why beagles" section is strong, voicey writing (the lab technician quote is a gut-punch, in a good way) — don't touch this one, it's an example of the honest-not-preachy tone working well in long form; it just needs to sit inside a page that isn't otherwise a wall of text.
- Six `.section-label` sections in a row with no visual variation between them (the tests, why beagles, "but it's banned here", scale in the UK, scale globally, proof, and then what) makes the page feel like one long uninterrupted argument even though the content shifts tone. Breaking a few of these into the accordion/flip-card/stat-chip treatments above would fix that pacing problem without cutting a single fact.

### money.html — good, minor tightening
Word count impression: light-medium. The ownership-chain cards (parent company → owned brands, colour-coded clean/not-clean) are a strong existing pattern — the JS-rendered cards do the same "visual not prose" job the owner wants more of elsewhere. Only the intro two paragraphs and the closing "a note on this list" paragraph are plain text, and both are already short. No structural rework needed, this is close to done.

### food.html — already good
Light-medium, and doing the job well — the ingredient-watch list is already a colour-coded card grid with an accordion ("why isn't this vegan?") tucked under each ambiguous ingredient, exactly the click-to-reveal pattern she likes. The three text blocks (cruelty-free vs vegan for food, hidden ingredients intro, easy swaps) are all short and purposeful. No changes needed.

### fashion.html — already good
Same shape as food.html: a data-driven materials glossary and retailer-policy grid, both loaded from JSON into cards, minimal prose framing. No changes needed.

### shop.html, scan.html, shelf.html, ingredient-check.html, brand-check.html — already good
All five are functionally UI, not articles — camera capture, barcode lookup, OCR ingredient reading, brand search, and a tabbed shop grid. Copy is limited to short instructional lines ("take a photo of the ingredients list, or pick one from your camera roll") and disclaimers. These are the pages that already embody exactly what she's asking for site-wide. No changes recommended; if anything, use their card/badge/verdict-banner visual language (colour-coded `.v-good`/`.v-warn`/`.v-bad` states, `.rcard` layout) as the template when reworking the denser explainer pages above.

### instead-of.html — already good
Structured entirely as repeating "instead of X → try Y" swap cards with one-line notes each. This is a strong existing interactive-adjacent pattern (not literally clickable, but scannable and visual) — no rework needed.

## AI-draft pages vs her-voice-but-dense pages (explicit split)

**AI-draft placeholders, not yet in her voice** (needs a full personality rewrite, not just trimming):
- `journal/what-does-cruelty-free-mean.html`
- `journal/cruelty-free-vs-vegan.html`
- `journal/you-dont-have-to-be-perfect.html`

All three read as generic AI-blog output: short choppy one-line "paragraphs" stacked for rhythm rather than reason ("Trying to make better choices can be exhausting. / There are thousands of brands. / Thousands of products. / Different certifications. / Different claims."), emoji-as-section-headers (🐰 🌱 🏢 🔎 💚 🛍️ 🐾) that don't appear anywhere else on the site, and repetitive "you don't have to be perfect" reassurance loops that show up near-verbatim in two different posts and again in about.html and start-here.html. None of these posts have a specific opinion, a joke, or a concrete detail the way about.html or what-testing-means.html do — they read as filler written to sound reassuring rather than to say something. These need her actual voice pass before any density editing is worth doing; trimming AI-generic prose just makes it shorter AI-generic prose. Recommend she rewrites these from scratch in her own voice rather than editing in place — the content is thin enough (three posts covering ground already better covered by about.html and food.html) that the density problem may resolve itself once the padding is gone.

**Already her voice, just needs tightening/visual treatment:**
- `about.html`
- `what-testing-means.html`
- `impact.html` (only the methodology section)
- `money.html` (barely — already close)

These have specific, opinionated, funny lines ("nobody is dabbing blusher on a chimp and taking notes", "What really grinds my gears...", "burn it all down" in the quiz) that are unmistakably a real person's voice and shouldn't be rewritten — just broken up and given the site's existing interactive treatments.

## Patterns & recommendations

**Repeated content across pages:**
- The cruelty-free-vs-vegan distinction is explained near-fully three separate times (about.html, food.html, and journal/cruelty-free-vs-vegan.html) plus referenced in start-here.html and quiz.html's beginner-mode text. Since food.html's version is the clearest and most concise, consider making that the canonical explanation and having the others link to it with one line instead of re-explaining.
- The "you don't have to overhaul everything / small changes count" reassurance appears in about.html, start-here.html, food.html, and all three journal posts. It's a good message but repeating it word-for-word-adjacent five times dilutes it — pick 1-2 places it really lands (start-here.html's intro is a good one) and let the others reference it in passing.
- Newsletter signup block is identical boilerplate on every single page (fine as-is, it's not prose, just noting it's the one truly repeated component already).

**New interactive/visual treatment ideas, building on what's already there:**

1. **Flip cards for "myth vs fact" and "test type" explainers beyond the homepage.** The homepage myth grid is the strongest asset on the site — extend it to what-testing-means.html (one flip card per test type) and possibly to a "common excuses brands use" set on money.html or brand-check.html.
2. **Stat-chip / big-number treatment for any paragraph that's secretly a list of numbers.** impact.html and what-testing-means.html both already use oversized serif numbers (`.big-num`, `.impact-teaser-num`) for the calculator — reuse that pattern for the UK Home Office statistics paragraph instead of writing them out as a sentence.
3. **Accordion (`<details>`) groups for "sourcing/methodology" sections.** food.html already does this per-ingredient ("why isn't this vegan?"). Apply the same pattern to impact.html's "where these numbers come from" block and to any brand-check note that currently reads as a long justification paragraph.
4. **A before/after or "spot the difference" toggle for the money.html ownership chains and brand-check parent-company notes** — currently these are read top-to-bottom as prose-in-a-card; a two-state toggle ("this brand" / "its parent") with a visual swap could replace the sentence structure "X is cruelty-free but owned by Y which isn't" that's repeated with minor variation across a dozen brand notes.

Net recommendation: the tool pages (scan/shelf/brand-check/quiz/food/fashion) are done and should not be touched structurally — they're the standard. The fix is concentrated on about.html, what-testing-means.html, the methodology half of impact.html, and a full voice rewrite (not a trim) of the three journal posts.
