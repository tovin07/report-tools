import argparse
import codecs
import datetime
import jinja2
import os

import gfm_compile
import stackalytics_contribution.main as sc


# Magic strings go here
TASKS = 'tasks'
OTHERS = 'others'
CONTRIBUTIONS = 'contributions'
ISSUES = 'issues'
TEMPLATE = 'template.html'

TITLE = 'Container and Troubleshooting team weekly report'
ANCHOR = ' <a id="{}"></a> '
TOC = '[^](#toc)'


def parse_args():
    parser = argparse.ArgumentParser(description="Just generate report.")
    parser.add_argument(
        'path',
        help='The absolute path to raw directory.',
        type=str
    )
    return parser.parse_args()


def list_files(path):
    """
    Fcuk it, full of magic.

    Return:
        List of files with format (directory, file_name, absolute_file_path)
    """
    files = []
    for directory in [TASKS, OTHERS]:
        sub_dir = os.path.join(path, directory)
        mds = sorted(list(os.walk(sub_dir))[0][2])
        # Directory, file name, absolute file path
        files.extend([(directory, f, os.path.join(sub_dir, f)) for f in mds])
    return files


def add_anchor_tag(directory, file_name, header):
    """
    Add anchor tag to header.
    Input and output will look like below.

    Input:
        ## Task 02 - Do something

    Output:
        ## <a id="task02"></a> Task 02 - Do something [^](#toc)
    """
    id_attr = '-'.join([directory[:-1], file_name.split('.')[0]])
    anchor = ANCHOR.format(id_attr)
    # Replace the first space with anchor tag
    header_with_anchor = header.replace(' ', anchor, 1)
    return ' '.join([header_with_anchor.strip(), TOC])


def generate_toc():
    return ''


def get_friday_date():
    """Return the friday date of this week."""
    today = datetime.date.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7)
    return friday.strftime('%Y%m%d')


def read_markdown_files(files):
    """
    Read all markdown files and concatenate to one file.
    """
    contents = []
    for directory, file_name, abs_file_path in files:
        with codecs.open(abs_file_path, mode='r', encoding='utf-8') as md:
            # First line is section header --> Add anchor tag to it
            header = add_anchor_tag(directory, file_name, md.readline())
            contents.append('\n'.join([header, md.read()]))
    return '\n\n'.join(contents)


def render_string(contents, team_table, member_table):
    """
    Using jinja2 to render markdown template in contribution file.
    """
    template = jinja2.Environment().from_string(contents)
    return template.render(team_table=team_table, member_table=member_table)


def render_html(path, title, html_body):
    """
    Using jinja2 to render html template.

    path: Path to directory that contains template
    title: Team title, use for html title and team title in h1
    html_body: All the content of the report

    returns: html text
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = env.get_template(TEMPLATE)
    return template.render(title=title, body=html_body)


def save(target, title, markdown, html):
    friday = get_friday_date()
    directory = os.path.join(target, friday)
    file_name = '_'.join([title.replace(' ', '_'), friday])
    file_path = os.path.join(target, friday, file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    write_file(file_path + '.md', markdown)
    write_file(file_path + '.html', html)


def write_file(path, content):
    with codecs.open(path, mode='w', encoding='utf-8') as f:
        f.write(content)


def main():
    # Just arguments
    args = parse_args()

    # List all the markdown file from tasks and others directory
    files = list_files(args.path)

    # Heading of markdown file
    heading = ' '.join(['#', TITLE])

    # Current week
    # current_week = ' '

    # All the markdown content from raws
    markdown_contents = read_markdown_files(files)
    # contents = '\n\n'.join([heading, current_week, markdown_contents])
    contents = '\n\n'.join([heading, markdown_contents])

    # Get contribution information
    team_table, member_table = sc.generate_data_table()

    # Fill contribution information to contribution markdown
    markdown = render_string(contents, team_table, member_table)

    # Compile markdown content to html
    html_body = gfm_compile.compile(markdown)

    # Render template from html
    html = render_html(args.path.rstrip('/'), TITLE, html_body)

    # Save markdown and html content to target directory
    dir_name = os.path.dirname(args.path.rstrip('/'))
    save(dir_name, TITLE, markdown, html)

if __name__ == '__main__':
    main()
