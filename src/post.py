# -*- coding: utf-8 -*-
import requests
import json

data={
	"racId": "0000041",
	"type": "item",
	"name":"12.25",
	"model": "iswift",
	#"startTime": "20200103002100",
	#"endTime": "20200103002400",
	"startTime": "20200109005900",
	"endTime": "20200109010100",
	"kpi": "CDN_EX_5XX_PER",
	#"kpi": "OUT_FLOW",
	#"kpi": "CDN_TTFB",
	#"kpi": "CDN_OUT_RATE",	
	"remarks":"This is remarks"
}
print(data)
#url="http://127.0.0.1:8383/locate"
url="http://10.10.27.130:8383/api/rcaService"
data_json = json.dumps(data)
headers = {'Content-type': 'application/json'}
response = requests.post(url, data=data_json, headers=headers)

print(response.text)
