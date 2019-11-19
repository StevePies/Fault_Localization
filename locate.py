# -*- coding: utf-8 -*-
import es_load 
import pandas as pd
import itertools,math

class Locate:
    def __init__(self, _task_id,_type,_model,_start,_end,_kpi):
        self._task_id = _task_id
        self._type = _type
        self._model = _model
        self._start = _start
        self._end = _end
        self._kpi = _kpi
       
    def getDataFromES(self):
        self.list = []
        es_data = es_load.search(self._start,self._end,self._kpi)
        for item in es_data:
            temp_list = []
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
        print(self.list[0])
        print("get data from es successful!")
       
    def dimCombination(self,dim_arr,i):
        result = []
        for j in itertools.combinations(dim_arr, i):
            _list = list(j)
            result.append(_list)
        return result
 
    def groupby_3d(self):
        #TODO
        merge_df = pd.DataFrame(self.list,columns=['DOMAIN', 'province', 'user_type', 'os', 'cdn_server','error','value'])
        index =  ['DOMAIN', 'province', 'user_type', 'os', 'cdn_server']
        self.d3_tree = []
        for i in range (1,4):
            dim_combin_list = self.dimCombination(index,i)
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
                    
                    if(isinstance(index,int)):
                        index=str(index)
                    if(isinstance(index,str)):
                        _temp_list_2.append(index)
                    else:
                        _temp_list_2=list(index)
                    
                    for i in index:
                        if(i in item):
                            _temp_list.append(_temp_list_2[item.index(i)])
                        else:
                            _temp_list.append("*")
                    _temp_list.append(row_dict[0])
                    _temp_list.append(row_dict[1])
                    #print(temp)
                    #print("+++++")
                    print(_temp_list)
                    self.d3_tree.append(_temp_list)

        
    def iswift(self):
        #TODO
        i=0


    def insert_to_db(self):
        #TODO
        i=0

if __name__ == "__main__":
    locate = Locate(1,1,1,20190610083800,20190610084500,"OUT_FLOW")
    locate.getDataFromES()
    locate.groupby_3d()