import type { Component } from 'svelte';
import type { LocaleCode } from 'mozaic/locale';
import type { Medium, Theme } from 'mozaic/styles';
import Example from './example/Chart.svelte';
import { messages as exampleMessages } from './example/messages';

/** Props every chart component accepts. */
export interface ChartProps {
	style: Theme;
	locale: LocaleCode;
	medium?: Medium;
	width?: number;
}

export interface ChartEntry {
	/** URL segment: embed/<slug>/<locale>/ */
	slug: string;
	title: (locale: LocaleCode) => string;
	component: Component<ChartProps>;
	/** Print widths to export (names from the style's print.widths). */
	print: string[];
}

/** Every chart in this project. Add new charts here. */
export const charts: ChartEntry[] = [
	{ slug: 'example', title: (locale) => exampleMessages[locale].title, component: Example, print: ['column', 'double'] }
];
