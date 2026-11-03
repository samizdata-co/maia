/**
 * Ziarul de Gardă house style for mozaic charts — brand v0.1.0.
 * Source: ../tokens.yml and ../../_brand.yml. Copy this folder into a mozaic
 * project (do not edit the copy) and pass the theme to `<Chart style={zdg}>`.
 *
 * From the zdg.md site design (October 2026): Source Serif Pro 600 headlines,
 * Source Sans Pro text, blue #0158B5, navy #002853, coral #FF595A, blue-grey
 * meta text #718BA7 and pale blue panels #CDD7EE.
 *
 * The site has no published chart palette. The categorical palette starts with
 * the brand blue and coral and adds amber, teal, violet and a light blue; slots
 * 1–4 pass the colour-blindness checks for all pairs on white. The sequential
 * ramp runs from a pale blue (≥ 2:1 on white) through the brand blue to the
 * site's navies.
 */
import { extendTheme } from '@samizdata/mozaic/styles';
import { zdgLogo } from './logo.js';

export const zdg = extendTheme({
	name: 'zdg',
	label: 'Ziarul de Gardă',
	tokens: {
		'--mz-font-title': "'Source Serif Pro', 'Source Serif 4', Georgia, serif",
		'--mz-font-body': "'Source Sans Pro', 'Source Sans 3', system-ui, sans-serif",
		'--mz-font-label': "'Source Sans Pro', 'Source Sans 3', system-ui, sans-serif",
		'--mz-weight-title': '600',
		'--mz-line-title': '1.25',
		'--mz-weight-label': '600',
		'--mz-weight-strong': '600',
		// Pills and chips on the site are uppercase with light tracking.
		'--mz-control-transform': 'uppercase',
		'--mz-control-tracking': '0.08em',
		'--mz-size-title': '1.5rem',
		'--mz-color-bg': '#ffffff',
		'--mz-color-text': '#171717',
		// #718BA7 (the site's meta colour) is too light for small text; the excerpt grey is used instead.
		'--mz-color-muted': '#585858',
		'--mz-color-faint': '#718ba7',
		'--mz-color-grid': '#cdd7ee',
		'--mz-color-axis': '#718ba7',
		'--mz-color-accent': '#0158b5',
		'--mz-color-border': '#cdd7ee',
		'--mz-shadow-floating': '0 0.5rem 1.5rem rgba(1, 88, 181, 0.12)',
		'--mz-radius': '999px',
		'--mz-radius-floating': '4px'
	},
	palettes: {
		categorical: ['#0158b5', '#ff595a', '#e8a33d', '#1a9e8f', '#7354a6', '#5fa8e8'],
		sequential: ['#94b9e8', '#6699dd', '#3a7bcd', '#0158b5', '#10357f', '#002853'],
		diverging: ['#0158b5', '#e8ebef', '#ff595a'],
		semantic: {
			positive: '#0158b5',
			negative: '#ff595a',
			neutral: '#718ba7',
			highlight: '#ff595a',
			context: '#b8c2cf'
		}
	},
	plot: { barRadius: 0 },
	fonts: {
		stylesheet: 'https://fonts.bunny.net/css?family=source-sans-pro:400,600,700|source-serif-pro:600&display=swap'
	},
	logo: { label: 'Ziarul de Gardă', svg: zdgLogo, height: 30 },
	defaultLocale: 'ro'
});
