// Images of the charts for social media, after `pnpm build`. Run from charts/: `pnpm social [slug…]`.
// For the outlet's own posts only: nothing about it is part of the embeds.
//
// Each chart is rendered from its embed page in ../output/charts/build/ and fitted into each format at its exact size in
// pixels. The chart's width (and so its layout, which changes at the breakpoints) is picked to fill the
// format best: the chart is drawn as large as fits inside the margins, and among the widths, the one that
// balances large type against empty space wins (scale × √share of the space filled). A width set for a
// chart and format in mozaic.config.ts (`social.widths`) wins over that choice. Files go to
// ../output/social/<slug>/<locale>/<format>.png.
//
//   pnpm social                          the charts in docs/story.* (all charts if it names none), every format
//   pnpm social prices imports           only these charts
//   pnpm social all                      every chart
//   pnpm social prices --formats square,story --locales ro
//   pnpm social prices --width 600       a fixed chart width (px) instead of the best fit
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

/** Sizes in pixels. `safe`: px at the top and bottom that the app covers with its own buttons, left empty. */
const FORMATS: Record<string, { width: number; height: number; use: string; safe?: number }> = {
	portrait: { width: 1080, height: 1350, use: 'Instagram and Facebook feed (4:5)' },
	square: { width: 1080, height: 1080, use: 'Instagram, Facebook, Threads (1:1)' },
	story: { width: 1080, height: 1920, use: 'Instagram and Facebook stories, reels (9:16)', safe: 250 },
	landscape: { width: 1600, height: 900, use: 'Bluesky, X, LinkedIn, Mastodon (16:9)' },
	link: { width: 1200, height: 630, use: 'Facebook and LinkedIn landscape (1.91:1)' }
};

/** Chart widths (CSS px) to try. Below 320 the charts are not designed to work. */
const MIN_WIDTH = 320;
const MAX_WIDTH = 1400;
const STEP = 10;
/** The largest scale a chart is drawn at, so a small chart in a big format does not get comically large type. */
const MAX_SCALE = 3.2;
/** Below these, the script flags an image to look at. */
const LOW_SCALE = 1.2;
const LOW_FILL = 0.8;

/** Interactive-only parts that do not belong in an image (as in `mozaic export`). */
const HIDE =
	'.mz-chart-tools, .mz-tooltip, .mz-data-table, .mz-data-download, .mz-button-group, .mz-table-search, .mz-table-more { display: none !important; }';

const { values: opts, positionals } = parseArgs({
	allowPositionals: true,
	options: {
		formats: { type: 'string', default: Object.keys(FORMATS).join(',') },
		locales: { type: 'string' },
		width: { type: 'string' },
		dir: { type: 'string', default: '../output/charts/build' },
		out: { type: 'string', default: '../output/social' },
		story: { type: 'string', default: '../docs' },
		browser: { type: 'string' },
		help: { type: 'boolean', short: 'h' }
	}
});

if (opts.help) {
	console.log('pnpm social [slug… | all] [--formats a,b] [--locales ro,en] [--width px] [--out dir] [--browser path]\n');
	for (const [name, f] of Object.entries(FORMATS)) console.log(`  ${name.padEnd(10)} ${f.width}×${f.height}  ${f.use}`);
	process.exit(0);
}

// mozaic's CLI finds a Chromium and serves a static folder; `mozaic export` uses the same two. It is resolved
// from the charts folder, since this script lives in the skill.
const require = createRequire(resolve('package.json'));
let cliPath: string;
try {
	cliPath = require.resolve('@samizdata/mozaic/cli');
} catch {
	throw new Error('Cannot find @samizdata/mozaic: run this from charts/ (`pnpm social`), after `pnpm install`.');
}
const { launchBrowser, serveStatic } = await import(pathToFileURL(cliPath).href);

/** Per chart and format widths from mozaic.config.ts, e.g. `social: { widths: { prices: { landscape: 800 } } }`. */
let presets: Record<string, Record<string, number>> = {};
try {
	const { config } = await import(pathToFileURL(resolve('mozaic.config.ts')).href);
	presets = config.social?.widths ?? {};
} catch (error) {
	console.warn(`Could not read social.widths from mozaic.config.ts (${(error as Error).message}); using the best fit.`);
}

interface Embed {
	slug: string;
	locale: string;
	title: string;
	path: string;
}
const manifest: { embeds: Embed[] } = JSON.parse(
	await readFile(join(opts.dir, 'embed', 'manifest.json'), 'utf8').catch(() => {
		throw new Error(`No ${opts.dir}/embed/manifest.json: run \`pnpm build\` first.`);
	})
);
const known = [...new Set(manifest.embeds.map((e) => e.slug))];

/** The newest modification time under a folder, to tell whether the build is stale. */
async function newest(dir: string): Promise<number> {
	let latest = 0;
	for (const entry of await readdir(dir, { withFileTypes: true, recursive: true }).catch(() => [])) {
		if (!entry.isFile()) continue;
		latest = Math.max(latest, (await stat(join(entry.parentPath, entry.name))).mtimeMs);
	}
	return latest;
}
const built = (await stat(join(opts.dir, 'embed', 'manifest.json'))).mtimeMs;
if (Math.max(await newest('src'), await newest('data')) > built)
	console.warn('Warning: src/ or data/ changed after the last build. Run `pnpm build` for current charts.\n');

/** The charts the story uses, in its order: slugs in export or embed paths, outside HTML comments. */
async function storyCharts(): Promise<string[]> {
	const files = (await readdir(opts.story).catch(() => [])).filter((f) => /^story\.(q?md|Rmd|ipynb|html)$/.test(f));
	const found: { slug: string; at: number }[] = [];
	for (const file of files) {
		const text = (await readFile(join(opts.story, file), 'utf8')).replace(/<!--[\s\S]*?-->/g, '');
		for (const slug of known) {
			const at = text.search(new RegExp(`(exports|embed)/${slug.replace(/[-]/g, '\\-')}/`));
			if (at >= 0 && !found.some((f) => f.slug === slug)) found.push({ slug, at });
		}
	}
	return found.sort((a, b) => a.at - b.at).map((f) => f.slug);
}

let slugs: string[];
if (positionals.includes('all')) slugs = known;
else if (positionals.length) slugs = positionals;
else {
	slugs = await storyCharts();
	console.log(slugs.length ? `Charts in the story: ${slugs.join(', ')}\n` : 'The story names no charts: exporting all.\n');
	if (!slugs.length) slugs = known;
}
const unknown = slugs.filter((s) => !known.includes(s));
if (unknown.length) throw new Error(`No chart ${unknown.join(', ')}. Charts: ${known.join(', ')}`);

const formats = opts.formats.split(',').map((f) => f.trim());
for (const f of formats)
	if (!FORMATS[f]) throw new Error(`No format ${f}. Formats: ${Object.keys(FORMATS).join(', ')}`);
const locales = opts.locales?.split(',').map((l) => l.trim());
const fixedWidth = opts.width ? Number(opts.width) : undefined;
const embeds = manifest.embeds
	.filter((e) => slugs.includes(e.slug) && (!locales || locales.includes(e.locale)))
	.sort((a, b) => slugs.indexOf(a.slug) - slugs.indexOf(b.slug));

/** Margin around the chart, in px of the image. */
const marginOf = (f: { width: number; height: number }) => Math.round(0.05 * Math.min(f.width, f.height));

const server = await serveStatic(opts.dir);
const browser = await launchBrowser(opts.browser);
const context = await browser.newContext({ deviceScaleFactor: 1, viewport: { width: 800, height: 800 } });
const page = await context.newPage();
const errors: string[] = [];
page.on('pageerror', (error: Error) => errors.push(error.message));

/** Wait for the chart to lay out again after a change of size. */
const settle = () =>
	page.evaluate(async () => {
		await document.fonts.ready;
		await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
	});

/** The chart's height when it is `width` px wide, without the controls under it. */
async function heightAt(width: number) {
	await page.setViewportSize({ width, height: 800 });
	await settle();
	return page.evaluate(() => document.querySelector('.mz-chart')!.getBoundingClientRect().height);
}

const written: string[] = [];
const toCheck: string[] = [];
try {
	for (const embed of embeds) {
		await page.setViewportSize({ width: 800, height: 800 });
		await page.goto(new URL(embed.path, server.url).href);
		await page.waitForFunction(() => Boolean((window as { __mozaic?: { ready?: boolean } }).__mozaic?.ready), null, {
			timeout: 15000
		});
		await page.addStyleTag({ content: HIDE });
		await settle();

		// Heights at every width, measured once per chart and shared by its formats.
		const preset = presets[embed.slug] ?? {};
		const widths: number[] = [];
		if (fixedWidth) widths.push(fixedWidth);
		else {
			for (let w = MIN_WIDTH; w <= MAX_WIDTH; w += STEP) widths.push(w);
			for (const w of Object.values(preset)) if (!widths.includes(w)) widths.push(w);
		}
		const heights = new Map<number, number>();
		for (const w of widths) heights.set(w, await heightAt(w));

		for (const name of formats) {
			const format = FORMATS[name];
			const margin = marginOf(format);
			const room = { width: format.width - 2 * margin, height: format.height - 2 * Math.max(margin, format.safe ?? 0) };
			const scaleAt = (w: number) => Math.min(room.width / w, room.height / heights.get(w)!, MAX_SCALE);
			const fillAt = (w: number) => (w * heights.get(w)! * scaleAt(w) ** 2) / (room.width * room.height);
			// A line chart's plot keeps its height as it widens, so a wide format is filled only by a wide chart
			// with smaller type: the square root lets it win when the type is not much smaller.
			const score = (w: number) => scaleAt(w) * Math.sqrt(fillAt(w));
			// Among near ties, the wider chart (more room for labels).
			let best = widths[0];
			for (const w of widths) if (score(w) >= score(best) * 0.995) best = w;
			const set = !fixedWidth && preset[name];
			if (set) best = set;
			const scale = scaleAt(best);

			await page.setViewportSize(format);
			await page.evaluate(
				({ width, scale }: { width: number; scale: number }) => {
					document.getElementById('social')?.remove();
					const bg = getComputedStyle(document.querySelector('.mz-chart')!).backgroundColor;
					const style = document.createElement('style');
					style.id = 'social';
					style.textContent = `
						html, body { width: 100%; height: 100%; overflow: hidden; background: ${bg}; }
						body { display: flex; align-items: center; justify-content: center; }
						.mz-embed { flex: none; width: ${width}px; transform: scale(${scale}); }`;
					document.head.append(style);
				},
				{ width: best, scale }
			);
			await settle();

			const file = join(opts.out, embed.slug, embed.locale, `${name}.png`);
			await mkdir(join(file, '..'), { recursive: true });
			await writeFile(file, await page.screenshot({ type: 'png' }));
			written.push(file);
			const fill = fillAt(best);
			const low = scale < LOW_SCALE || fill < LOW_FILL;
			if (low) toCheck.push(file);
			console.log(
				`${file}  (chart ${best}px wide${set ? ', set in mozaic.config.ts' : ''}, ×${scale.toFixed(2)}, fills ${Math.round(fill * 100)}%)${low ? '  ← check' : ''}`
			);

			await page.evaluate(() => document.getElementById('social')?.remove());
		}
	}
	if (errors.length) throw new Error(`Page errors:\n${errors.join('\n')}`);
} finally {
	await browser.close();
	await server.close();
}
console.log(`\n${written.length} images in ${opts.out}/`);
if (toCheck.length)
	console.log(`${toCheck.length} with small type (×<${LOW_SCALE}) or much empty space (<${LOW_FILL * 100}%): look at these first.`);
