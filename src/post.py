# -*- coding: utf-8 -*-
import requests
import json

data={
	"task_id": "12356",
	"type": "0",
	"name":"123",
	"model": "iswift",
	"start": "20190610113700",
	"end": "20190610114000",
	"kpi": "OUT_FLOW"
}
print(data)
#url="http://127.0.0.1:8383/locate"
url="http://10.10.27.130:8383/locate"
data_json = json.dumps(data)
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=data_json, headers=headers)

print(response.text)
