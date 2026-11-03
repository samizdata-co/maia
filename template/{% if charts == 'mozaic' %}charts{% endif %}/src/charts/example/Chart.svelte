<script lang="ts">
	import { scaleLinear } from 'd3-scale';
	import { extent, max } from 'd3-array';
	import { Chart, Header, Title, Subtitle, Footer, Notes, Source, DataTable } from '@samizdata/mozaic/frame';
	import { Plot, Svg, Html } from '@samizdata/mozaic/core';
	import { Line, LineEndLabels, Points } from '@samizdata/mozaic/marks';
	import { AxisX, AxisY, GridY, Legend } from '@samizdata/mozaic/guides';
	import { PointerArea, Tooltip } from '@samizdata/mozaic/interactive';
	import { createLocale } from '@samizdata/mozaic/locale';
	import type { ChartProps } from '../index';
	import { messages } from './messages';
	import { regions, rows, type Row } from './data';

	let { style, locale, medium = 'web', width }: ChartProps = $props();

	const t = $derived(messages[locale]);
	const fmt = $derived(createLocale(locale));
	const theme = $derived(style);
	// Colour follows the region, in palette order.
	const color = $derived(Object.fromEntries(regions.map((r, i) => [r, theme.palettes.categorical[i]])));

	const years = [...new Set(rows.map((d) => d.year))];
	const x = scaleLinear().domain(extent(years) as [number, number]);
	const y = scaleLinear()
		.domain([0, max(rows, (d) => d.value) ?? 1])
		.nice();
	const series = regions.map((region) => ({ region, values: rows.filter((d) => d.region === region) }));
	const ends = series.map((s) => s.values[s.values.length - 1]);

	let hoverYear = $state<number | null>(null);
</script>

<Chart {style} {locale} {medium} {width} alt={t.alt}>
	<Header>
		<Title>{t.title}</Title>
		<Subtitle>{t.subtitle}</Subtitle>
		<Legend shape="line" items={regions.map((r) => ({ label: t.regions[r] ?? r, color: color[r] }))} />
	</Header>

	<Plot
		{x}
		{y}
		height={({ breakpoint }) => (breakpoint === 's' ? 240 : 320)}
		padding={{ left: 36, right: 80, top: 12, bottom: 28 }}
	>
		{#snippet children(plot)}
			<Svg>
				<GridY ticks={5} />
				<AxisY ticks={5} />
				<AxisX tickValues={years.filter((_, i) => plot.breakpoint !== 's' || i % 3 === 0)} format={String} />
				{#each series as s (s.region)}
					<Line data={s.values} x={(d: Row) => d.year} y={(d: Row) => d.value} stroke={color[s.region]} />
				{/each}
				<LineEndLabels
					data={ends}
					x={(d) => d.year}
					y={(d) => d.value}
					text={(d) => t.regions[d.region] ?? d.region}
					color={(d) => color[d.region]}
				/>
				{#if hoverYear !== null}
					<Points
						data={rows.filter((d) => d.year === hoverYear)}
						x={(d) => d.year}
						y={(d) => d.value}
						fill={(d) => color[d.region]}
					/>
				{/if}
				<PointerArea
					onmove={({ x: px }) => (hoverYear = Math.round(plot.x.invert?.(px) ?? years[0]))}
					onleave={() => (hoverYear = null)}
				/>
			</Svg>
			<Html>
				{#if hoverYear !== null}
					<Tooltip x={plot.x(hoverYear) ?? 0} y={plot.height / 2}>
						<strong>{hoverYear}</strong>
						{#each rows.filter((d) => d.year === hoverYear).toSorted((a, b) => b.value - a.value) as d (d.region)}
							<div>{t.regions[d.region] ?? d.region}: <strong>{fmt.number(d.value)}</strong></div>
						{/each}
					</Tooltip>
				{/if}
			</Html>
		{/snippet}
	</Plot>

	<Footer>
		<Notes>{t.notes}</Notes>
		<Source>{t.source}</Source>
	</Footer>
	<DataTable
		data={rows}
		columns={[
			{ key: 'region', label: t.region, value: (d: Row) => t.regions[d.region] ?? d.region },
			{ key: 'year', label: t.year, value: (d: Row) => d.year, format: String },
			{ key: 'value', label: t.value, value: (d: Row) => d.value }
		]}
		maxRows={10}
	/>
</Chart>
