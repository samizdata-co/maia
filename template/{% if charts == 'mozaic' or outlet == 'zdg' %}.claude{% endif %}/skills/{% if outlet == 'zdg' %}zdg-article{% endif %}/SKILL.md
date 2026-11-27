---
name: zdg-article
description: Write, edit, shorten or fact-check a data-driven article for Ziarul de Gardă (zdg.md) in Romanian, in docs/story.md — its title, bold lede, question subheads, chart placement, sourcing and links — in the house style of ZdG's data explainers, at 3,000–4,000 characters. Includes a script that searches zdg.md's own archive for articles to cite (search it before any other source) and one that counts the article's characters without comments and charts. Use this whenever the user asks to write, draft, outline, rewrite, edit, cut, tighten, proofread or source the story, an "articol", "reportaj", "explainer" or "infografic", a lede ("șapou"), a headline or subheads, to find ZdG articles or sources to link, or to check the length — even if they only say "write it up" or "turn this analysis into a story".
---

# Write a Ziarul de Gardă article

The article is a data explainer for Ziarul de Gardă (ZdG), an independent investigative outlet in
Chișinău. It takes a question readers are asking after a news event ("Cât plătește R. Moldova pentru
gaz?", "Cât de pregătită e R. Moldova pentru următorul cutremur?") and answers it with data, official
documents and earlier reporting, in plain Romanian, with charts. It is published in Reporter Special →
Reportaje. Readers are Moldovan citizens, not specialists: everything has to make sense to someone who
reads it on a phone on the way to work.

The story lives in `docs/story.md` (Quarto Markdown, rendered to .docx for the editor). Charts are
built separately (see the `mozaic-chart` skill if the project has charts) and are placed in the story
as images.

## Workflow

1. **Find the question and the peg.** What happened that makes people ask this now, and what is the one
   question the article answers? Read what the project already has: the analysis in `docs/`, data in
   `data/` and `charts/data/`, chart titles in `charts/src/charts/*/messages.ts`, notes in the README.
   The numbers in the article must match those.
2. **Search ZdG first.** Before any other source, look for ZdG's own coverage of each fact you will
   cite (see *Sources*). Run `scripts/zdg_search.py` (below), then `read` each candidate to check it
   actually says what you will attribute to it and when.
3. **Outline**: title, lede, three or four question subheads, where each chart goes.
4. **Write** `docs/story.md` (format below).
5. **Count** with `scripts/count_chars.py docs/story.md` and cut or add until it is 3,000–4,000
   characters (see *Length*).
6. **Check** against the checklist at the end, then tell the user the count, any fact you could not
   source (left as a comment in the story) and anything you changed in their numbers.

Never make up a number, a quote, a name or a link. If something needs a source you could not find,
write the sentence and add `<!-- SURSĂ? what is missing -->` after it; comments are not counted and
do not render, and the user can fill them in.

## The scripts

Both use only the Python standard library; run them with `python3` (or `uv run`) from the project root.

```bash
python3 .claude/skills/zdg-article/scripts/zdg_search.py search "tarif gaz" --after 2026-01-01
python3 .claude/skills/zdg-article/scripts/zdg_search.py search "MD-ALERT" --title-only
python3 .claude/skills/zdg-article/scripts/zdg_search.py search cutremur --category reportaje --orderby date
python3 .claude/skills/zdg-article/scripts/zdg_search.py read <url, slug or id>
python3 .claude/skills/zdg-article/scripts/zdg_search.py categories
python3 .claude/skills/zdg-article/scripts/count_chars.py docs/story.md
```

`search` queries zdg.md's WordPress API (`/wp-json/wp/v2/posts`), most relevant first, and prints
date, title, URL and excerpt. Search in Romanian, with the words a ZdG headline would use (`tarif gaz`,
`ANRE`, `Energocom`), try synonyms and the names of the people and institutions involved, and narrow
with `--after`/`--before` to the dates of the event. `--title-only` cuts noise for common words. `read`
prints an article as Markdown with its links, which is how you check a claim, and also how you find the
official document a ZdG news story was based on.

`count_chars.py` prints the characters a reader sees (with spaces, the number that counts), without
spaces, words, and a breakdown per section, so you know where to cut. It skips the front matter, `<!--
comments -->`, images and the `:::` chart blocks, code and link URLs; link text and headings count.
`--text` prints what it counted.

## Sources

Link the best source available for each fact, in this order of priority. Go down the list only when
nothing higher up has the fact:

1. **Articles published by zdg.md.** ZdG's own reporting comes first, even when an official source
   also has the fact: it is the outlet's journalism, it keeps readers on the site, and the editor
   expects it. Link the specific article that reports the fact, not a tag page or a video round-up
   when a news story exists. Check its date: a 2014 interview is fine for what an institute said in
   2014, not for what is true today.
2. **Official government sources.** Moldovan public institutions and state bodies: the Government,
   ministries, Parliament, ANRE, the National Bureau of Statistics (statistica.gov.md), legis.md and
   Monitorul Oficial, state companies' own announcements (Energocom), the institutes of the Academy
   (IGS); and their counterparts abroad (INFP in Romania, a ministry in Kyiv) for their own facts.
3. **Reputable NGOs, think tanks and international organisations**: World Bank, IMF, EBRD, UN
   agencies, OECD, Eurostat and other EU bodies, CSIS, Expert-Grup, Transparency International, peer-reviewed papers.
4. **Reputable international outlets**: Reuters, AP, AFP, BBC, Financial Times, Politico Europe,
   Radio Free Europe/Radio Liberty, Interfax for wire facts.
5. **Reputable outlets from Moldova and the region**: Radio Moldova/TRM, Europa Liberă Moldova,
   NewsMaker, Agora, IPN, Moldpres, and the equivalents in Romania and Ukraine (Digi24, HotNews,
   G4Media, Recorder, Ukrainska Pravda, The Kyiv Independent).
6. **Do not cite** low-quality, spammy or click-bait sources: content farms and aggregators that
   rewrite other outlets, anonymous Telegram channels, sites with no named editors, Russian state media
   and other propaganda outlets, Wikipedia, AI-generated pages, SEO "news" sites. Use them, at most, to
   find the original. If the story is *about* what such a source said, say so and attribute it ("a
   scris pe Telegram", "a relatat agenția rusă de stat RIA Novosti"), without presenting it as a source
   of fact.

Within a tier, prefer the original over a rewrite and the document over a press release about it. In
the earthquake story, the editor replaced a link to a site that summarised the ministry's statement
with Radio Moldova's interview in which the state secretary made it. Data you calculated yourself
gets a link to the dataset you used (an Eurostat table, a statistica.gov.md indicator); say what you
did in words ("la prețurile din 2025", "raportat la salariul mediu brut").

## Format of `docs/story.md`

```markdown
---
title: "Cât de pregătită e R. Moldova pentru următorul cutremur?"
author: "Prenume Nume"
format:
  docx: default
toc: false
---

**Lede, in bold: one or two paragraphs.**

**Prenume NUME**

Body paragraph that bridges from the news to the question.

## Cât de des avem cutremure?

Body…

::: {.content-hidden when-format="pdf"}
![](../output/charts/exports/<slug>/zdg-ro/web.png){fig-alt="…"}
:::

::: {.content-visible when-format="pdf"}
![](../output/charts/exports/<slug>/zdg-ro/print-double.pdf){fig-alt="…"}
:::
```

Keep the front matter the project already has. The byline goes under the lede, with the surname in
capitals (`**Nicu CALCEA**`). Use the chart export paths that exist in the project (`ls
output/charts/exports`); the `fig-alt` says what the chart shows and its main numbers, in Romanian. If
a chart doesn't exist yet, put `<!-- GRAFIC: what it should show -->` where it belongs.

## Structure

**Title.** Ask the question the article answers, or state the finding, in at most about 90 characters,
with the country as "R. Moldova": "Cât plătește R. Moldova pentru gaz, cum ajunge în țară și de ce
nu-l cumpărăm „mai ieftin” din Rusia?". ZdG marks the genre with a capitalised prefix and a slash; use
`INFOGRAFIC/ ` when the charts carry the story. Quote a claim you examine in „…” ("„mai ieftin”").

**Lede** (bold, the WordPress excerpt). It must work alone, because on the homepage and on Facebook it
is all most people read. Open with the news peg and the hard numbers, then the stakes:
*„De la începutul lunii octombrie, consumatorii din R. Moldova plătesc 26,14 lei pentru un metru cub
de gaz, cu 56 % mai mult decât în aceeași perioadă a anului trecut."* Or pose the question and give the
main findings up front, as the editor did for the earthquake story: *„Cutremurul de săptămâna trecută a
trecut fără victime, dar cât de pregătită e R. Moldova pentru un cutremur cu magnitudinea de peste 7?
Țara noastră are multe clădiri vechi… nu are o listă a clădirilor cu risc seismic și nici o lege…"*
Around 300–500 characters.

**Bridge.** One or two short paragraphs after the byline that take the reader from the event to the
bigger picture: *„A fost cel mai puternic cutremur pe care l-a simțit R. Moldova în acest an, însă
departe de ce am avut în anii precedenți sau de ce ar putea urma."*

**Sections.** Three or four `##` subheads, each a short question the reader would ask next, in a
logical order — the cause, the mechanism, the comparison: „De ce se majorează costul gazului?”, „De
unde vine gazul?", „De ce nu mai cumpărăm gaz din Rusia?”, „Cât costă gazul în alte țări?”. The first
sentence under each subhead answers it; the rest gives evidence, context and caveats.

**Charts.** Each chart goes after the paragraph that makes its point. The text gives the headline
number; the chart gives the detail, so don't walk through it or write „în graficul de mai jos”. One
chart per section at most, three or four in all.

**Ending.** Close on a fact that answers the headline, not on a verdict that repeats the article.
The gas story turns the official claim around: *„Altfel spus, R. Moldova, într-adevăr, nu are cel mai
scump gaz din Europa. Raportat la venituri însă, cetățenii R. Moldova plătesc mult mai mult decât
restul continentului."* The earthquake story ends with what is certain: *„Cutremurele nu pot fi
prezise, însă, cu siguranță, se vor repeta… De la ultimul cu o asemenea intensitate au trecut 40 de
ani."* The editor cut the author's summary paragraph that followed („R. Moldova se apropie de
următorul cutremur mare doar parțial pregătită…").

## Voice

- **Explain, don't argue.** Neutral, calm, factual. Let numbers and named sources make the case; no
  adjectives of judgement ("alarmant", "dezastruos"), no rhetorical questions in the body, no
  exclamation marks, no advice to the reader.
- **Explain how things work.** The value of the piece is the mechanism behind the news: *„Prețul
  aprobat de ANRE este, de fapt, o prognoză. Când prețul real e mai mic, diferența e returnată
  consumatorilor prin ieftiniri, iar când e mai mare, deficitul e recuperat prin scumpiri."* Define a
  technical term the first time, in a clause: the logarithmic magnitude scale, the TTF index, EMS-98.
- **Give every number a scale.** A change ("cu 56 % mai mult"), a comparison with the region ("de două
  ori mai scump decât în România"), a share of income ("15,47 % dintr-un salariu mediu brut"), today's
  prices for old sums, "de N ori" for energy or price ratios. Round where precision adds nothing
  ("circa două treimi", "aproape în proporții egale"), keep exact figures for tariffs and official data.
- **Test claims against data.** When an official makes a claim, report it, then what the data show,
  fairly: *„ministrul Energiei, Dorin Junghietu, a negat că R. Moldova ar plăti cele mai mari tarife la
  gaz din Europa. Datele Eurostat arată, într-adevăr, că…"* Then the angle the claim leaves out.
- **Add the caveat in the same place as the fact.** *„Statisticile arată însă țara de unde a fost
  cumpărat gazul, nu neapărat cea în care a fost extras."* *„Nu toate construcțiile vechi sunt
  periculoase, însă…"* Say what is not public ("nu publică numele câștigătorilor și nici prețurile din
  contracte", "Prețul este confidențial").
- **Plain, short sentences.** One idea per sentence, active voice, mostly 15–25 words. Paragraphs of
  two to four sentences. Connectors that carry the logic: *însă, totuși, astfel, totodată, în plus,
  de fapt, altfel spus, în comparație*.
- **"Noi" for the country, sparingly.** ZdG writes as a Moldovan outlet: *„de ce nu-l cumpărăm”*, *„ce
  am avut în anii precedenți"*, *„Țara noastră”*. Never "I".
- **People and institutions.** On first mention, the role then the name: „ministrul Energiei, Dorin
  Junghietu", „secretarul de stat al Ministerului Infrastructurii și Dezvoltării Regionale, Veaceslav
  Șipitca", „inginerul constructor Evgheni Cutia, lector universitar la Universitatea Tehnică a
  Moldovei". Then the surname or the role („șefa statului”). Institutions: the full name with the
  acronym in brackets, then the acronym: „Institutul de Geologie și Seismologie (IGS)”. Well-known ones
  (ANRE, Eurostat, Banca Mondială) need no expansion.
- **Attribute in the sentence.** „potrivit Eurostat”, „Potrivit IGS”, „potrivit recensământului din
  2024", „Datele … arată”. Quotes are short, in „…”, followed by the verb and the speaker: „…”, a
  punctat șefa statului. Use a quote for a position or a reason, not for a number.
- **Names of places.** "R. Moldova" (the long form "Republica Moldova" only occasionally), "malul
  drept" for the territory the government controls, "regiunea transnistreană", "Chișinău",
  "București".

## Romanian typography (as the ZdG editor applies it)

- Decimal comma: `5,7`, `26,14 lei`. Four-digit numbers without a separator: `2795 de clădiri`,
  `de 4000 de ori`, `1883 de dolari`. Larger numbers in words where possible (`893 de milioane de metri
  cubi`, `15,5 miliarde de lei`), otherwise a dot: `12.500`.
- "de" after numbers whose last two digits are 20 or more: `25 de ani`, `500 de ori`, `32 de ori`, but
  `13 cutremure`, `2–3 %`.
- Percent with a space: `56 %`, `2–3 %`.
- En dash without spaces for ranges: `35–40 de secunde`, `2026–2027`, `ianuarie–august`. Spaced en dash
  ` – ` in a sentence; no em dashes (—).
- Romanian quotation marks „…”.
- Diacritics with a comma below (ș, ț), never the cedilla (ş, ţ).
- Dates and times: `18 noiembrie`, `la 1 septembrie`, `la ora 02:48`; month names in lower case.
- Units in words in the text (`metri cubi`, `lei`, `euro/MWh`); symbols such as m³ are for charts.

## Links

Put the link on the words that state the fact, three to eight of them, not on "aici", the source's
name alone or a whole sentence: *„[a declarat că necesarul de gaze este „asigurat integral”](…)"*,
*„[doar 2–3 % din case sunt asigurate](…)”*. Every number that is not common knowledge has a link or a
named source in the sentence. Link the specific page (the article, the PDF, the dataset), never a
homepage. Aim for roughly one link per paragraph; the same source linked once is enough.

## Length

Most articles are **3,000–4,000 characters with spaces**, counted by `scripts/count_chars.py` (charts
and comments excluded). If the user asks for another length, use theirs (`--min`/`--max`).

To cut: drop the second example where one makes the point, the background the reader doesn't need to
follow the argument, numbers that repeat what a chart shows, and a section that doesn't answer a
question the title raises; merge sentences that share a subject; turn a quote into attribution. Keep
the lede numbers, the mechanism, the caveats and the comparison that gives the scale. To add, add
context or a comparison with sources, never padding.

## Checklist

- The lede works alone and holds the main numbers.
- Every subhead is a question that the first sentence under it answers.
- Every number has a source in the sentence or a link, matches the data and charts in the project, and
  has a scale.
- Sources follow the priority order: ZdG searched first and linked where it covers the fact; nothing
  from tier 6.
- Officials named with their role; acronyms expanded once.
- Typography: decimal commas, `56 %`, en dashes, „…”, ș and ț, "de" after 20+.
- 3,000–4,000 characters with spaces.
- No invented facts or links; open questions left as `<!-- SURSĂ? -->` comments and reported to the user.
- `quarto render docs/story.md` lists possible spelling mistakes (Hunspell, Romanian); fix them, and
  add correct names to `WORDLIST`.
