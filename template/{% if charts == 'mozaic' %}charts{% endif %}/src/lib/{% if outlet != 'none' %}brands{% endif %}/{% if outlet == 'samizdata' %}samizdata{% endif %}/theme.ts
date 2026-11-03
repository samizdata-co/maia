/**
 * SAMIZDATA house style for mozaic charts — brand v1.0.0.
 * Source: ../tokens.yml, ../../_brand.yml and ../../css/tokens.css. Copy this
 * folder into a mozaic project (do not edit the copy) and pass the theme to
 * `<Chart style={samizdata}>`.
 *
 * Documented adaptations for charts:
 * - Title weight 700: Space Grotesk on Bunny Fonts stops at 700 (the brand lists 900).
 * - Title line height 1 and tracking −0.02em: chart titles wrap and carry Romanian
 *   diacritics, so the 0.95 / −0.04em display settings are relaxed slightly.
 * - Work Sans 700 is loaded for the data-vis "strong" weight (datavis tokens: 700).
 * - Space Grotesk and Work Sans have no Cyrillic: Russian text falls back to the system sans.
 */
import { extendTheme } from '@samizdata/mozaic/styles';
import { samizdataMark } from './logo.js';

export const samizdata = extendTheme({
	name: 'samizdata',
	label: 'SAMIZDATA',
	tokens: {
		'--mz-font-title': "'Space Grotesk', ui-sans-serif, sans-serif",
		'--mz-font-body': "'Work Sans', ui-sans-serif, sans-serif",
		'--mz-font-label': "'Space Grotesk', ui-sans-serif, sans-serif",
		'--mz-weight-title': '700',
		'--mz-line-title': '1',
		'--mz-tracking-title': '-0.02em',
		'--mz-weight-label': '700',
		'--mz-weight-strong': '700',
		// The brand's "data label" voice: uppercase with generous tracking.
		'--mz-label-transform': 'uppercase',
		'--mz-label-tracking': '0.18em',
		'--mz-control-transform': 'uppercase',
		'--mz-control-tracking': '0.18em',
		'--mz-size-title': '1.5rem',
		'--mz-size-axis': '0.6875rem',
		'--mz-color-bg': '#fbf9f4',
		'--mz-color-text': '#1b1c19',
		'--mz-color-muted': '#574146',
		'--mz-color-faint': '#8a7076',
		'--mz-color-grid': 'rgba(138, 112, 118, 0.3)',
		'--mz-color-axis': '#8a7076',
		'--mz-color-accent': '#9f1853',
		'--mz-color-border': 'rgba(138, 112, 118, 0.3)',
		'--mz-color-tooltip-bg': 'rgba(255, 255, 255, 0.94)',
		'--mz-shadow-floating': '0 0.5rem 1.5rem rgba(123, 0, 60, 0.1)',
		'--mz-grid-dash': '2 2',
		// Sharp, architectural shapes.
		'--mz-radius': '0',
		'--mz-radius-floating': '0'
	},
	palettes: {
		categorical: ['#9f1853', '#28666e', '#c26d3a', '#60569b', '#67823a', '#a64b37', '#397c8c', '#8a6075'],
		sequential: ['#f8edf2', '#edcad8', '#dda0b9', '#c96891', '#ad3267', '#8b0c48', '#5d002e'],
		diverging: ['#28666e', '#f0eee9', '#9f1853'],
		semantic: {
			// Raspberry for the leading series or positive pole; teal for the negative pole.
			positive: '#9f1853',
			negative: '#28666e',
			neutral: '#8a7076',
			highlight: '#9f1853',
			// The brand's dark-mode muted ink: a warm grey that recedes on paper.
			context: '#c2b7b3'
		}
	},
	plot: { barRadius: 0, fontSize: 11 },
	fonts: { stylesheet: 'https://fonts.bunny.net/css?family=space-grotesk:700|work-sans:400,500,700&display=swap' },
	logo: { label: 'SAMIZDATA', svg: samizdataMark, text: 'SAMIZDATA', height: 14 },
	defaultLocale: 'en'
});
