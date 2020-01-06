# -*- coding: utf-8 -*-
import requests
import json

data={
	"racId": "1233432323455",
	"type": "item",
	"name":"locate",
	"model": "iswift",
	"startTime": "20191225200000",
	"endTime": "20191225200500",
	"kpi": "CDN_EX_5XX_PER",
	"remarks":"This is remarks"
}
print(data)
#url="http://127.0.0.1:8383/locate"
url="http://10.10.27.130:8383/api/rcaService"
data_json = json.dumps(data)
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=data_json, headers=headers)

print(response.text)
