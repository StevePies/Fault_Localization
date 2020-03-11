#!/usr/bin/python
# -*- coding: UTF-8 -*-

from subprocess import *
import pandas as pd
import itertools,math,sys,datetime
from model.iswift import iswift 
from util.db_util import MysqldbHelper
import util.es_load 
import os, sys,logging,time,MySQLdb
                    
reload(sys)  
sys.setdefaultencoding('utf8')  

now = time.strftime("%Y%m%d", time.localtime(time.time()))
logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
                    format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s-%(thread)d:%(message)s',
                    filename = 'logs/'+now+'.log',
                    filemode = 'a')
 
class Locate:
    def __init__(self, _task_id,_type,_name,_model,_start,_end,_kpi,_remark):
        self._task_id = _task_id
        self._type = _type
        self._name = _name
        self._model = _model
        self._start = _start
        self._end = _end
        self._kpi = _kpi
        self._remark = _remark
        self.create_time= datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.init_database()
        
    def init_database(self):
        self.db=MysqldbHelper()   
        sql = "UPDATE rca_task_table SET state = '0' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        logging.info(str(self._task_id)+" status: init_database")


    def getDataFromES(self):
        self.list = []
        try:
            es_data = util.es_load.search(self._start,self._end,self._kpi)
            for item in es_data:
                temp_list = []
                #TODO
                temp_list.append(item['DOMAIN'])
                temp_list.append(item['province'])            
                temp_list.append(item['user_type'])
                temp_list.append(item['os'])
                temp_list.append(item['cdnserver'])
                temp_list.append(item[self._kpi])
                if(int(item[self._kpi+'_ERROR']) == -1):
                    temp_list.append(0)
                else:
                    temp_list.append(int(item[self._kpi+'_ERROR']))
                #temp_list.append(item['TIMESTAMP'])
                self.list.append(temp_list)

            sql = "UPDATE rca_task_table SET state = '1' WHERE rcaId = '"+self._task_id+"'"
            self.db.update(sql)

            logging.info(str(self._task_id)+" get data from es successful!")
            path = "data/"+self._task_id

            tt = pd.DataFrame(data=self.list)
            if not os.path.exists(path):
                os.makedirs(path)
            tt.to_csv(path+"/es_dl.csv",encoding="utf-8",index=None,columns=None)
        except Exception as e:
            sql = "UPDATE rca_task_table SET state = '4' WHERE rcaId = '"+self._task_id+"'"
            self._remark = self._remark + "-—es download data error"
            self.db.update(sql)
            logging.error(str(self._task_id)+" es load error\n"+str(e))

       
    def dimCombination(self,dim_arr,i):
        result = []
        for j in itertools.combinations(dim_arr, i):
            _list = list(j)
            result.append(_list)
        return result
 
    def groupby_3d(self):
        self.d3_tree = []
        if(len(self.list) == 0):
            return
        
        #TODO
        merge_df = pd.DataFrame(self.list,columns=['DOMAIN', 'province', 'user_type', 'os', 'cdn_server','value','error'])
    
        ix =  ['DOMAIN', 'province', 'user_type', 'os', 'cdn_server']
        
        for i in range (1,6):
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
        
        path = "data/"+self._task_id
        tt = pd.DataFrame(data=self.d3_tree)
        if not os.path.exists(path):
            os.makedirs(path)
        tt.to_csv(path+"/d3_tree.csv",encoding="utf-8",index=None,columns=None)
    
        logging.info(str(self._task_id)+" status: groupby finished!")
        sql = "UPDATE rca_task_table SET state = '2' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
                    
    def algorithm(self):
        #TODO
        sql = "UPDATE rca_task_table SET state = '3' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
        logging.info(str(self._task_id)+" status: start iswift")
        d3_path = "data/" + self._task_id + "/d3_tree.csv"
        es_path = "data/" + self._task_id + "/es_dl.csv"
        p = Popen(['python', 'offline_iswift.py',d3_path,es_path],
                stdin=PIPE,
                stdout=PIPE,
                )
        p.wait()
        rt = p.stdout.read()
    
        self.result = MySQLdb.escape_string(rt)

        self.over_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        sql = "UPDATE rca_task_table SET state = '9',overTime = '"+self.over_time+"',result = '"+str(self.result)+"' WHERE rcaId = '"+self._task_id+"'"
        self.db.update(sql)
    

        