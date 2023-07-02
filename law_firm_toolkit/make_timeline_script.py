import datetime

import timeline

dates = {}
while True:
    raw_input = input('Enter date dd/mm/yyyy and event separated by coma.')
    if raw_input.strip().lower() in ['q', 'quit']:
        break
    date, event = raw_input.split(',')
    date = [int(_) for _ in date.strip().split('/')]
    date.reverse()
    event = event.strip()
    dates[datetime.date(*date)] = event

title = input('Enter plot title.')

timeline.export_timeline(dates, title)
