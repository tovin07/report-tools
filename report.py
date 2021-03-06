import argparse
import codecs
import datetime
import jinja2
import os
import re

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
TOC_HEADING = '## <a id="toc"></a> Table of contents'
SECTION_SEP = '\n\n'
WEEKLY_REPORT = 'WeeklyReport'
CURRENT_WEEK = 'Current week: [{} - {} | R-{}]({})'
CYCLE_SCHEDULE = 'https://releases.openstack.org/rocky/schedule.html'


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


def get_heading(first_line):
    return re.split(r'\s+', first_line.strip(), maxsplit=1)[-1]


def create_anchor_id(directory, file_name,):
    return '-'.join([directory, re.sub(r'\s+', '-', file_name.split('.')[0])])


def add_anchor_tag(anchor_id, header):
    """
    Add anchor tag to header.
    Input and output will look like below.

    Input:
        ## Task 02 - Do something

    Output:
        ## <a id="task02"></a> Task 02 - Do something [^](#toc)
    """
    anchor = ANCHOR.format(anchor_id)
    # Replace the first space with anchor tag
    header_with_anchor = header.replace(' ', anchor, 1)
    return ' '.join([header_with_anchor.strip(), TOC])


def get_date_of_week(date_of_week):
    """
    Return the date of this week.

    Input:
        date_of_week: Offset of the date with base 0
                      0 is for Monday
                      ...
                      6 is for Sunday

    Output example: 2018/04/20
    """
    today = datetime.date.today()
    date = today + datetime.timedelta(date_of_week - today.weekday())
    return date


def create_current_week():
    _, remaining_weeks = sc.calculate_passed_time()
    monday = get_date_of_week(0).strftime("%b %d")
    friday = get_date_of_week(4).strftime("%b %d")
    return CURRENT_WEEK.format(monday, friday, remaining_weeks, CYCLE_SCHEDULE)


def generate_toc(headings, anchor_ids):
    """
    Generate table of contents.

    Input:
        headings: List of headings
        anchor_ids: List of anchor ids

    Output:
        Markdown string with table of contents look like below

        ```markdown
        ## <a id="toc"></a> Table of contents

        1. [Task 01 - Do do](#tasks-01)
        2. [Task 02 - Da da](#tasks-02)
        3. [Task 03 - Young wild and free](#tasks-03)
        4. [Contributions](#others-contributions)
        5. [IRC meetings](#others-irc-meeeting)
        6. [Issues](#others-issues)
        ```
    """
    contexts = zip(range(1, len(headings) + 1), headings, anchor_ids)
    toc_entries = [
        '{}. [{}](#{})'.format(order, heading, anchor_id)
        for order, heading, anchor_id in contexts
    ]
    return '\n\n'.join([TOC_HEADING, '\n'.join(toc_entries)])


def read_markdown_files(files):
    """
    Read all markdown files and concatenate to one file.

    Return:
        markdown contents, headings, anchor ids for those headings
    """
    contents = []
    headings = []
    anchor_ids = []
    for directory, file_name, abs_file_path in files:
        with codecs.open(abs_file_path, mode='r', encoding='utf-8') as md:
            anchor_id = create_anchor_id(directory, file_name)
            # First line is section header --> Add anchor tag to it
            first_line = md.readline()
            header = add_anchor_tag(anchor_id, first_line)
            contents.append('\n'.join([header, md.read()]))
            headings.append(get_heading(first_line))
            anchor_ids.append(anchor_id)

    return '\n'.join(contents), headings, anchor_ids


def render_string(contents, team_table, member_table):
    """
    Using jinja2 to render markdown template in contribution file.
    """
    template = jinja2.Environment().from_string(contents)
    return template.render(team_table=team_table, member_table=member_table)


def render_html(path, html_body):
    """
    Using jinja2 to render html template.

    path: Path to directory that contains template
    title: Team title, use for html title and team title in h1
    html_body: All the content of the report

    returns: html text
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = env.get_template(TEMPLATE)
    return template.render(title=TITLE, body=html_body)


def save(target, title, markdown, html):
    friday = get_date_of_week(4).strftime("%Y%m%d")
    report_dir = '_'.join([friday, WEEKLY_REPORT])
    directory = os.path.join(target, report_dir)
    file_name = '_'.join([title.replace(' ', '_'), friday])
    file_path = os.path.join(target, report_dir, file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    write_file(file_path + '.md', markdown)
    write_file(file_path + '.html', html)

    # Print done message
    print("Weekly report is generated in {} directory.".format(directory))


def write_file(path, content):
    with codecs.open(path, mode='w', encoding='utf-8') as f:
        f.write(content)


def main():
    # Just arguments
    args = parse_args()

    # List all the markdown file from tasks and others directory
    files = list_files(args.path)

    # Heading of markdown file
    title = ' '.join(['#', TITLE])

    # Current week string
    week = create_current_week()

    # All the markdown content from raws
    markdown_contents, headings, anchor_ids = read_markdown_files(files)

    # Generate TOC from headings and anchor ids
    tocs = generate_toc(headings, anchor_ids)

    # Make contents
    contents = SECTION_SEP.join([title, week, tocs, markdown_contents])

    # Get contribution information
    team_table, member_table = sc.generate_data_table()

    # Fill contribution information to contribution markdown
    markdown = render_string(contents, team_table, member_table)

    # Compile markdown content to html
    html_body = gfm_compile.compile(markdown)

    # Render template from html
    html = render_html(args.path.rstrip('/'), html_body)

    # Save markdown and html content to target directory
    dir_name = os.path.dirname(args.path.rstrip('/'))
    save(dir_name, TITLE, markdown, html)


if __name__ == '__main__':
    main()
