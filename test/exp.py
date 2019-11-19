
import pandas as pd
import itertools,math

class TTT:
    def dimCombination(self,dim_arr,i):
            result = []
            for j in itertools.combinations(dim_arr, i):
                _list = list(j)
                result.append(_list)
            return result
    
    def groupby_3d(self):
        #TODO

        merge_df = pd.read_csv("./merge.csv")
        #merge_df = pd.DataFrame(self.list,columns=['DOMAIN', 'province', 'user_type', 'os', 'cdn_server','value','error'])
        ix =  ['DOMAIN', 'province', 'user_type', 'os', 'cdn_server']
        self.d3_tree = []
        for i in range (1,4):
            dim_combin_list = self.dimCombination(ix,i)
            #print(dim_combin_list)
            for item in dim_combin_list:
                _df = merge_df.groupby(item)['error'].value_counts().unstack()
                for index, row in _df.iterrows():
                    row_dict = row.to_dict()  
                    #print(index,row_dict)          
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
                    
                    for i in ix:
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

if __name__ == "__main__":
    tt = TTT()
    tt.groupby_3d() 