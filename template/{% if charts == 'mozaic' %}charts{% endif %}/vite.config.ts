import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
			},
			// Next to the rendered docs in ../output/ (Quarto's output-dir), so the whole story publishes from one folder.
			adapter: adapter({ pages: '../output/charts/build' }),
			prerender: {
				// The manifest and host script are not linked from any page.
				entries: ['*', '/embed/manifest.json', '/embed.js']
			}
		})
	]
});
