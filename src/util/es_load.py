#!/usr/bin/python
# -*- coding: UTF-8 -*-
import elasticsearch
import es_client
from elasticsearch import helpers

ES_SERVERS = [{
    'host': '39.137.77.252',
    'port': 9200
}]

es_client = elasticsearch.Elasticsearch(
    hosts=ES_SERVERS
)

def search(start,end,kpi):
    es_search_options = set_search_optional(start,end,kpi)
    es_result = get_search_result(es_search_options)
    final_result = get_result_list(es_result)
    return final_result


def get_result_list(es_result):
    final_result = []
    for item in es_result:
        final_result.append(item['_source'])
    return final_result


def get_search_result(es_search_options, scroll='5m', index='result-from-module2', doc_type='doc', timeout="1m"):
    es_result = helpers.scan(
        client=es_client,
        query=es_search_options,
        scroll=scroll,
        index=index,
#        doc_type=doc_type,
        timeout=timeout
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

