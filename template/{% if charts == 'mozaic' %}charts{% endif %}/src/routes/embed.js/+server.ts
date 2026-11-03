import { hostScript } from 'mozaic/embed';

export const prerender = true;
export const trailingSlash = 'never';

/** The script host pages include to auto-size embed iframes. */
export function GET() {
	return new Response(hostScript, { headers: { 'content-type': 'text/javascript; charset=utf-8' } });
}
