---
name: mozaic-chart
description: Build or change a chart in this project's charts/ folder (mozaic). Use when asked to add a chart, change how a chart looks, or chart new data.
---

# Build a mozaic chart

1. **Data.** Find or create the tidy CSV in `charts/data/`. If it does not exist, add a step to
   the project's `etl/` scripts or notebook that writes it, and run it.
2. **Form.** Pick the chart from what the data must show: magnitude → bars; change over time →
   lines; parts of a whole → stacked bars (`StackedBarChart`) or a waffle; parts of a whole across groups of different sizes → mosaic (`MosaicChart`); distribution → beeswarm or histogram; where a reader's own value sits in published percentiles ("how do you compare?") → `PercentileChart`;
   geography → choropleth; two values per item → dumbbell or slope; one item at two dates → arrow plot (`ArrowChart`), or bars
   with a dot for the earlier date (`BarDotChart`) when the latest value matters most. One number → no chart.
3. **Files.** Work in `charts/`. Copy `src/charts/example/` to `src/charts/<slug>/`. Edit `data.ts` (import the CSV
   with `?raw`, parse with `csvParse(raw, autoType)`, type the rows), `messages.ts` (title,
   subtitle, alt, notes, source per language) and `Chart.svelte`.
4. **Compose.** If a recipe in `@samizdata/mozaic/recipes` fits (`BarChart`, `ColumnChart`, `LineChart`,
   `ScatterChart`, `ArrowChart`, `BarDotChart`, `StackedBarChart`, `MosaicChart`, `PercentileChart`), wrap it: pass the data, accessors and strings. A new
   form that other charts could reuse goes into mozaic as a recipe, not into this project.
   Otherwise use `Chart` / `Header` / `Plot` / `Svg` / marks / guides / `Footer` from mozaic.
   Prefer existing marks (`Bars`, `Line`, `Area`, `Points`, `Rects`, `Text`, `GeoPath`, `Treemap`,
   `Waffle`, `Dumbbell`, `Slope`, `Beeswarm`) and annotations (`Callout`, `RefLine`, `RefBand`,
   `Label`). Write raw SVG with `usePlot()` scales only when no mark fits.
5. **Register** the chart in `src/charts/index.ts` (slug, title, component, print widths).
6. **Check.** Run `pnpm check`. Open the preview with `pnpm dev` and look at the chart at 320 px
   and 1000 px, in every language and in print; fix overlaps, clipped labels and empty states.
7. **Build.** `pnpm build` must succeed; `pnpm export` produces print files when needed.
