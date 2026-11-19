---
name: cover-image
description: Make a cover image for a story in this project, in the FT collage style — a treated photo of an object that stands for the story (a radiator, a gas pipe, a wallet) with thick lines of the story's real data weaving through it, in front of some parts and behind others. Use this whenever the user asks for a cover, thumbnail, header, hero or featured image, lead art, OG or link-preview image, or "an image for the article", or wants a photo combined with chart lines or data, even if they don't say "collage" or name a chart. Not for the charts themselves at social media sizes (social-images).
---

# Cover image

A 16:9 cover, drawn at 3840 × 2160 and exported as one 1280 × 720 JPEG. The data comes from the
project's chart CSVs, the colours from the outlet's chart palette, and everything else from one
TOML file that `scripts/cover.py` turns into the image. The script handles the hard parts: the
photo treatment, masks, line paths that match the charts (d3's step and monotone curves), the
front/behind weave and the gaps around lines.

Work from the project root. Keep the cover's files together:

```
cover/
├── <name>.toml          # the config
└── source/              # the photo (and any upscaled or hand-made mask versions), with CREDITS.md
output/cover/<name>.jpg  # the result
```

## 1. Decide what the image says

Read the story (`docs/story.*`) and the chart data (`charts/data/*.csv`). Pick **one or two
series** whose shape carries the story; two lines look much cleaner than three. Pick an object
that stands for the subject and can carry the lines: something long or with gaps (pipes,
radiator columns, banknotes, a wallet) works best. The best weaves mean something: in the gas
story, the European price dips out of sight behind the pipe in the cheap years and rises above
it when prices soar.

## 2. Get the photo

The user usually supplies it (a file or a URL). Download into `cover/source/` and look at it.

- **Rights.** Photos from news sites and manufacturers belong to someone. Record the source and
  owner in `cover/source/CREDITS.md`, and tell the user it needs permission and a credit before
  publication.
- **Two modes.**
  - `cutout` — a transparent PNG of the object alone on the paper background (the classic FT
    look). If the photo has a background, cut it out first (for example with `rembg`, after
    asking the user to install it).
  - `scene` — the whole photo, treated. The lines pass behind one object in it (the
    *occluder*), found by colour.
- **Resolution.** The canvas is 3840 wide. A photo much under ~2000 px wide looks soft. Upscale
  it 4× with Real-ESRGAN (`realesrgan-ncnn-vulkan`, x4plus model, from the project's GitHub
  releases). Ask the user before downloading and running it. On integrated GPUs, pass `-t 64`, or
  it fails with `vkQueueSubmit failed`. Note the command next to the file.

## 3. Write the config

Copy the nearest example from `assets/examples/` into `cover/<name>.toml`:

- `cutout.toml` — a cut-out object (a radiator) with lines threading its columns.
- `scene.toml` — a whole photo in calm colour, lines over and under a pipe.
- `scene-mono.toml` — a whole photo in black and white with the occluder tinted, sky replaced.

Fill in the photo, the lines (CSV, filter, curve, colour) and the scale.
`references/config.md` documents every option.

**Colours.** Use the outlet's chart palette, in order: `palettes.categorical` in
`charts/src/lib/brands/<outlet>/theme.ts`. With no outlet, use mozaic's base theme. Use the same
colour per series as the story's charts, so readers recognise the lines.

## 4. Check, then place the lines

```bash
uv run .claude/skills/cover-image/scripts/cover.py check cover/<name>.toml
```

This writes `output/cover/<name>-check.png` and prints some numbers. In the image, the occluder
is tinted magenta, the detected sky green, and the lines are drawn thin. Look at it.

- **The occluder must hug the object.** If it doesn't, adjust `guess_top` or the colour ranges
  (band), the colour ranges (colour), or draw a mask by hand (`method = "file"`).
- **The sky** (scene mode) must not swallow blue objects. Tighten `sky_saturation` or
  `sky_value` if it does.
- **The lines** must cross the object where the idea needs them to. Move them with the scale:
  `zero`/`px_per_unit`, or `level`/`level_below` relative to the occluder's top edge.

Then decide the weave, the `front` setting for each line. The printed see-through gaps are the
seamless places to switch.

## 5. Build and look

```bash
uv run .claude/skills/cover-image/scripts/cover.py build cover/<name>.toml
```

Open the JPEG. Look at it whole, then at a thumbnail (about 480 px wide, how it appears in feeds
and link previews), then zoom into every crossing and every point where a line meets the
occluder. `canvas.master` saves a full-size PNG for zooming. Fix what you see, rebuild and show
the user. Expect a few rounds: the user's eye decides.

`references/look.md` has the style rules and the mistakes that are easy to make. Read it before
the first build.

## Notes

- The script needs `uv` and `rsvg-convert` (librsvg). It installs its own Python dependencies.
- Keep the cover free of text: the site adds the headline.
- If the user asks for other sizes or formats, change `canvas.export_width` or add a second
  config. Don't hand-edit the JPEG.
