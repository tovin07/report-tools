# Report tools for OpenStack team

## Overview flow

```
Sorted markdown files --> concatenatenation --> compilation to html
```

## File organize for reports

`raws` directory contains all the raw reports.

Other directory is output of the report of the week that run this script.

```
reports
    |-- raws
    |   |-- template.html
    |   |-- tasks
    |   |   |-- 01.md
    |   |   |-- 02.md
    |   |   |-- 03.md
    |   |   \-- ...
    |   |
    |   \-- others
    |       |-- issues.md
    |       |-- contributions.md
    |       \-- ...
    |
    |-- 20180413_WeeklyReport
    |   |-- TeamName_WeeklyReport_20180413.html
    |   \-- TeamName_WeeklyReport_20180413.md
    |
    |-- 20180420_WeeklyReport
    |   |-- TeamName_WeeklyReport_20180420.html
    |   \-- TeamName_WeeklyReport_20180420.md
    |
    \-- ...
```

## Run the code

```shell
$ python report.py /path/to/reports/raws
Weekly report is generated in 20180420_WeeklyReport directory.
```
