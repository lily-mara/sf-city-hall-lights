---
title: "{{ replace .Name "-" " " | title }}"
start: {{ .Date }} # start date
end: {{ dateFormat "2006-01-02T15:04:05" (now.AddDate 0 0 +1) }} # expire date
color: 'pink'

allday: true
---
