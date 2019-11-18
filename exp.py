es_search_options = {
                        "query": {
                            "range": {
                                "TIMESTAMP": {
                                    "gte": "20190820000000",
                                    "lte": "20190909000000"
                                }
                                
                            }
                        },
                        "_source": ["TIMESTAMP", "DOMAIN", "province", "user_type", "os", "cdn_srever"]
                    }

print(es_search_options['query']["range"]["TIMESTAMP"]["gte"])
print(es_search_options['query']["range"]["TIMESTAMP"]["lte"])
print(es_search_options['_source'])

es_search_options['query']["range"]["TIMESTAMP"]["gte"]=20190909000000
es_search_options['query']["range"]["TIMESTAMP"]["lte"]=20190820000000
es_search_options["_source"].append("OUT_FLOW")
print(es_search_options['query']["range"]["TIMESTAMP"]["gte"])
print(es_search_options['query']["range"]["TIMESTAMP"]["lte"])
print(es_search_options['_source'])