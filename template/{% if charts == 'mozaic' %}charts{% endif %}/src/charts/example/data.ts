import { autoType, csvParse } from 'd3-dsv';
// Chart data lives in charts/data/ (committed, unlike data/processed/). Vite inlines it at build time.
import raw from '../../../data/example.csv?raw';

export interface Row {
	year: number;
	region: string;
	value: number;
}

export const rows = csvParse(raw, autoType) as unknown as Row[];
export const regions = [...new Set(rows.map((d) => d.region))];
