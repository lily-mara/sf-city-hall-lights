#!/usr/bin/env python3

from typing import Optional, Union
from bs4 import BeautifulSoup
import re
from datetime import date
import requests
import sys

def main():
    headers = {}

    etag = read_etag()
    if etag:
        headers['If-None-Match'] = etag

    resp = requests.get('https://www.sf.gov/location/san-francisco-city-hall', headers=headers)
    if resp.status_code == 304:
        print('Got 304, no new contents')
        sys.exit(0)

    if resp.status_code != 200:
        print(f'Got non-OK status code from sf.gov! status={resp.status_code}')
        print('\n=====\n')
        print(resp.text)
        print('\n=====\n')
        sys.exit(1)

    html = resp.text

    soup = BeautifulSoup(html, features="html.parser")

    with open('city-hall.html', 'w') as f:
        f.write(soup.prettify())

    write_events(soup)

    write_etag(resp)


def write_events(soup: BeautifulSoup):
    heading = soup.find('h3', string='Lighting schedule')
    if not heading:
        raise ValueError('Page was missing "lighting schedule" h3 node')

    summary = heading.parent
    if not summary:
        raise ValueError('Page was missing "lighting schedule" h3 node\'s summary parent')

    schedule = summary.parent
    if not schedule:
        raise ValueError('Page missing details node')

    date_line_regex = re.compile(r'([^–-]*) (-|–) ([^–-]*) (-|–) ((in recognition of )?(the )?(.*))')
    date_regex = re.compile(r'((January|February|March|April|May|June|July|September|October|November|December)\s*(\d+)(,?\s*(\d{4}))? through \w*,\s*)?(January|February|March|April|May|June|July|September|October|November|December)\s*(\d+),?\s*(\d{4})')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    for p in schedule.find_all('p'):
        m = date_line_regex.match(p.text)
        if m:
            groups = m.groups()
            date_part = groups[0]
            color = groups[2]
            reason = groups[7].replace('"', '\\"')


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


def read_etag() -> Optional[str]:
    try:
        with open('.etag') as f:
            return f.read().strip()
    except Exception as e:
        print(f'Failed to load ETag: {e}')
        return None


def write_etag(response: requests.Response):
    etag = response.headers.get('ETag', None)
    if not etag:
        return

    try:
        with open('.etag', 'w') as f:
            f.write(etag.strip())
    except Exception as e:
        print(f'Failed to save ETag: {e}')


if __name__ == "__main__":
    main()
