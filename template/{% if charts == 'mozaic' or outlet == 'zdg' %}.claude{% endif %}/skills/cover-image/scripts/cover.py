# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "numpy>=2", "scipy>=1.14"]
# ///
"""Cover images in the FT collage style: a treated photo with real data lines weaving through it.

    uv run cover.py check cover/cover.toml   # masks and lines over the photo, plus numbers
    uv run cover.py build cover/cover.toml   # the cover: one JPEG, export_width wide

Everything is set in a TOML file (see references/config.md). Paths in it are relative to the
directory you run from (the project root). Needs rsvg-convert (librsvg) on the PATH.

How it is drawn, back to front:
  1. the scene: paper background, and either a cut-out photo (with a floor shadow) or a whole
     photo (treated; its sky kept, faded or replaced with paper);
  2. every line, in config order, each with an optional paper-coloured gap ("halo") around it;
  3. the occluder again (the cut-out, or the part of the photo the lines pass behind), so lines
     disappear behind it;
  4. the parts of lines that are "in front": a halo over everything, then the line.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

DEFAULTS = {
    "canvas": {"width": 3840, "height": 2160, "export_width": 1280, "quality": 90, "seed": 7},
    "background": {"centre": "#fcf7f0", "edge": "#f0e6d8", "centre_y": 0.46, "grain": 0.012},
    "photo": {
        "mode": "scene",  # scene | cutout
        "style": "colour",  # colour | mono
        # cutout placement (canvas px)
        "height": 1400, "centre_x": None, "floor": None, "shadow": 0.28,
        # scene crop (source px): [x, y, w, h]; default a centred band at the canvas aspect
        "crop": None,
        # tone
        "levels": [0.03, 0.97], "gamma": 1.0, "s_curve": 0.35, "grain": 0.025,
        # colour style
        "saturation_subject": 0.9, "saturation_rest": 0.62, "saturation_sky": 1.0, "haze": 0.18,
        # mono style
        "ink": "#181716", "tint": None,
        # scene sky: photo | fade | paper
        "sky": "photo",
        # sky detection: hue range; saturation range and minimum value of the main sky; a paler,
        # brighter band near the horizon; and the smallest patch that counts as sky (canvas px)
        "sky_hue": [195, 255], "sky_saturation": [0.33, 0.64], "sky_value": 0.55,
        "sky_pale": True, "sky_min_area": 2500,
    },
    "occluder": {"method": None},
    "style": {"line_width": 26, "halo": 12, "dot_radius": 34, "halo_behind": None},
    "scale": {},
}


# --- config ---------------------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    raw = tomllib.loads(path.read_text())
    cfg = {k: {**v, **raw.get(k, {})} for k, v in DEFAULTS.items()}
    cfg["line"] = raw.get("line", [])
    if "output" not in raw.get("canvas", {}):
        sys.exit("canvas.output is required (e.g. output/cover/cover.jpg)")
    if not cfg["line"]:
        sys.exit("at least one [[line]] is required")
    return cfg


def rgb(hex_: str) -> np.ndarray:
    h = hex_.lstrip("#")
    return np.array([int(h[i: i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def parse_x(v: str | float | int):
    if isinstance(v, (int, float)):
        return float(v)
    v = str(v).strip()
    try:
        return float(v)
    except ValueError:
        pass
    if len(v) == 7:  # YYYY-MM
        v += "-01"
    return date.fromisoformat(v[:10]).toordinal()


# --- data -----------------------------------------------------------------------------------------

def load_series(line: dict) -> list[tuple[float, float]]:
    rows = []
    with open(line["csv"], newline="") as f:
        for r in csv.DictReader(f):
            if any(str(r.get(k)) != str(v) for k, v in line.get("where", {}).items()):
                continue
            x, y = r[line.get("x", "date")], r[line.get("y", "value")]
            if y in ("", "NA", None):
                continue
            rows.append((parse_x(x), float(y)))
    rows.sort()
    if "from" in line:
        rows = [p for p in rows if p[0] >= parse_x(line["from"])]
    if "until" in line:
        rows = [p for p in rows if p[0] <= parse_x(line["until"])]
    if not rows:
        sys.exit(f"no rows for line {line.get('name', line['csv'])}")
    return rows


# --- paths ----------------------------------------------------------------------------------------

def linear(pts):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def step_after(pts):
    """d3.curveStepAfter."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (_, _), (x1, y1) in zip(pts, pts[1:]):
        d += f"H{x1:.1f}V{y1:.1f}"
    return d


def monotone_x(pts):
    """d3.curveMonotoneX (Steffen 1990): smooth, never overshoots the data."""
    n = len(pts)
    if n < 3:
        return linear(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    h = [xs[i + 1] - xs[i] or 1e-6 for i in range(n - 1)]
    s = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    t = [0.0] * n
    for i in range(1, n - 1):
        p = (s[i - 1] * h[i] + s[i] * h[i - 1]) / (h[i - 1] + h[i])
        t[i] = (np.sign(s[i - 1]) + np.sign(s[i])) * min(abs(s[i - 1]), abs(s[i]), 0.5 * abs(p))
    t[0] = (3 * s[0] - t[1]) / 2
    t[-1] = (3 * s[-1] - t[-2]) / 2
    d = f"M{xs[0]:.1f},{ys[0]:.1f}"
    for i in range(n - 1):
        dx = h[i] / 3
        d += (f"C{xs[i] + dx:.1f},{ys[i] + dx * t[i]:.1f} {xs[i + 1] - dx:.1f},{ys[i + 1] - dx * t[i + 1]:.1f} "
              f"{xs[i + 1]:.1f},{ys[i + 1]:.1f}")
    return d


CURVES = {"monotone": monotone_x, "step": step_after, "linear": linear}


def dots_for(line: dict, pts: list[tuple[float, float]], W: int) -> list[tuple[float, float]]:
    kind = line.get("dots", "end")
    if kind == "none":
        out = []
    elif kind == "end":
        out = [pts[-1]]
    elif kind == "changes":  # where the value changes (for steps), and the end
        out = [p for p, q in zip(pts[1:], pts) if p[1] != q[1]] + [pts[-1]]
    elif kind == "all":
        out = list(pts)
    else:
        sys.exit(f"dots must be none, end, changes or all, not {kind}")
    seen, uniq = set(), []
    for p in out:
        if 0 < p[0] < W and p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def svg(W, H, d, dots, colour, width, r):
    circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y in dots)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/><g fill="{colour}">{circles}</g></svg>')


def rasterise(text: str, W: int, H: int, tmp: Path, name: str) -> np.ndarray:
    src, png = tmp / f"{name}.svg", tmp / f"{name}.png"
    src.write_text(text)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-o", str(png), str(src)], check=True)
    return np.asarray(Image.open(png).convert("RGBA"), np.float32) / 255


# --- photo ----------------------------------------------------------------------------------------

def hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return hue, s, mx


def load_scene(p: dict, W: int, H: int) -> np.ndarray:
    im = Image.open(p["file"]).convert("RGB")
    if p["crop"]:
        x, y, w, h = p["crop"]
    else:
        w = min(im.width, round(im.height * W / H))
        h = round(w * H / W)
        x, y = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((x, y, x + w, y + h))
    scale = W / im.width
    im = im.resize((W, H), Image.LANCZOS)
    if scale > 1.5:  # a small photo blown up: put back some edge definition
        im = im.filter(ImageFilter.UnsharpMask(radius=2.5 * scale / 3, percent=70, threshold=2))
    return np.asarray(im, np.float32) / 255


def load_cutout(p: dict, W: int, H: int) -> tuple[np.ndarray, tuple[int, int]]:
    im = Image.open(p["file"]).convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if box is None:
        sys.exit("the cut-out is fully transparent")
    im = im.crop(box)
    h = int(p["height"])
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    cx = p["centre_x"] if p["centre_x"] is not None else W / 2
    floor = p["floor"] if p["floor"] is not None else H - (H - h) / 2
    return np.asarray(im, np.float32) / 255, (round(cx - im.width / 2), round(floor - h))


def place(layer: np.ndarray, at: tuple[int, int], W: int, H: int) -> np.ndarray:
    """Put a layer on a W x H canvas at `at`, clipping whatever falls outside."""
    out = np.zeros((H, W, layer.shape[2]), np.float32)
    x, y = at
    h, w = layer.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 < x1 and y0 < y1:
        out[y0:y1, x0:x1] = layer[y0 - y: y1 - y, x0 - x: x1 - x]
    return out


def tone(lum: np.ndarray, p: dict) -> np.ndarray:
    lo, hi = p["levels"]
    v = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1) ** p["gamma"]
    return p["s_curve"] * v * v * (3 - 2 * v) + (1 - p["s_curve"]) * v


def treat(a, subject, sky, p, paper, rng):
    """Mono: ink to paper (to `tint` on the subject). Colour: saturation per region, haze on the rest."""
    grain = rng.normal(0, p["grain"], a.shape[:2])[..., None]
    if p["style"] == "mono":
        lum = 0.30 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
        v = np.clip(tone(lum, p)[..., None] + grain, 0, 1)
        light = paper if not p["tint"] else paper * (1 - subject[..., None]) + rgb(p["tint"]) * subject[..., None]
        return rgb(p["ink"]) * (1 - v) + light * v
    c = tone(a, p)
    lum = (0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2])[..., None]
    s, k = subject[..., None], sky[..., None]
    sat = p["saturation_rest"] + (p["saturation_subject"] - p["saturation_rest"]) * s
    sat = sat + (p["saturation_sky"] - p["saturation_rest"]) * k * (1 - s)
    c = lum + (c - lum) * sat
    haze = p["haze"] * (1 - s) * (1 - k)
    c = c * (1 - haze) + paper * haze
    return np.clip(c + grain, 0, 1)


def background(cfg, W, H) -> np.ndarray:
    b = cfg["background"]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * b["centre_y"]) / (H * 0.75)) ** 2)
    t = np.clip(r, 0, 1)[..., None] ** 1.6
    return rgb(b["centre"]) * (1 - t) + rgb(b["edge"]) * t


def floor_shadow(alpha: np.ndarray, W: int, H: int) -> np.ndarray:
    """A soft pool under the cut-out's feet, a little to the right, and a tight contact shadow."""
    ys, xs = np.nonzero(alpha.max(axis=1) > 0.5)[0], np.nonzero(alpha.max(axis=0) > 0.5)[0]
    left, right, bottom = xs.min(), xs.max(), ys.max()
    span = right - left
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([left + span * 0.04, bottom - 40, right + span * 0.16, bottom + 70], fill=120)
    pool = np.asarray(m.filter(ImageFilter.GaussianBlur(55)), np.float32) / 255
    c = Image.new("L", (W, H), 0)
    ImageDraw.Draw(c).rectangle([left + 20, bottom - 14, right - 20, bottom + 8], fill=150)
    contact = np.asarray(c.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    return np.clip(pool + contact, 0, 1)


# --- masks ----------------------------------------------------------------------------------------

def robust_fit(xs, ys, keep_pct):
    for _ in range(4):
        c = np.polyfit(xs, ys, 2)
        res = np.abs(np.polyval(c, xs) - ys)
        keep = res < max(4, np.percentile(res, keep_pct))
        xs, ys = xs[keep], ys[keep]
    return np.polyfit(xs, ys, 2)


def in_ranges(hue, s, v, o):
    h0, h1 = o.get("hue", [0, 360])
    s0, s1 = o.get("saturation", [0, 1])
    v0, v1 = o.get("value", [0, 1])
    return (hue >= h0) & (hue <= h1) & (s >= s0) & (s <= s1) & (v >= v0) & (v <= v1)


def band_occluder(a, o, W, H):
    """A long object crossing the frame (a pipe, a road, a banner), between a top and a bottom edge.

    Its colour is given by hue/saturation/value ranges; each edge is found column by column near
    `guess_top` (y = a + b*x, canvas px) and fitted with a smooth curve, so lettering and stray
    pixels inside do not matter. Dark markings (value < 0.25) count as inside.
    """
    hue, s, v = hsv(a)
    paint = in_ranges(hue, s, v, o)
    inside = paint | (v < 0.25)
    ga, gb = o["guess_top"]
    search, run = o.get("search", 160), o.get("run", 40)
    xt, yt = [], []
    for x in range(0, W, 6):
        g = int(ga + gb * x)
        for y in range(max(g - search, 0), min(g + search, H - run)):
            if paint[y, x] and paint[y: y + run, x].mean() > 0.9 and not paint[max(y - 6, 0): y, x].any():
                xt.append(x)
                yt.append(y)
                break
    if len(xt) < 20:
        sys.exit("band: could not find the top edge; check guess_top and the colour ranges with `check`")
    top = robust_fit(np.array(xt), np.array(yt), 80)
    xb, yb = [], []
    for x in range(0, W, 6):
        y = int(np.polyval(top, x)) + o.get("bottom_from", 60)
        while y < H - 12 and inside[y: y + 12, x].mean() > 0.25:
            y += 1
        if y < H - 12:
            xb.append(x)
            yb.append(y)
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    t = np.polyval(top, xx)
    if len(xb) >= 20:
        b = np.polyval(robust_fit(np.array(xb), np.array(yb), 70), xx)
    else:  # runs off the bottom of the frame
        b = np.full_like(t, H + 10)
    mask = np.clip(yy - t + 0.5, 0, 1) * np.clip(b - yy + 0.5, 0, 1)
    return mask, top


def colour_occluder(a, o):
    """The largest region in the given colour ranges, holes filled (for lettering), edges softened."""
    hue, s, v = hsv(a)
    m = in_ranges(hue, s, v, o)
    labels, n = ndimage.label(m)
    if n == 0:
        sys.exit("colour: nothing in those colour ranges; check them with `check`")
    sizes = ndimage.sum(m, labels, range(1, n + 1))
    m = ndimage.binary_fill_holes(labels == 1 + int(np.argmax(sizes)))
    im = Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(1))
    return np.asarray(im, np.float32) / 255


def file_occluder(o, p, W, H):
    """A hand-made mask (white = occluder), the size of the photo; cropped and scaled like it."""
    im = Image.open(o["file"]).convert("L")
    if p["mode"] == "scene" and p["crop"]:
        x, y, w, h = p["crop"]
        im = im.crop((x, y, x + w, y + h))
    return np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255


def sky_mask(a, p, top_fn, W, H):
    """Sky-blue pixels (above the occluder's top edge, if it has one), in patches big enough to be sky.

    Deep, saturated blues (painted objects) and dim blue-greys (treelines) are left out.
    """
    hue, s, v = hsv(a)
    h0, h1 = p["sky_hue"]
    s0, s1 = p["sky_saturation"]
    main = (s >= s0) & (s <= s1) & (v > p["sky_value"])
    pale = (s > 0.2) & (s < s0) & (v > 0.74) if p["sky_pale"] else False
    m = (hue > h0) & (hue < h1) & (main | pale)
    if top_fn is not None:
        m &= np.arange(H)[:, None] < top_fn(np.arange(W))[None, :] - 2
    labels, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, labels, range(1, n + 1))
        m = np.isin(labels, 1 + np.nonzero(sizes > p["sky_min_area"])[0])
    im = Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255


def gaps(alpha: np.ndarray) -> list[tuple[int, int]]:
    """See-through gaps in the occluder (between a radiator's columns, say), across its middle."""
    rows = np.nonzero(alpha.max(axis=1) > 0.5)[0]
    if len(rows) == 0:
        return []
    r0, r1 = rows.min(), rows.max()
    band = alpha[r0 + int((r1 - r0) * 0.35): r0 + int((r1 - r0) * 0.65)]
    solid = band.mean(axis=0) > 0.6
    cols = np.nonzero(alpha.max(axis=0) > 0.5)[0]
    out, start = [], None
    for x in range(cols.min(), cols.max() + 1):
        if not solid[x] and start is None:
            start = x
        elif solid[x] and start is not None:
            if x - start > 8:
                out.append((start, x))
            start = None
    return out


# --- build ----------------------------------------------------------------------------------------

def over(base, layer, mask=None):
    a = layer[..., 3:4] if mask is None else layer[..., 3:4] * mask[..., None]
    return base * (1 - a) + layer[..., :3] * a


class Scene:
    """The treated picture without lines, its occluder, and what the y scale can hang on."""

    def __init__(self, cfg):
        c, p, o = cfg["canvas"], cfg["photo"], cfg["occluder"]
        W, H = c["width"], c["height"]
        self.W, self.H = W, H
        rng = np.random.default_rng(c["seed"])
        self.bg = background(cfg, W, H)
        paper = rgb(cfg["background"]["centre"])
        self.top_fn = None
        self.sky = np.zeros((H, W), np.float32)
        if p["mode"] == "cutout":
            cut, at = load_cutout(p, W, H)
            full = place(cut, at, W, H)
            self.occ = full[..., 3]
            treated = treat(full[..., :3], np.ones((H, W), np.float32), self.sky, p, paper, rng)
            base = self.bg * (1 - p["shadow"] * floor_shadow(self.occ, W, H)[..., None])
            self.base = over(base, np.dstack([treated, self.occ]))
        elif p["mode"] == "scene":
            a = load_scene(p, W, H)
            method = o["method"]
            if method == "band":
                self.occ, top = band_occluder(a, o, W, H)
                self.top_fn = lambda x: np.polyval(top, x)
            elif method == "colour":
                self.occ = colour_occluder(a, o)
            elif method == "file":
                self.occ = file_occluder(o, p, W, H)
            elif method is None:
                self.occ = np.zeros((H, W), np.float32)
            else:
                sys.exit(f"occluder.method must be band, colour or file, not {method}")
            if p["sky"] in ("paper", "fade") or (p["style"] == "colour" and p["saturation_sky"] != p["saturation_rest"]):
                self.sky = sky_mask(a, p, self.top_fn, W, H)
            treated = treat(a, self.occ, self.sky, p, paper, rng)
            sky = self.sky.copy()
            if p["sky"] == "photo":
                sky[:] = 0
            elif p["sky"] == "fade":
                horizon = self.top_of_occluder() or H * 0.6
                sky *= (np.clip((horizon - np.arange(H, dtype=np.float32)) / horizon, 0, 1) ** 0.7)[:, None]
            self.base = treated * (1 - sky[..., None]) + self.bg * sky[..., None]
        else:
            sys.exit(f"photo.mode must be scene or cutout, not {p['mode']}")

    def top_of_occluder(self, x=None):
        """The occluder's top edge at x (canvas centre by default)."""
        x = self.W / 2 if x is None else x
        if self.top_fn is not None:
            return float(self.top_fn(x))
        col = np.nonzero(self.occ[:, int(np.clip(x, 0, self.W - 1))] > 0.5)[0]
        if len(col) == 0:
            rows = np.nonzero(self.occ.max(axis=1) > 0.5)[0]
            return float(rows.min()) if len(rows) else None
        return float(col.min())


def scales(cfg, scene, series):
    s = cfg["scale"]
    xs = [p[0] for pts in series for p in pts]
    x0 = parse_x(s["x_from"]) if "x_from" in s else min(xs)
    x1 = parse_x(s["x_to"]) if "x_to" in s else max(xs)
    px0, px1 = s.get("px_from", 0), s.get("px_to", scene.W)
    sx = lambda x: px0 + (x - x0) / ((x1 - x0) or 1) * (px1 - px0)  # noqa: E731
    k = s.get("px_per_unit")
    if "zero" in s and k:
        zero = s["zero"]
    elif "level" in s and k:
        top = scene.top_of_occluder()
        if top is None:
            sys.exit("scale.level needs an occluder")
        zero = top + s.get("level_below", 50) + s["level"] * k
    elif "y_from" in s and "y_to" in s:  # [value, px] pairs
        (v0, p0), (v1, p1) = s["y_from"], s["y_to"]
        k = (p0 - p1) / (v1 - v0)
        zero = p0 + v0 * k
    else:
        sys.exit("scale needs zero + px_per_unit, level + px_per_unit, or y_from + y_to")
    sy = lambda v: zero - v * k  # noqa: E731
    return sx, sy


def front_mask(spec, occ, W, H, reach):
    """Columns where a line is drawn in front: its ranges, only where the occluder is (elsewhere
    the lines simply stack in config order)."""
    cols = np.zeros(W, bool)
    if spec == "all":
        cols[:] = True
    elif spec in ("none", None):
        pass
    else:
        for x0, x1 in spec:
            cols[max(int(x0), 0): max(min(int(x1), W), 0)] = True
    near = ndimage.binary_dilation(occ.max(axis=0) > 0.5, iterations=reach)
    return np.broadcast_to((cols & near).astype(np.float32), (H, W)).copy()


def prepare(cfg_path: Path):
    cfg = load_config(cfg_path)
    if not shutil.which("rsvg-convert"):
        sys.exit("rsvg-convert is not installed (librsvg: apt install librsvg2-bin, brew install librsvg, pacman -S librsvg)")
    scene = Scene(cfg)
    series = [load_series(line) for line in cfg["line"]]
    sx, sy = scales(cfg, scene, series)
    lines = []
    for line, pts in zip(cfg["line"], series):
        xy = [(sx(x), sy(y)) for x, y in pts]
        curve = CURVES.get(line.get("curve", "monotone"))
        if curve is None:
            sys.exit("curve must be monotone, step or linear")
        lines.append({**line, "pts": xy, "d": curve(xy), "dots": dots_for(line, xy, scene.W), "raw": pts})
    return cfg, scene, lines


def build(cfg_path: Path) -> None:
    cfg, scene, lines = prepare(cfg_path)
    W, H = scene.W, scene.H
    st = cfg["style"]
    lw, halo, r = st["line_width"], st["halo"], st["dot_radius"]
    halo_behind = st["halo_behind"]
    if halo_behind is None:
        halo_behind = cfg["photo"]["mode"] == "scene"
    reach = lw + 2 * halo + 2 * r
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for i, ln in enumerate(lines):
            ln["ink"] = rasterise(svg(W, H, ln["d"], ln["dots"], ln["colour"], lw, r), W, H, tmp, f"l{i}")
            ln["halo"] = rasterise(svg(W, H, ln["d"], ln["dots"], "#000", lw + 2 * halo, r + halo), W, H, tmp, f"h{i}")[..., 3]
    img = scene.base.copy()
    for ln in lines:  # behind
        if halo_behind:
            img = over(img, np.dstack([scene.bg, ln["halo"]]))
        img = over(img, ln["ink"])
    img = over(img, np.dstack([scene.base, scene.occ]))  # the occluder again
    for ln in lines:  # in front
        m = front_mask(ln.get("front", "none"), scene.occ, W, H, reach)
        # A dot is wholly in front or wholly behind, as its centre is.
        rr = r + halo + 3
        col = m[0].copy()
        for cx, cy in ln["dots"]:
            state = col[int(np.clip(cx, 0, W - 1))]
            y0, y1 = max(int(cy - rr), 0), min(int(cy + rr) + 1, H)
            x0, x1 = max(int(cx - rr), 0), min(int(cx + rr) + 1, W)
            gy, gx = np.mgrid[y0:y1, x0:x1]
            m[y0:y1, x0:x1][(gx - cx) ** 2 + (gy - cy) ** 2 <= rr * rr] = state
        img = over(img, np.dstack([scene.bg, ln["halo"]]), m)
        img = over(img, ln["ink"], m)
    rng = np.random.default_rng(cfg["canvas"]["seed"] + 1)
    img = np.clip(img + rng.normal(0, cfg["background"]["grain"], (H, W, 1)), 0, 1)

    out_path = Path(cfg["canvas"]["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB")
    if cfg["canvas"].get("master"):
        out.save(cfg["canvas"]["master"], optimize=True)
    ew = cfg["canvas"]["export_width"]
    out = out.resize((ew, round(ew * H / W)), Image.LANCZOS)
    out.save(out_path, quality=cfg["canvas"]["quality"], subsampling=0, optimize=True)
    print(f"wrote {out_path} ({out.width} x {out.height})")


def check(cfg_path: Path) -> None:
    """The photo with the occluder (magenta) and sky (green) tinted, the lines drawn thin, a
    1600-wide PNG next to the output; and the numbers you need to place the lines."""
    cfg, scene, lines = prepare(cfg_path)
    W, H = scene.W, scene.H
    img = scene.base.copy()
    img = img * (1 - 0.45 * scene.occ[..., None]) + np.array([1, 0, 1]) * 0.45 * scene.occ[..., None]
    img = img * (1 - 0.45 * scene.sky[..., None]) + np.array([0, 1, 0]) * 0.45 * scene.sky[..., None]
    with tempfile.TemporaryDirectory() as t:
        for i, ln in enumerate(lines):
            img = over(img, rasterise(svg(W, H, ln["d"], ln["dots"], ln["colour"], 8, 14), W, H, Path(t), f"c{i}"))
    out_path = Path(cfg["canvas"]["output"])
    path = out_path.with_name(out_path.stem + "-check.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((1600, round(1600 * H / W))).save(path)

    print(f"canvas {W} x {H}; check image: {path}")
    cols = np.nonzero(scene.occ.max(axis=0) > 0.5)[0]
    if len(cols):
        print(f"occluder: x {cols.min()}..{cols.max()}, top edge at x=0: {scene.top_of_occluder(0):.0f}, "
              f"centre: {scene.top_of_occluder():.0f}, right: {scene.top_of_occluder(W - 1):.0f}")
        g = gaps(scene.occ)
        if g:
            print("see-through gaps (switch front/behind inside one, so the switch is seamless):")
            print("  " + ", ".join(f"{(a + b) // 2}" for a, b in g))
    else:
        print("occluder: none")
    for ln in lines:
        ys = [p[1] for p in ln["pts"]]
        print(f"line {ln.get('name', ln['colour'])}: {len(ln['pts'])} points, x {ln['pts'][0][0]:.0f}..{ln['pts'][-1][0]:.0f}, "
              f"y {min(ys):.0f}..{max(ys):.0f}, dots at x {', '.join(f'{x:.0f}' for x, _ in ln['dots']) or '-'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["build", "check"])
    ap.add_argument("config", type=Path)
    args = ap.parse_args()
    (build if args.command == "build" else check)(args.config)


if __name__ == "__main__":
    main()
