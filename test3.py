#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

payload = {'city': u'上海', 'mobile': '13061938527','points':'25'}
while 1:
    r=requests.post('http://www.kissfromrose.com/icecream/signData.aspx',data=payload)
    print json.loads(r.text)['status']
    if json.loads(r.text)['status']!='5':
        break
