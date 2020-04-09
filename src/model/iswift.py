#/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function  
import pandas as pd
import numpy as np
import yaml,itertools,csv,datetime,math,json,time,io,sys  


reload(sys)  
sys.setdefaultencoding('utf8')
class iswift:
    def __init__(self,dims_list,merge_list):
        self.merge_list = merge_list 
        self.dims_list = dims_list

        self.init_from_config()
        self.getStartList()
        self.calcErrorItem()

    def init_from_config(self):

        self.dims_len = 5
        self.A = 0.1
        self.B = 1
        self.cut_threshold = 0.001
        self.supTHR = 0
        self.conTHR = 0.50
        self.con_combine_thr = 0.15
        self.topK = 300
        self.for_num = 2



    #返回维度信息
    # qq.com,shandong,*,*,android -> return 3
    def getListLen(self,_list):
        i=0
        for item in _list:
            if item != "*":
                i= i+1
        return i

    #一维数据
    def getStartList(self):
        self.start_list = []
        for item in self.dims_list:
            
            if(self.getListLen(item[0:5]) == 1):
                #print(item[0:5],self.getListLen(item[0:5]))
                self.start_list.append(item)
        
    #计算error_item
    def calcErrorItem(self):
        self.error_item = 0
        for item in self.merge_list:
            #print(int(item[-1]))
            if(int(item[-1])==1):
                self.error_item =  self.error_item +1
        #print(self.error_item)
        
    #将排过序的集合中前K项组合加入候选集合，并在搜索集合中删除其中元素
    def getCandidateList(self,search_set_sorted):
        i=0
        result=[]
        topK=[]
        for item in search_set_sorted:
            if(i==self.topK):
                break
            temp = item[0].split("~")
            i=i+1
            topK.append(temp)

        #TOPK两两组合
        for i in range(0,len(topK)-1):
            for j in range(i+1,len(topK)):
                _list = []
                ##print (topK[i],topK[j])
                for k in range(0,self.dims_len):
                    if(topK[i][k]=="*" and topK[j][k]=="*"):
                        _list.append("*")
                        continue
                    elif(topK[i][k]!="*" and topK[j][k]!="*"):
                        if(topK[i][k] == topK[j][k]):
                            _list.append(topK[i][k])
                        else:
                            break
                    else:
                        if(topK[i][k]!="*"):
                            _list.append(topK[i][k])
                        else:
                            _list.append(topK[j][k])


                if(len(_list)==self.dims_len):
                    result.append(_list)
        return result
    
    def getDataFromList(self,item,_dims_list):    
        for i in _dims_list:
            if(item==i[0:self.dims_len]):
                return i[self.dims_len],i[self.dims_len+1]
        return -1,-1

    #推荐集合中儿子的support之和 儿子的平均confidence
    def subNodeCalc(self,ix1,ix1_conf):

        #print("进入儿子节点")
        conf_avg = 0
        support_sum = 0
        _list =  ix1.split("~")
        result_list = []
        #print("============")

        for item in self.dims_list:
            mark=0
            for i in range(0,len(_list)):
                if(_list[i]!="*" and _list[i]!=item[i]):
                    mark=1
                    break
            item_1 = self.getListLen(item[0:5])
            list_1 = self.getListLen(_list)

            if(mark==0 and _list!=item[0:5] and abs(item_1-list_1)==1 ):
                result_list.append(item)
            
        local_conf={}
        local_sup={}
        #print("所有的儿子信息：")
        if(self.error_item==0):
            return 0,0

        for item in result_list:
            ix = str(item[0])+"~"+str(item[1])+"~"+str(item[2])+"~"+str(item[3])+"~"+str(item[4])
            if((item[self.dims_len+1]+item[self.dims_len]) == 0):
                continue
            local_sup[ix]=float(item[self.dims_len+1])/float(self.error_item)
            local_conf[ix]=float(item[self.dims_len+1])/float(item[self.dims_len+1]+item[self.dims_len])
            #if("iphone.cmvideo.cn" in ix and 'Android' in ix):
                #print(ix,local_sup[ix],local_conf[ix])
            support_sum = support_sum+local_sup[ix]
            m = abs(local_conf[ix] - ix1_conf)
            conf_avg = conf_avg+m
        if len(result_list) == 0:
            return 0,0
        else:
            return float(conf_avg)/len(result_list),support_sum
    
    def removeChildfromList(self,ix):
        _list =  ix.split("~")

        remove_list = []
        for item in self.dims_list:
            mark=0
            for i in range(0,len(_list)):
                if(_list[i]!="*" and _list[i]!=item[i]):
                    mark=1
                    break

            if(mark==0):
                #print(item)
                remove_list.append(item)
                #dims_list.remove(item)
        for item in remove_list:
            self.dims_list.remove(item)

    def quick_sort(self,nums,latent_force):
        n = len(nums)
        if n ==1 or len(nums)==0:
            return nums  
        left = []
        right = []
        for i in range(1,n):
            if latent_force[nums[i]] >= latent_force[nums[0]]:
                left.append(nums[i])
            else:
                right.append(nums[i])         
        return self.quick_sort(left,latent_force)+[nums[0]]+self.quick_sort(right,latent_force)

    def run(self):
        latent_force = {}
        confidence_set = {}
        sp_set = {}
        recommond_list = []
        search_set = {}
        confidence_loss = {}
        #logging.info("error_item: "+str(self.error_item))
        if(self.error_item == 0):
            return []

        for item in self.start_list:

            if(item[self.dims_len+1]+item[self.dims_len] == 0):
                continue

            ix = str(item[0])+"~"+str(item[1])+"~"+str(item[2])+"~"+str(item[3])+"~"+str(item[4])

            latent_force[ix]=round(float(item[self.dims_len+1])/float(self.error_item),2)
            confidence_set[ix]=round(float(item[self.dims_len+1])/float(item[self.dims_len+1]+item[self.dims_len]),2)
            sp_set[ix] = round(self.A * latent_force[ix]+self.B * confidence_set[ix],2)

            #print(latent_force[ix])
            #print(confidence_set[ix])
            if(latent_force[ix] < self.cut_threshold):
                continue
            search_set[ix] = sp_set[ix] #第一层用latent_force剪枝之后
            if(latent_force[ix] > self.supTHR and confidence_set[ix]> self.conTHR):
                conf_avg,support_sum = self.subNodeCalc(ix,confidence_set[ix])
                confidence_loss[ix] = round(conf_avg,2)

                #if (abs(confidence_set[ix] - conf_avg) < self.con_combine_thr):
                if (conf_avg < self.con_combine_thr):
                    recommond_list.append(ix)
                    
                    self.removeChildfromList(ix)
                else:
                    continue

        #print(search_set)
        #logging.info("first layer length: "+str(len(self.start_list)))
        search_set_sorted= sorted(search_set.items(), key=lambda item:item[1], reverse=True)
        Candidate_list = self.getCandidateList(search_set_sorted)

        #logging.info("search_set_sorted length: "+str(len(search_set_sorted)))
        search_set.clear()
        #print(len(Candidate_list))
        for loop in range(0,self.for_num):
            for item in Candidate_list:
                #calc support confidence_set sp_set
                normal,abnormal = self.getDataFromList(item,self.dims_list) 
                if(normal==-1 and abnormal==-1):
                    continue
                ix = str(item[0])+"~"+str(item[1])+"~"+str(item[2])+"~"+str(item[3])+"~"+str(item[4])
                if(abnormal+normal == 0):
                    continue
                latent_force[ix]=round(float(abnormal)/float(self.error_item),2)
                confidence_set[ix]=round(float(abnormal)/float(abnormal+normal),2)
                sp_set[ix] = round(self.A*latent_force[ix]+self.B*confidence_set[ix],2)

                if(latent_force[ix]< self.cut_threshold):
                    continue
                search_set[ix]=sp_set[ix]
            
                if(latent_force[ix] > self.supTHR and confidence_set[ix]> self.conTHR):
                    conf_avg,support_sum = self.subNodeCalc(ix,confidence_set[ix])
                    confidence_loss[ix] = round(conf_avg,2)                    

                    #if (abs(confidence_set[ix] - conf_avg) < self.con_combine_thr):
                    if (conf_avg < self.con_combine_thr):
                        recommond_list.append(ix)
                        self.removeChildfromList(ix)
                    else:
                        continue

            #logging.info("第"+str(loop+2)+"层的search_set大小："+str(len(search_set)))
            #print(str(loop+2)+" 层的search_set大小：" + str(len(search_set)))
            search_set_sorted= sorted(search_set.items(), key=lambda item:item[1], reverse=True)
            Candidate_list = self.getCandidateList(search_set_sorted)
            search_set.clear()

        pod_dict = {}
        pod_name = ['域名','用户所在地','接入网类型','操作系统','服务器']
        for recom in recommond_list:
            recom_list = recom.split("~")
            rx = ""
            for i in range(0,len(recom_list)):
                if(recom_list[i]=="*"):
                    rx = rx+"*"
                else:
                    rx = rx + pod_name[i]
                if(i < 4):
                    rx = rx + "~"
            if( rx not in pod_dict.keys() ):
                pod_dict[rx] = []

            pod_dict[rx].append(recom)


        pod_filter_dict = {}
        pod_information_dict = {}
        for pod_item in pod_dict:
            pod_dict[pod_item] = self.quick_sort(pod_dict[pod_item],latent_force)
            pod_filter_dict[pod_item] = 0
            sum_t = 0
            temp_dict = {}
            temp_lf = []
            temp_conf = []
            for item in pod_dict[pod_item]:
                sum_t = sum_t + latent_force[item]
                temp_lf.append(latent_force[item])
                temp_conf.append(confidence_set[item])
            temp_dict['latent_force'] = temp_lf
            temp_dict['confidence'] = temp_conf
            temp_dict['sum_latent_force'] = round(sum_t,2)
            temp_dict['length'] = len(pod_dict[pod_item])
            pod_information_dict[pod_item]= temp_dict
            #pod_filter_dict[pod_item] = 100*(sum_t)-len(pod_dict[pod_item])
            pod_filter_dict[pod_item] = round((sum_t)/len(pod_dict[pod_item]),2)

        pod_filter_sorted = sorted(pod_filter_dict.items(), key=lambda x: x[1], reverse=True)
        result = []
        j=0
    
        item_dict = {}
        for pod in pod_dict:
            rs = []
            for m in pod_dict[pod]:
                tp_list = []
                
                print(m)
                _recom = m
                if("9999~" in m):
                    _recom = m.replace("9999~", "其他~") 
                if("~0~" in m):
                    _recom = m.replace("~0~", "~手机用户~")  
                if("~1~" in m):
                    _recom = m.replace("~1~", "~家庭宽带~")  
                if("~2~" in m):
                    _recom = m.replace("~2~", "~WLAN~")  
                if("~3~" in m):
                    _recom = m.replace("~3~", "~集团用户~")  
                if("~4~" in m):
                    _recom = m.replace("~4~", "~system~")  
                if("~9~" in m):
                    _recom = m.replace("~9~", "~用户侧其他~") 
                print(_recom)
                tp_list.append(_recom)
                tp_list.append(latent_force[m])
                tp_list.append(confidence_set[m])
                tp_list.append(confidence_loss[m])
                rs.append(tp_list)
            item_dict[pod] = rs
                
        for item in pod_filter_sorted:
            if j==5:
                break
            j = j  + 1  
            temp = {}
            temp['pod']  = item[0]
            temp['score'] = round(item[1],2)
            temp['item'] = item_dict[item[0]]
            temp['sum_latent_force'] = round(pod_information_dict[item[0]]['sum_latent_force'],2)
            temp['length'] = pod_information_dict[item[0]]['length']
            result.append(temp)
            #print(item[0],item[1],temp)
        topResult = []
        if(len(result)!=0):
            if(result[0]['length']>=5):
                for iter in range(0,5):
                    temp = {}
                    temp["item"] = (result[0]['item'][iter][0])
                    temp['latent_force'] = (result[0]['item'][iter][1])
                    topResult.append(temp)
            else:
                for iter in result:
                    for it in iter['item']:
                        temp = {}
                        temp["item"] = (it[0])
                        temp['latent_force'] = (it[1])
                        topResult.append(temp)   
                topResult = topResult[0:5]        
         
        result = json.dumps(result)
        topResult = json.dumps(topResult)
        return(result,topResult)

def read_csv(file_name):
    f = open(file_name, 'r')
    content = f.read()
    final_list = list()
    rows = content.split('\n')
    for row in rows:
        final_list.append(row.split(','))
    return final_list

if __name__ == "__main__":
    d3_tree = []
    _list = []

    d3_file = sys.argv[1]
    es_file = sys.argv[2]
    with io.open(d3_file , "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        firstline = True
        for line in reader:
            if firstline:    #skip first line
                firstline = False
                continue
            #print(line)
            line[-1] = float(line[-1])
            line[-2] = float(line[-2])
            d3_tree.append(line)
    with io.open(es_file , "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        firstline = True
        for line in reader:
            if firstline:    #skip first line
                firstline = False
                continue
        
            line[-1] = float(line[-1])
            line[-2] = float(line[-2])
            _list.append(line)

    ift = iswift(d3_tree,_list)

    print(str(ift.run()),end='')





