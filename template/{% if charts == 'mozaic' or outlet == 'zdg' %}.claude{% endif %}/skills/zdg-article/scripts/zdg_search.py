#!/usr/bin/env python3
"""Search zdg.md through its public WordPress REST API, and read its articles.

Standard library only. Examples:

    python3 zdg_search.py search "tarif gaz" --after 2026-01-01
    python3 zdg_search.py search cutremur --category reportaje --orderby date
    python3 zdg_search.py search "MD-ALERT" --title-only
    python3 zdg_search.py read https://www.zdg.md/stiri/.../slug/
    python3 zdg_search.py categories
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = 'https://www.zdg.md/wp-json/wp/v2'
USER_AGENT = 'Mozilla/5.0 (compatible; zdg-search/1.0)'
FIELDS = 'id,date,link,title,excerpt,categories'


def get(path: str, params: dict | None = None):
    query = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v not in (None, '')})
    url = f'{API}/{path}' + (f'?{query}' if query else '')
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), response.headers
    except urllib.error.HTTPError as error:
        sys.exit(f'{error.code} from {url}: {error.read()[:300].decode(errors="replace")}')
    except urllib.error.URLError as error:
        sys.exit(f'Could not reach {url}: {error.reason}')


def text(fragment: str) -> str:
    """HTML to one line of plain text."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


def to_markdown(content: str) -> str:
    """Article HTML to Markdown that keeps the links, headings, bold and embedded charts."""
    content = re.sub(r'<iframe[^>]*src="([^"]+)"[^>]*>.*?</iframe>', r'\n[Grafic: \1]\n', content, flags=re.S)
    content = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', r'\n[Imagine: \1]\n', content)
    content = re.sub(r'<a\s[^>]*>\s*(\[Imagine: [^\]]+\])\s*</a>', r'\1', content, flags=re.S)
    content = re.sub(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.S)
    content = re.sub(r'<h(\d)[^>]*>(.*?)</h\1>', lambda m: '\n' + '#' * int(m[1]) + ' ' + m[2] + '\n', content, flags=re.S)
    content = re.sub(r'</?(strong|b)>', '**', content)
    content = re.sub(r'</?(em|i)>', '*', content)
    content = re.sub(r'<li[^>]*>', '\n- ', content)
    content = re.sub(r'</p>|<br\s*/?>|</li>|</blockquote>', '\n', content)
    content = html.unescape(re.sub(r'<[^>]+>', '', content))
    content = content.replace('****', '').replace(' ', ' ')
    return re.sub(r'\n\s*\n+', '\n\n', content).strip()


def category_ids(slugs: str) -> str:
    ids = []
    for slug in slugs.split(','):
        found, _ = get('categories', {'slug': slug.strip(), '_fields': 'id'})
        if not found:
            sys.exit(f'No category "{slug}". Run `categories` to list them.')
        ids.append(str(found[0]['id']))
    return ','.join(ids)


def search(args):
    params = {
        'search': args.query,
        'per_page': args.per_page,
        'page': args.page,
        'orderby': args.orderby,
        'order': 'desc',
        'after': f'{args.after}T00:00:00' if args.after else None,
        'before': f'{args.before}T23:59:59' if args.before else None,
        'categories': category_ids(args.category) if args.category else None,
        'search_columns': 'post_title' if args.title_only else None,
        '_fields': FIELDS,
    }
    posts, headers = get('posts', params)
    if args.json:
        print(json.dumps(posts, ensure_ascii=False, indent=2))
        return
    total = headers.get('X-WP-Total', '?')
    pages = headers.get('X-WP-TotalPages', '?')
    print(f'{total} results for "{args.query}" (page {args.page} of {pages})\n')
    for post in posts:
        excerpt = text(post['excerpt']['rendered'])
        if len(excerpt) > args.excerpt:
            excerpt = excerpt[: args.excerpt].rsplit(' ', 1)[0] + '…'
        print(f"{post['date'][:10]}  {text(post['title']['rendered'])}")
        print(f"            {post['link']}")
        if excerpt:
            print(f'            {excerpt}')
        print()


def read(args):
    target = args.article.strip()
    if target.isdigit():
        post, _ = get(f'posts/{target}', {'_fields': 'id,date,modified,link,title,content'})
    else:
        slug = urllib.parse.urlparse(target).path.rstrip('/').rsplit('/', 1)[-1] or target
        found, _ = get('posts', {'slug': slug, '_fields': 'id,date,modified,link,title,content'})
        if not found:
            sys.exit(f'No zdg.md article with the slug "{slug}".')
        post = found[0]
    print(f"# {text(post['title']['rendered'])}\n")
    print(f"{post['link']}\nPublicat: {post['date'][:16].replace('T', ' ')}, modificat: {post['modified'][:16].replace('T', ' ')}\n")
    print(to_markdown(post['content']['rendered']))


def categories(args):
    found, _ = get('categories', {'per_page': 100, 'orderby': 'count', 'order': 'desc', '_fields': 'slug,name,count'})
    for category in found:
        print(f"{category['slug']:32} {category['count']:>7}  {html.unescape(category['name'])}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)

    s = commands.add_parser('search', help='search articles (newest or most relevant first)')
    s.add_argument('query', help='words to look for, in Romanian; diacritics are optional')
    s.add_argument('--after', metavar='YYYY-MM-DD', help='published on or after this date')
    s.add_argument('--before', metavar='YYYY-MM-DD', help='published on or before this date')
    s.add_argument('--category', metavar='SLUG', help='category slug(s), comma-separated (see `categories`)')
    s.add_argument('--title-only', action='store_true', help='match the title only')
    s.add_argument('--orderby', choices=['relevance', 'date'], default='relevance')
    s.add_argument('--per-page', type=int, default=10, help='results per page, up to 100')
    s.add_argument('--page', type=int, default=1)
    s.add_argument('--excerpt', type=int, default=220, help='characters of excerpt to show (0 for none)')
    s.add_argument('--json', action='store_true', help='print the raw API response')
    s.set_defaults(run=search)

    r = commands.add_parser('read', help='print an article as Markdown, with its links')
    r.add_argument('article', help='article URL, slug or numeric id')
    r.set_defaults(run=read)

    c = commands.add_parser('categories', help='list the category slugs')
    c.set_defaults(run=categories)

    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
