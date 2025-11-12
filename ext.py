import fitz, re, json, sys
from collections import defaultdict
print('Extracting 1028 classes from 82 pages...')
doc = fitz.open('MTT_2526S1_V2_20250911.pdf')
groups = defaultdict(lambda: {'code':'','classNo':'','name':'','weekday':0,'times':[],'room':''})
current = {'code':'','classNo':'','name':''}

for page in doc:
    lines = [l.strip() for l in page.get_text().split('\n') if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^[A-Z]{4}\d{4}$', line):
            current['code'] = line
            i += 1
            if i < len(lines) and re.match(r'^(CL|CT)\d+$', lines[i]):
                current['classNo'] = lines[i]
                i += 1
            if i < len(lines):
                current['name'] = lines[i]
                i += 1
            continue
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 5 and parts[0] == '1' and current['code']:
            try:
                weekday = int(parts[1])
                time_str = ' '.join(parts[2:4])
                room = parts[-1]
                times = re.findall(r'\d{2}:\d{2}', time_str)
                if len(times) == 2:
                    key = (current['code'], current['classNo'], weekday)
                    g = groups[key]
                    g.update(current)
                    g['weekday'] = weekday
                    g['room'] = room
                    g['times'].append(times)
            except: pass
        i += 1

courses = []
for key, g in groups.items():
    if not g['times']: continue
    times = sorted(g['times'])
    start = times[0][0]
    end = times[0][1]
    for t in times[1:]:
        if int(t[0].replace(':','')) <= int(end.replace(':','')) + 10:
            end = t[1]
    courses.append({
        'code': g['code'],
        'classNo': g['classNo'],
        'name': g['name'],
        'weekday': g['weekday'],
        'startTime': start,
        'endTime': end,
        'room': g['room']
    })

courses.sort(key=lambda x: (x['code'], x['classNo'], x['weekday']))

with open('courses.js', 'w', encoding='utf-8') as f:
    f.write('const courses = ' + json.dumps(courses, ensure_ascii=False) + ';\n')
print(f'SUCCESS! {len(courses)} classes → courses.js')

