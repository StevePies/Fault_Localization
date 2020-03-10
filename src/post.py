# -*- coding: utf-8 -*-
import requests
import json

data={
	"racId": "0000048",
	"type": "terminal",
	"name":"ceshi",
	"model": "iswift",
	"startTime": "20200309143900",
	"endTime": "20200309144000",
	"kpi": "OUT_RATE",
	"remarks":"test remarks"
}
for i in range(0,10):
	data['racId'] = str(int(data['racId'])+1)

	print(data)
	url="http://127.0.0.1:8383/api/rcaService"
	data_json = json.dumps(data)
	headers = {'Content-type': 'application/json'}
	response = requests.post(url, data=data_json, headers=headers)
	print(response.text)
