<!-- Preview page: every chart in every language, with embed codes and downloads. Not meant for readers. -->
<script lang="ts">
	import { embedCode } from 'mozaic/embed';
	import { downloadPng, downloadSvg } from 'mozaic/export';
	import { mm } from 'mozaic/core';
	import type { LocaleCode } from 'mozaic/locale';
	import { charts } from '../charts';
	import { config } from '../../mozaic.config';
	import { theme } from '../lib/theme';

	let locale = $state<LocaleCode>(config.locales[0]);
	let width = $state(640);
	let medium = $state<'web' | 'print'>('web');
	const frames: Record<string, HTMLElement> = $state({});

	const figure = (slug: string) => frames[slug]?.querySelector('.mz-chart') as HTMLElement;
	const url = (slug: string) => `${config.baseUrl || '/'}embed/${slug}/${locale}/`;
</script>

<svelte:head><title>{config.title} · preview</title></svelte:head>

<main>
	<h1>{config.title}</h1>
	<p class="meta">Style: <strong>{theme.label}</strong> · Project: <code>{config.project}</code></p>
	<div class="controls">
		<label
			>Language <select bind:value={locale}
				>{#each config.locales as l (l)}<option value={l}>{l}</option>{/each}</select
			></label
		>
		<label
			>Medium <select bind:value={medium}><option value="web">web</option><option value="print">print</option></select
			></label
		>
		{#if medium === 'web'}
			<label>Width {width}px <input type="range" min="300" max="1000" step="10" bind:value={width} /></label>
		{:else}
			<label
				>Print width <select bind:value={width}
					>{#each Object.entries(theme.print.widths) as [name, w] (name)}<option value={Math.round(mm(w))}
							>{name} ({w} mm)</option
						>{/each}</select
				></label
			>
		{/if}
	</div>

	{#each charts as chart (chart.slug)}
		<section>
			<h2>{chart.title(locale)} <a href="embed/{chart.slug}/{locale}/">embed page</a></h2>
			<div class="frame" style:width="{width}px" bind:this={frames[chart.slug]}>
				<chart.component style={theme} {locale} {medium} width={medium === 'print' ? width : undefined} />
			</div>
			<div class="actions">
				<button onclick={() => downloadSvg(figure(chart.slug), `${chart.slug}-${locale}.svg`)}>Download SVG</button>
				<button onclick={() => downloadPng(figure(chart.slug), `${chart.slug}-${locale}.png`)}>Download PNG</button>
			</div>
			<textarea readonly rows="3"
				>{embedCode({
					src: url(chart.slug),
					title: chart.title(locale),
					scriptSrc: `${config.baseUrl || '/'}embed.js`
				})}</textarea
			>
		</section>
	{/each}
</main>

<style>
	main {
		max-width: 1040px;
		margin: 0 auto;
		padding: 1.5rem 16px 4rem;
		font-family: system-ui, sans-serif;
	}
	.meta {
		color: #555;
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem 1.5rem;
		padding: 0.75rem 1rem;
		border: 1px solid #ddd;
		border-radius: 6px;
	}
	label {
		display: flex;
		flex-direction: column;
		font-size: 0.8125rem;
		font-weight: 600;
	}
	section {
		margin-top: 2.5rem;
	}
	h2 {
		font-size: 1rem;
	}
	h2 a {
		font-size: 0.8125rem;
		font-weight: 400;
	}
	.frame {
		max-width: 100%;
		padding: 16px;
		border: 1px solid #ddd;
		border-radius: 6px;
		box-sizing: border-box;
	}
	.actions {
		display: flex;
		gap: 0.5rem;
		margin: 0.5rem 0;
	}
	textarea {
		width: 100%;
		font-family: ui-monospace, monospace;
		font-size: 0.75rem;
	}
</style>
