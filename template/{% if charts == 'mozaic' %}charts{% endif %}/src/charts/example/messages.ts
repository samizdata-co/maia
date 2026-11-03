import type { LocaleCode } from '@samizdata/mozaic/locale';

export const messages: Record<
	LocaleCode,
	{
		title: string;
		subtitle: string;
		alt: string;
		notes: string;
		source: string;
		year: string;
		value: string;
		region: string;
		/** Display names for the region codes in the data. */
		regions: Record<string, string>;
	}
> = {
	en: {
		title: 'Example: values rose in every region',
		subtitle: 'Value by region, 2015–2024 (example data)',
		alt: 'Line chart of an example value for three regions from 2015 to 2024. All three rise; the capital rises fastest.',
		notes: 'Example data. Replace it with your own.',
		source: 'Example',
		year: 'Year',
		value: 'Value',
		region: 'Region',
		regions: { North: 'North', South: 'South', Capital: 'Capital' }
	},
	ro: {
		title: 'Exemplu: valorile au crescut în toate regiunile',
		subtitle: 'Valoarea pe regiuni, 2015–2024 (date de exemplu)',
		alt: 'Grafic liniar al unei valori de exemplu pentru trei regiuni, 2015–2024. Toate cresc; capitala crește cel mai repede.',
		notes: 'Date de exemplu. Înlocuiți-le cu datele proprii.',
		source: 'Exemplu',
		year: 'Anul',
		value: 'Valoarea',
		region: 'Regiunea',
		regions: { North: 'Nord', South: 'Sud', Capital: 'Capitala' }
	},
	ru: {
		title: 'Пример: значения выросли во всех регионах',
		subtitle: 'Значение по регионам, 2015–2024 (пример данных)',
		alt: 'Линейный график примерного значения для трёх регионов, 2015–2024. Все растут; быстрее всех столица.',
		notes: 'Пример данных. Замените своими данными.',
		source: 'Пример',
		year: 'Год',
		value: 'Значение',
		region: 'Регион',
		regions: { North: 'Север', South: 'Юг', Capital: 'Столица' }
	}
};
