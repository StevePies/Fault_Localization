#!/usr/bin/python
# -*- coding: UTF-8 -*-
import elasticsearch
import es_client
from elasticsearch import helpers
import yaml 

ES_SERVERS = [{
    #'host': '39.137.77.252',
    'host': '10.10.26.43',
    'port': 9200
}]

es_client = elasticsearch.Elasticsearch(
    hosts=ES_SERVERS
)

def search(start,end,kpi):
    file = open("config/config.yaml")
    config = yaml.load(file)
    file.close()
    env = config["currentEnv"]

    es_ip = config["env"][env]["es_ip"]
    es_index = config["env"][env]["es_index"]
    ES_SERVERS[0]['host'] = (es_ip)
    
    #es_index = "anomaly-result-2019.12.25-final"
    #es_index = "anomaly-result-new"
    es_search_options = set_search_optional(start,end,kpi)
    es_result = get_search_result(es_search_options,index = es_index)
    final_result = get_result_list(es_result)
    return final_result


def get_result_list(es_result):
    final_result = []
    for item in es_result:
        final_result.append(item['_source'])
    return final_result


def get_search_result(es_search_options, index='anomaly-result'):
    print(index,ES_SERVERS)
    es_result = helpers.scan(
        client=es_client,
        query=es_search_options,
        scroll='5m',
        index=index,
#        doc_type=doc_type,
        timeout="1m"
    )
    return es_result


def set_search_optional(start,end,kpi):
    # 检索选项
    es_search_options = {
                        "query": {
                            "range": {
                                "TIMESTAMP": {
                                    "gte": "20190820000000",
                                    "lte": "20190909000000"
                                }
                                
                            }
                        },
                        "_source": ["TIMESTAMP", "DOMAIN", "province", "user_type", "os", "cdnserver"]
                    }
    es_search_options['query']["range"]["TIMESTAMP"]["gte"]=int(start)
    es_search_options['query']["range"]["TIMESTAMP"]["lte"]=int(end)
    es_search_options["_source"].append(kpi)
    es_search_options["_source"].append(kpi+"_ERROR")
    print(es_search_options)
    return es_search_options

