import { json } from '@sveltejs/kit';
import type { EmbedManifest } from '@samizdata/mozaic/embed';
import { charts } from '../../../charts';
import { config } from '../../../../mozaic.config';
import { theme } from '../../../lib/theme';

export const prerender = true;
export const trailingSlash = 'never';

/** Lists every embed page for `mozaic export`. */
export function GET() {
	const manifest: EmbedManifest = {
		project: config.project,
		embeds: charts.flatMap((chart) =>
			config.locales.map((locale) => ({
				slug: chart.slug,
				style: theme.name,
				locale,
				title: chart.title(locale),
				path: `embed/${chart.slug}/${locale}/`,
				print: Object.fromEntries(chart.print.map((name) => [name, theme.print.widths[name]]))
			}))
		)
	};
	return json(manifest);
}
