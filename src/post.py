# -*- coding: utf-8 -*-
import requests
import json

data={
	"racId": "12370",
	"type": "web",
	"name":"locate",
	"model": "iswift",
	"startTime": "20190610113700",
	"endTime": "20190610114000",
	"kpi": "OUT_FLOW",
	"remarks":"This is remarks"
}
print(data)
#url="http://127.0.0.1:8383/locate"
url="http://10.10.27.130:8383/api/rcaService"
data_json = json.dumps(data)
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=data_json, headers=headers)

print(response.text)
