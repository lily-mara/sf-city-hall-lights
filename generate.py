#!/usr/bin/env python3

from bs4 import BeautifulSoup
import re
from datetime import date
import requests

def main():
    resp = requests.get('https://www.sf.gov/location/san-francisco-city-hall')
    html = resp.text

    soup = BeautifulSoup(html, features="html.parser")
    summary = soup.find('summary', string='Lighting schedule')
    if not summary:
        exit(1)

    schedule = summary.parent
    if not schedule:
        exit(1)

    date_line_regex = re.compile(r'([^–-]*) (-|–) ([^–-]*) (-|–) ((in recognition of )?(the )?(.*))')
    date_regex = re.compile(r'((January|February|March|April|May|June|July|September|October|November|December)\s*(\d+)(,?\s*(\d{4}))? through \w*,\s*)?(January|February|March|April|May|June|July|September|October|November|December)\s*(\d+),?\s*(\d{4})')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    for p in schedule.find_all('p'):
        m = date_line_regex.match(p.text)
        if m:
            groups = m.groups()
            date_part = groups[0]
            color = groups[2]
            reason = groups[7]


            m = date_regex.search(date_part)
            if m:
                groups = m.groups()
                start_month = groups[1]
                start_day = groups[2]
                start_year = groups[4]

                end_month = groups[5]
                end_day = groups[6]
                end_year = groups[7]

                end_month_no = months.index(end_month) + 1

                end_date = date(year=int(end_year), month=end_month_no, day=int(end_day))

                start_date = end_date
                if start_day:
                    start_month_no = months.index(start_month) + 1

                    start_date = date(year=int(start_year or end_year), month=start_month_no, day=int(start_day))

                with open(f'content/event/{start_date}.md', 'w') as f:
                    contents = f"""---
title: "{reason} - {color}"
start: "{start_date}"
end: "{end_date}"
color: "{color.split('/')[0]}"
allday: true
---
"""
                    print(contents, file=f)


if __name__ == "__main__":
    main()
