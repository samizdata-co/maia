#!/usr/bin/env python3
"""Count the characters a reader sees in a Markdown/Quarto article.

Counts the body only: not the YAML front matter, comments (<!-- -->), charts and images
(![](…), iframes, the ::: blocks that hold them), code blocks or link URLs. Link text,
headings and the bold lede count. Paragraph breaks don't, as in Word's "characters
(with spaces)". Standard library only.

    python3 count_chars.py docs/story.md
    python3 count_chars.py docs/story.md --min 3000 --max 4000
    python3 count_chars.py docs/story.md --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


def visible_text(source: str) -> str:
    text = source.replace('\r\n', '\n')
    # YAML front matter at the very top.
    text = re.sub(r'\A---\n.*?\n(---|\.\.\.)\n', '', text, flags=re.S)
    # HTML comments, possibly over several lines.
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    # Fenced code blocks, including raw ```{=html} blocks.
    text = re.sub(r'^(```|~~~).*?^\1[^\n]*$', '', text, flags=re.S | re.M)
    # Iframes and other embeds, then any HTML tags left.
    text = re.sub(r'<(iframe|script|figure)\b.*?</\1>', '', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', '', text)
    # Quarto shortcodes ({{< video … >}}) and images with their attributes (charts, fig-alt).
    text = re.sub(r'\{\{<.*?>\}\}', '', text, flags=re.S)
    text = re.sub(r'!\[(?:[^\]\\]|\\.)*\]\([^)]*\)(\{[^}]*\})?', '', text, flags=re.S)
    # Fenced div markers (::: {.content-hidden …}, :::); their remaining text still counts.
    text = re.sub(r'^\s*:{3,}.*$', '', text, flags=re.M)
    # Footnote markers and reference-style link definitions.
    text = re.sub(r'\[\^[^\]]+\]', '', text)
    text = re.sub(r'^\s*\[[^\]]+\]:\s+\S+.*$', '', text, flags=re.M)
    # Links and spans keep their text: [text](url), [text]{.class}, [text][ref].
    for _ in range(3):  # nested brackets, e.g. a link inside a span
        text = re.sub(r'\[([^\[\]]*)\]\([^)]*\)', r'\1', text)
        text = re.sub(r'\[([^\[\]]*)\]\{[^}]*\}', r'\1', text)
        text = re.sub(r'\[([^\[\]]*)\]\[[^\]]*\]', r'\1', text)
    # Heading attributes ({#id .class}) and markers.
    text = re.sub(r'^(#{1,6}\s.*?)\s*\{[^}]*\}\s*$', r'\1', text, flags=re.M)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.M)
    # Block quotes, list markers, horizontal rules.
    text = re.sub(r'^\s*>\s?', '', text, flags=re.M)
    text = re.sub(r'^\s*([-*+]|\d+[.)])\s+', '', text, flags=re.M)
    text = re.sub(r'^\s*([-*_]\s*){3,}$', '', text, flags=re.M)
    # Emphasis markers and backslash escapes.
    text = re.sub(r'(\*\*|__|\*|_(?=\S)|(?<=\S)_)', '', text)
    text = re.sub(r'\\(.)', r'\1', text)
    return text


def paragraphs(text: str) -> list[str]:
    blocks = re.split(r'\n\s*\n', text)
    cleaned = (re.sub(r'\s+', ' ', block.replace(' ', ' ')).strip() for block in blocks)
    return [block for block in cleaned if block]


def sections(source: str) -> list[tuple[str, int]]:
    """Characters per section: the text before the first heading, then each heading."""
    body = re.sub(r'\A---\n.*?\n(---|\.\.\.)\n', '', source.replace('\r\n', '\n'), flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    body = re.sub(r'^(```|~~~).*?^\1[^\n]*$', '', body, flags=re.S | re.M)
    parts = re.split(r'^(#{1,6}\s.*)$', body, flags=re.M)
    result = [('(intro)', parts[0])]
    for heading, content in zip(parts[1::2], parts[2::2]):
        result.append((heading, heading + '\n\n' + content))
    return [(name, sum(len(p) for p in paragraphs(visible_text(chunk)))) for name, chunk in result]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file', type=Path)
    parser.add_argument('--min', type=int, default=3000, help='lower target, with spaces (default 3000)')
    parser.add_argument('--max', type=int, default=4000, help='upper target, with spaces (default 4000)')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--text', action='store_true', help='print the text that was counted')
    args = parser.parse_args()

    source = args.file.read_text(encoding='utf-8')
    text_paragraphs = paragraphs(visible_text(source))
    with_spaces = sum(len(p) for p in text_paragraphs)
    without_spaces = sum(len(re.sub(r'\s', '', p)) for p in text_paragraphs)
    words = sum(len(p.split()) for p in text_paragraphs)
    by_section = sections(source)

    if with_spaces < args.min:
        verdict = f'{args.min - with_spaces} under the {args.min}–{args.max} target'
    elif with_spaces > args.max:
        verdict = f'{with_spaces - args.max} over the {args.min}–{args.max} target'
    else:
        verdict = f'within the {args.min}–{args.max} target'

    if args.json:
        print(json.dumps({
            'file': str(args.file), 'characters': with_spaces, 'characters_without_spaces': without_spaces,
            'words': words, 'paragraphs': len(text_paragraphs), 'target': [args.min, args.max],
            'verdict': verdict, 'sections': [{'section': s, 'characters': n} for s, n in by_section],
        }, ensure_ascii=False, indent=2))
        return
    if args.text:
        print('\n\n'.join(text_paragraphs), end='\n\n---\n')
    print(f'{args.file}: {with_spaces} characters with spaces ({verdict})')
    print(f'{without_spaces} without spaces, {words} words, {len(text_paragraphs)} paragraphs\n')
    for name, count in by_section:
        print(f'{count:>6}  {name}')


if __name__ == '__main__':
    sys.exit(main())
