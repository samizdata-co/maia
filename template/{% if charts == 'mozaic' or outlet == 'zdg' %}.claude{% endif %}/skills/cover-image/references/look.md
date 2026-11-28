# The look, and what to avoid

These rules came out of real review rounds with an editor. Each says why, so you can judge cases
they don't cover.

## The style

- **The FT collage.** A photo on a warm off-white paper, with thick data lines and big dots. The
  lines have no axes and no labels, and they run off the edges. The photo is high-contrast and
  grainy. In mono, a single colour accent can survive (the FT keeps banknotes green; we kept a
  gas pipe yellow).
- **The lines pass in front of the object in places and behind it in others.** That weave is what
  makes it a collage rather than a chart pasted on a photo. Where a line passes in front, a thin
  paper-coloured gap separates it from what is behind.
- **One idea.** One object and one or two lines. The image works at 480 px wide in a feed, so
  anything that only reads at full size doesn't count.
- **No text.** The site sets the headline.
- **The subject sits in the middle.** Sites crop covers to squares and to 1.91:1 link previews.

## Lines

- **Two lines at most, in the story's chart colours**, so readers connect them to the charts.
  Same unit, same scale. Stretch, offset or crop the scale freely for composition, but never
  change a line's shape. It is decoration, but it must still be the real data.
- **Width 26 px at 3840 (about 9 px at 1280).** Thinner lines vanish in thumbnails, and dotted or
  dashed lines read as noise.
- **Dots:** an end dot on each line works well. A dot at every step change was too busy; the
  editor preferred the bare line with only its end dot.
- **Slivers.** When a line runs almost along the occluder's edge, it shows as a thin sliver or a
  tiny bump that looks like a glitch. Shift the scale a little so the values sit clearly above or
  below the edge, then zoom in to check.

## The weave

- **Fewer switches.** Switching front and behind at every radiator column made the lines look
  dashed. One switch per line was much cleaner: blue in front of the left part and behind the
  right, red the other way round.
- **Switch where it is seamless.** That means inside a see-through gap (where the line shows
  either way) or off the object entirely. `check` lists the gaps.
- **Never switch across a dot.** A dot half in front and half behind looks broken. The script
  gives each dot the state of its centre; pick switch points well away from dots.
- **The gap around a front line covers everything behind it**, other lines included. If the gap
  only covered the photo, a line behind would show right up to the front line in the
  see-through gaps: "the red line goes over the blue's outline but behind the line".
- **Outside the object, lines cross with no gap**, the later one on top. A gap at those crossings
  looked like clipping to the editor.
- **Let the weave mean something** where the data allows: low prices hidden behind the pipe,
  high prices rising above it.

## The photo

- **Cut-outs** suit plain objects on the paper (mono, with a soft floor shadow). Very dark objects
  hide their detail in the shadows: lift them with a low white point (`levels = [0, 0.32]`).
- **Whole photos** suit scenes. Editors may want colour rather than black and white. Find the
  middle ground: keep the occluder's colour strong (about 0.9 saturation), mute the rest (about
  0.6) and haze it slightly towards the paper, so the eye lands on the object and the lines.
  "Too vivid, too much happening" was the complaint at full saturation.
- **Keep the real sky** unless asked otherwise. Replacing it with paper looked too cut-out for a
  whole photo, and a fade to paper was rejected too. The lines' gaps keep them legible on blue.
- **Watch what the sky detection takes.** Blue valves and blue gloves turned into paper-coloured
  holes until the sky was limited to pale blues above the occluder.
- **Small photos:** a 1200 px source upscaled with plain resampling is soft. Real-ESRGAN gives
  crisp edges and lettering. Its slightly painted texture on gravel or foliage disappears under
  the grain.

## Reviewing

Look at the whole image, then a 480 px thumbnail, then full-size crops of every crossing and
every place a line meets the occluder's edge. Problems hide at the crossings: slivers, nicked
lines, cut dots, gaps where none belong.
