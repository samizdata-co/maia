---
name: social-images
description: Export this project's mozaic charts as PNGs sized for social media — Instagram and Facebook feed (portrait, square), stories and reels, Bluesky/X/LinkedIn/Mastodon (landscape) and link posts — with the bundled `pnpm social` script, into output/social/. Use this whenever the user wants the story's charts for social media, a chart for a post, tweet or story, "social exports", or square, portrait, vertical, 9:16, 16:9 or Instagram versions of a chart, even if they only say "make the charts shareable". Not for the article's cover or lead image (cover-image), and not for print or web exports of charts (`pnpm export`).
---

# Social media images of the charts

`scripts/social.ts` renders each chart from its embed page in `output/charts/build/` with a headless Chromium
and saves a PNG at each platform's exact size to `output/social/<slug>/<locale>/<format>.png`. These are
for the outlet's own posts; nothing about them belongs in the embeds or the story. Don't add a page,
route or button for them.

| Format      | Pixels    | For                                                     |
| ----------- | --------- | ------------------------------------------------------- |
| `portrait`  | 1080×1350 | Instagram and Facebook feed (4:5): the best default     |
| `square`    | 1080×1080 | Instagram, Facebook, Threads                            |
| `story`     | 1080×1920 | Stories and reels; the top and bottom 250 px stay empty |
| `landscape` | 1600×900  | Bluesky, X, LinkedIn, Mastodon (16:9)                   |
| `link`      | 1200×630  | Facebook and LinkedIn landscape (1.91:1)                |

A chart's layout changes with its width, so the script doesn't just scale one picture. For each
chart and format it measures the chart at every width from 320 to 1400 px and picks the one that
fills the frame with the largest type. Tall formats get the mobile layout, and wide formats get a
wide chart. For each file it prints the width, the scale (×) and the share of the frame filled.

## 1. Build

```bash
cd charts && pnpm build
```

The script reads `output/charts/build/`, so a stale build gives stale charts. It warns when `src/` or `data/`
changed after the last build. If the chart data comes from the project's `etl/` or notebooks and
those changed, rerun them first.

## 2. Export

From `charts/`:

- `pnpm social`: the charts in `docs/story.*`, in the story's order, in every format and language.
  It finds them by their export or embed paths (`charts/exports/<slug>/…`) and skips commented-out
  parts (`<!-- -->`). If the story names no chart, it exports all of them.
- `pnpm social prices imports`: only these slugs (from `src/charts/index.ts`). `pnpm social all`
  exports every chart.
- Options:
  - `--formats portrait,story`
  - `--locales ro`
  - `--width 600`: a fixed chart width instead of the best fit
  - `--out <dir>`: another output folder, for trials
  - `--browser /path/to/chrome`: when no Chromium is found
  - `--help`: lists everything

If `pnpm social` isn't in `charts/package.json` (an older project), run
`node ../.claude/skills/social-images/scripts/social.ts` instead, or add that as the `social`
script. It needs Node 22.18 or later, which runs TypeScript directly.

## 3. Look at every image

Open the PNGs before handing them over. The script marks with `← check` any image whose scale is
below about 1.2 (small type on a phone) or whose fill is below 80% (lots of empty space). Look at
those first, but look at all of them. Check that nothing is clipped, labels don't collide, the
type is readable at phone size and the chart fills the frame.

To review many images at once, make a contact sheet of each chart in a scratch folder (needs
ImageMagick):

```bash
magick montage ../output/social/<slug>/<locale>/{portrait,square,story}.png -tile 3x1 -geometry +10+10 -background '#888' -resize x1000 <scratch>/<slug>-tall.png
magick montage ../output/social/<slug>/<locale>/{landscape,link}.png -tile 2x1 -geometry +10+10 -background '#888' -resize 1000x <scratch>/<slug>-wide.png
```

The sheet shrinks the images, so the story format looks smaller than it really is. Judge type
size from the scale the script printed.

## 4. Fix a poor fit

Different charts fail in different ways, so first work out why an image is poor:

- **Grids and waffles grow with their width.** In wide formats, the best fit is a very wide chart
  with tiny type. A fixed width of about 640–800 px gives larger type at the cost of some empty
  space, which is the better trade.
- **Line charts, scatters and bar charts with long notes grow taller as they narrow.** In the
  short `link` format their type stays small at any width. Narrower doesn't help. Recommend
  `landscape`, `portrait` or `square` for these instead.
- **Two panels side by side** (small multiples) can leave a tall format half empty. Try a width
  below the chart's breakpoint, where the panels stack. Keep the stacked version only if its type
  is not much smaller.

Try a few widths into a scratch folder and compare the images:

```bash
pnpm social prices --formats landscape,link --width 800 --out <scratch>/w800
```

When a width wins, save it in `charts/mozaic.config.ts` so that every later `pnpm social` uses
it:

```ts
social: {
	widths: { prices: { landscape: 800, link: 640 } }
}
```

Then rerun `pnpm social <slug>` to write the final images to `output/social/`. Change the chart
itself (its `Chart.svelte`) only when the change would also be better on the site. A clipped
label in a social image is usually a clipped label at that width in the embed too.

## 5. Hand over

List the files by chart and format, and say which images are weak and which format to use
instead. Send the user a few of the images (portrait is the usual pick), especially if they're
away. `output/social/` isn't ignored by git, so mention that it will show up as new files.

## Changing the script

- **A new format:** add it to `FORMATS` with its size, what it's for, and `safe` (px at the top
  and bottom) if the platform covers that area with its own buttons. Add it to the table above.
- **Other margins or a scale limit:** `marginOf` and `MAX_SCALE`.
- **mozaic's CLI:** the script borrows `launchBrowser` and `serveStatic` from
  `@samizdata/mozaic/cli`, resolved from the charts folder it runs in.
- **After a change:** run it on a line chart, a bar chart and a waffle or grid, in every format,
  and look at the images.
