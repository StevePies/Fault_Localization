# -*- coding: utf-8 -*-
import requests
import json

data={
	"racId": "0000048",
	"type": "terminal",
	"name":"ceshi",
	"model": "iswift",
	"startTime": "20200103002100",
	"endTime": "20200103002400",
	"kpi": "OUT_FLOW",
	"remarks":"test remarks"
}
print(data)
url="http://127.0.0.1:8383/api/rcaService"
data_json = json.dumps(data)
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=data_json, headers=headers)
print(response.text)
