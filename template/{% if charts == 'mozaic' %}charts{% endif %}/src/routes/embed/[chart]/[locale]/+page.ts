import { error } from '@sveltejs/kit';
import type { LocaleCode } from '@samizdata/mozaic/locale';
import { charts } from '../../../../charts';
import { config } from '../../../../../mozaic.config';
import type { EntryGenerator, PageLoad } from './$types';

export const entries: EntryGenerator = () =>
	charts.flatMap((chart) => config.locales.map((locale) => ({ chart: chart.slug, locale })));

export const load: PageLoad = ({ params }) => {
	const chart = charts.find((c) => c.slug === params.chart);
	if (!chart || !config.locales.includes(params.locale as LocaleCode)) error(404, 'No such chart');
	return { slug: chart.slug, locale: params.locale as LocaleCode };
};
