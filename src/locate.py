#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import itertools,math,sys,datetime
from model.iswift import iswift 
from util.db_util import MysqldbHelper
import util.es_load 

reload(sys)  
sys.setdefaultencoding('utf8')   

class Locate:
    def __init__(self, _task_id,_type,_name,_model,_start,_end,_kpi):
        self._task_id = _task_id
        self._type = _type
        self._name = _name
        self._model = _model
        self._start = _start
        self._end = _end
        self._kpi = _kpi
        self.create_time= datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.init_database()
        
    def init_database(self):
        self.db=MysqldbHelper()   
        sql = "insert into rca_task_table (rcaId,type,name,startTime,endTime,kpi,model,createtime,state) values ('"+\
            self._task_id+"','"+self._type+"','"+self._name+"','"+self._start+"','"+self._end+"','"+self._kpi+"','"+self._model+"','"+self.create_time+"','"+str(0)+"')"
        self.db.update(sql)
        print(sql)

    def getDataFromES(self):
        self.list = []
        es_data = util.es_load.search(self._start,self._end,self._kpi)
        for item in es_data:
            temp_list = []
            
            #TODO
            #字段可能为空 需要判断
            #之后error字段可以直接获取，需要修改
            temp_list.append(item['DOMAIN'])
            temp_list.append(item['province'])            
            temp_list.append(item['user_type'])
            temp_list.append(item['os'])
            temp_list.append(item['cdn_srever'])
            #temp_list.append(item['error'])
            temp_list.append(item[self._kpi])
            if(float(item[self._kpi]) >10000):
                temp_list.append(0)
            else:
                temp_list.append(1)
            self.list.append(temp_list)
            #print(temp_list)

        print("get data from es successful!")

        sql = "UPDATE rca_task_table SET state = '1' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        print(sql)
       
    def dimCombination(self,dim_arr,i):
        result = []
        for j in itertools.combinations(dim_arr, i):
            _list = list(j)
            result.append(_list)
        return result
 
    def groupby_3d(self):
        #TODO
        merge_df = pd.DataFrame(self.list,columns=['DOMAIN', 'province', 'user_type', 'os', 'cdn_server','value','error'])
    
        ix =  ['DOMAIN', 'province', 'user_type', 'os', 'cdn_server']
        self.d3_tree = []
        for i in range (1,4):
            dim_combin_list = self.dimCombination(ix,i)
            #print(dim_combin_list)

            for item in dim_combin_list:
                _df = merge_df.groupby(item)['error'].value_counts().unstack()
                for index, row in _df.iterrows():
                    row_dict = row.to_dict()  
     
                    _temp_list=[]
                    _temp_list_2=[]
                    if 1 not in row_dict.keys():
                        row_dict[1]=0
                    if 0 not in row_dict.keys():
                        row_dict[0]=0
                    if math.isnan(row_dict[0]):
                        row_dict[0]=0
                    if math.isnan(row_dict[1]):
                        row_dict[1]=0
                    #print(index,type(index),isinstance(index,unicode))
                    if(isinstance(index,unicode)):
                        _temp_list_2.append(index)
                    if(isinstance(index,tuple)):
                        _temp_list_2 = list(index)

                    for i in ix:
                        if(i in item):
                            #print(i,ix,item)
                            _temp_list.append(_temp_list_2[item.index(i)])
                        else:
                            _temp_list.append("*")

                    _temp_list.append(row_dict[0])
                    _temp_list.append(row_dict[1])
                    #print(_temp_list)
                    self.d3_tree.append(_temp_list)
        
        #print("3d data length:"+str(len(self.d3_tree)))
        #print(self.list[0])
        #print(self.d3_tree[0])
        print("groupby finished!")
        sql = "UPDATE rca_task_table SET state = '2' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        print(sql)
                    
    def algorithm(self):
        #TODO
        
        ift = iswift(self.d3_tree,self.list)
        sql = "UPDATE rca_task_table SET state = '3' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        print(sql)
        rt = str(ift.run())
        import MySQLdb
        self.result = MySQLdb.escape_string(rt)

        self.over_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        sql = "UPDATE rca_task_table SET state = '9',overTime = '"+self.over_time+"',result = '"+str(self.result)+"' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        print(sql)

