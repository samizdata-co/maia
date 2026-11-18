# Config reference

`cover.py` reads one TOML file. Paths are relative to where you run it (the project root).
Coordinates are canvas pixels: x from the left, y from the top, on the 3840 × 2160 canvas.
Colours are hex strings.

## `[canvas]`

| Key | Default | |
|---|---|---|
| `output` | required | The JPEG to write, e.g. `output/cover/gas.jpg`. `check` writes `<stem>-check.png` beside it. |
| `width`, `height` | 3840, 2160 | The drawing size. Keep 16:9 unless asked otherwise. |
| `export_width` | 1280 | The exported JPEG's width; the height follows the aspect. |
| `quality` | 90 | JPEG quality. |
| `master` | none | Also save the full-size image here (a PNG), for zooming in while reviewing. |
| `seed` | 7 | Seed for the grain, so rebuilds are identical. |

## `[background]`

The paper: a warm off-white with a lighter centre.

| Key | Default | |
|---|---|---|
| `centre`, `edge` | `#fcf7f0`, `#f0e6d8` | Paper colour at the centre and at the edges. The halos around lines use this paper too. |
| `centre_y` | 0.46 | Height of the lighter centre, as a fraction of the canvas. |
| `grain` | 0.012 | Film grain over the whole image (standard deviation, 0–1 scale). |

## `[photo]`

| Key | Default | |
|---|---|---|
| `file` | required | The photo. |
| `mode` | `scene` | `cutout`: a transparent PNG placed on the paper (its opaque part is the occluder). `scene`: the whole photo fills the canvas. |
| `style` | `colour` | `colour` or `mono` (black and white, toned from `ink` to the paper). |
| `levels` | [0.03, 0.97] | Input black and white points (0–1). Very dark objects need a low white point: `[0, 0.32]` lifted a black radiator into a metallic grey. |
| `gamma` | 1.0 | Below 1 lightens the midtones. |
| `s_curve` | 0.35 | 0–1: how much S-shaped contrast to add. |
| `grain` | 0.025 | Grain on the photo itself. |

**Cutout only:** `height` (px of the object's opaque part; default 1400), `centre_x` (default
the canvas centre), `floor` (the y of its lowest pixel), `shadow` (strength of the soft floor
shadow, 0 for none; default 0.28).

**Scene only:** `crop = [x, y, w, h]` in source pixels. The default is the largest centred band at
the canvas aspect. A source more than 1.5× smaller than the canvas gets a little sharpening.

**Colour style:** `saturation_subject` (on the occluder; default 0.9), `saturation_rest`
(0.62), `saturation_sky` (1.0), `haze` (0.18: how far everything except the occluder and sky is
blended towards the paper, so it recedes). 1 = as photographed.

**Mono style:** `ink` (the darkest tone; default `#181716`), `tint` (a colour for the occluder's
highlights, e.g. `#eed680` to keep a pipe yellow; none by default).

**Sky (scene):** `sky = "photo" | "fade" | "paper"`. With `fade`, the sky goes from as
photographed at the occluder's top edge to the paper at the top of the frame. The sky is detected
by colour:

| Key | Default | |
|---|---|---|
| `sky_hue` | [195, 255] | Hue range, in degrees. |
| `sky_saturation` | [0.33, 0.64] | Saturation of the main sky. The upper limit keeps out painted blue objects (valves, gloves). Raise it for a deep, dark sky. |
| `sky_value` | 0.55 | Minimum brightness of the main sky. Lower it for a dark sky. |
| `sky_pale` | true | Also take paler, brighter blue near the horizon (s 0.2–`sky_saturation[0]`, value > 0.74), but not dim treelines. |
| `sky_min_area` | 2500 | Smaller blue patches are not sky. |

When the occluder has a top edge (`band`), only blue above that edge counts as sky.

## `[occluder]` (scene mode)

What the lines pass in front of or behind. In cutout mode it is the cut-out itself, and this
section is ignored.

- `method = "band"`: a long object crossing the frame (a pipe, a beam, a banner).
  - `hue`, `saturation` and `value` are `[min, max]` ranges of its colour. Measure them on the
    photo: the GAZ pipe was a pale yellow, `hue [30, 65]`, `saturation [0.25, 0.82]`, which kept
    out the saturated yellow pipes behind it.
  - `guess_top = [a, b]` is a rough top edge, `y = a + b·x`, in canvas pixels. Read it off the
    check image. The search looks `search` px (default 160) either side of it.
  - `bottom_from` (default 60) is how far below the top edge to start walking down to the bottom
    edge. Set it past any lettering.
  - Both edges are fitted with smooth curves. Dark markings inside (value < 0.25) count as the
    object, and a bottom edge that leaves the frame is fine.
- `method = "colour"`: the largest region in the `hue`, `saturation` and `value` ranges, with
  its holes filled.
- `method = "file"`: `file` is a hand-made mask (white is the occluder), the size of the photo.
  It is cropped and scaled like the photo.
- No method: no occluder; every line is simply drawn on top.

## `[scale]`

How data values map to the canvas. All lines share one scale.

- **x:** `x_from` and `x_to` (dates as `YYYY-MM-DD` or `YYYY-MM`, or numbers) map to `px_from`
  and `px_to`. They default to the data's range and 0…width. Start lines off the left edge
  (`px_from = -160`) and end them inside the right edge (`px_to = width - 260`), so the end dots
  show.
- **y**, one of:
  - `zero` (the y of value 0) and `px_per_unit`;
  - `level`, `level_below` and `px_per_unit`: value `level` sits `level_below` px under the
    occluder's top edge at the canvas centre. This is handy for "low values hide behind the
    object, high ones rise above it".
  - `y_from = [value, y]` and `y_to = [value, y]`: two anchor points.

Values can run off the canvas; peaks leaving the top edge look good.

## `[style]`

| Key | Default | |
|---|---|---|
| `line_width` | 26 | At 3840 wide. It stays legible at thumbnail size. |
| `halo` | 12 | Width of the paper-coloured gap around a line where it passes in front. |
| `dot_radius` | 34 | |
| `halo_behind` | scene: true, cutout: false | Also give lines a gap where they pass over the photo but behind the occluder. Over a busy photo they need it; on plain paper it only nicks other lines. |

## `[[line]]` (one block per line; later lines are drawn on top)

| Key | Default | |
|---|---|---|
| `csv` | required | e.g. `charts/data/prices.csv`. |
| `x`, `y` | `date`, `value` | Column names. |
| `where` | none | Row filter, e.g. `{ series = "europe" }`. |
| `from`, `until` | none | Keep rows within these x values. |
| `colour` | required | |
| `curve` | `monotone` | `monotone` (smooth, never overshoots: d3's curveMonotoneX), `step` (d3's curveStepAfter, for tariffs and other prices that change on a date), or `linear`. |
| `dots` | `end` | `none`, `end`, `changes` (each step change, plus the end) or `all`. |
| `front` | `none` | Where the line passes in front of the occluder: `"all"`, `"none"`, or x ranges `[[x0, x1], …]`. Ranges only matter where the occluder is; elsewhere lines stack in config order. A dot is wholly in front or behind, as its centre is. |
| `name` | | Used in `check`'s printout. |
