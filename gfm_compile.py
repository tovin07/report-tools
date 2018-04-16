import argparse
import codecs
import requests


GITHUB_API_URL = 'https://api.github.com/markdown'

PREFIX_CSS = '''
<link rel="stylesheet" type="text/css" href="https://cdn.rawgit.com/charliebr30
/57e188334dcf9570383354ada93baa37/raw/5bca7bc87ee58339846e19722f2b8ddf2e09edb8/
github-markdown.css" media="screen" />
'''.strip().replace('\n', '') + '\n'


def parse_args():
    parser = argparse.ArgumentParser(description='Compile mardown with GFM')
    parser.add_argument(
        'markdown',
        type=str,
        default='in.md',
        help='Input markdown file name.'
    )

    parser.add_argument(
        '-o',
        '--html',
        dest='html',
        type=str,
        default='out.html',
        help='Output HTML file name.'
    )

    parser.add_argument(
        '-f',
        '--flavor',
        dest='flavor',
        type=str,
        default='markdown',
        help='Mardown flavor: markdown or gfm.'
    )

    return parser.parse_args()


def process_filename(markdown, html):
    if html != 'out.html':
        return html
    else:
        return markdown.replace('md', 'html')


def read_markdown(filename):
    with codecs.open(filename, mode='r', encoding='utf-8') as file:
        return file.read()


def compile_markdown(text, flavor):
    headers = {
        'Authorization': 'token dc2770ee692ba657d9a59f5351b41acda3010856'
    }

    payload = {
        'text': text,
        'mode': flavor
    }

    response = requests.post(
        GITHUB_API_URL,
        headers=headers,
        json=payload,
    )

    return response.text


def compile(markdown):
    html_text = compile_markdown(markdown, 'gfm')
    html = beautify(html_text)
    return html


def beautify(text):
    # Replace all id header prefix of github with empty string -- fcuk github
    return text.replace('user-content-', '')


def write_html(filename, text):
    with codecs.open(filename, mode='w', encoding='utf-8') as file:
        file.write(PREFIX_CSS)
        file.write(text)


def main():
    args = parse_args()
    html = process_filename(args.markdown, args.html)
    try:
        markdown_text = read_markdown(args.markdown)
        html_text = compile_markdown(markdown_text, args.flavor)
        text = beautify(html_text)
        write_html(html, text)
        print('Compilation finished. Please open output html file in browser.')
    except:
        print('Whoops, sum ting wong!!! Please try your luck again.')


if __name__ == '__main__':
    main()
