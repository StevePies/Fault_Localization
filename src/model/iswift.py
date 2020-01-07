#!/usr/bin/python
# coding=utf-8 

import pandas as pd
import numpy as np
import yaml
import itertools
import csv
import datetime


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
        self.con_combine_thr = 0.05
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
            temp = item[0].split("-")
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
    def subNodeCalc(self,ix):

        #print("进入儿子节点")
        conf_avg = 0
        support_sum = 0
        _list =  ix.split("-")
        result_list = []
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
            ix = str(item[0])+"-"+str(item[1])+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])
            if((item[self.dims_len+1]+item[self.dims_len]) == 0):
                continue
            local_sup[ix]=item[self.dims_len+1]/(self.error_item)
            local_conf[ix]=item[self.dims_len+1]/(item[self.dims_len+1]+item[self.dims_len])
            ##print(ix,local_sup[ix],local_conf[ix])
            support_sum = support_sum+local_sup[ix]
            conf_avg = conf_avg+local_conf[ix]
        if len(result_list) == 0:
            return 0,0
        else:
            return conf_avg/len(result_list),support_sum
    
    def removeChildfromList(self,ix):
        _list =  ix.split("-")

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
        
        if(self.error_item == 0):
            print("error_item = 0")
            return []

        for item in self.start_list:
            if(item[self.dims_len+1]+item[self.dims_len] == 0):
                continue
            ix = str(item[0])+"-"+str(item[1])+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])
            latent_force[ix]=item[self.dims_len+1]/(self.error_item)
            confidence_set[ix]=item[self.dims_len+1]/(item[self.dims_len+1]+item[self.dims_len])
            sp_set[ix] = self.A * latent_force[ix]+self.B * confidence_set[ix]
            print("++++++++++++++++")
            print(ix)
            print(latent_force[ix])
            print(confidence_set[ix])

            if(latent_force[ix] < self.cut_threshold):
                continue
            search_set[ix] = sp_set[ix] #第一层用latent_force剪枝之后
            if(latent_force[ix] > self.supTHR and confidence_set[ix]> self.conTHR):
                conf_avg,support_sum = self.subNodeCalc(ix)

                #print(ix,latent_force[ix],confidence_set[ix],conf_avg,support_sum)

                if (abs(confidence_set[ix] - conf_avg) < self.con_combine_thr):
                    recommond_list.append(ix)
                    self.removeChildfromList(ix)
                else:
                    continue

        print(recommond_list)
          
        search_set_sorted= sorted(search_set.items(), key=lambda item:item[1], reverse=True)
        Candidate_list = self.getCandidateList(search_set_sorted)
        search_set.clear()
        print(len(Candidate_list))
        for loop in range(0,self.for_num):
            for item in Candidate_list:
                #calc support confidence_set sp_set
                normal,abnormal = self.getDataFromList(item,self.dims_list) 
                if(normal==-1 and abnormal==-1):
                    continue
                ix = str(item[0])+"-"+str(item[1])+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])
                if(abnormal+normal == 0):
                    continue
                latent_force[ix]=abnormal/(self.error_item)
                confidence_set[ix]=abnormal/(abnormal+normal)
                sp_set[ix] = self.A*latent_force[ix]+self.B*confidence_set[ix]

                if(latent_force[ix]< self.cut_threshold):
                    continue
                search_set[ix]=sp_set[ix]
            
                if(latent_force[ix] > self.supTHR and confidence_set[ix]> self.conTHR):
                    conf_avg,support_sum = self.subNodeCalc(ix)
                    #print(ix, latent_force[ix], confidence_set[ix], conf_avg, support_sum)
                    if (abs(confidence_set[ix] - conf_avg) < self.con_combine_thr):
                        recommond_list.append(ix)
                        self.removeChildfromList(ix)
                    else:
                        continue
            #print("第"+str(aaa+2)+"层："+str(len(search_set)))
            print(str(loop+2)+" 层的search_set大小：" + str(len(search_set)))
            search_set_sorted= sorted(search_set.items(), key=lambda item:item[1], reverse=True)
            Candidate_list = self.getCandidateList(search_set_sorted)
            search_set.clear()

        print(recommond_list)
        pod_dict = {}
        for recom in recommond_list:
            recom_list = recom.split("-")
            rx = ""
            for i in range(0,len(recom_list)):
                if(recom_list[i]=="*"):
                    rx = rx+"*"
                else:
                    rx = rx + str(i)
                if(i < 4):
                    rx = rx + "-"
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
            temp_dict['sum_latent_force'] = sum_t
            temp_dict['length'] = len(pod_dict[pod_item])

            pod_information_dict[pod_item]= temp_dict
            pod_filter_dict[pod_item] = 100*(sum_t)-len(pod_dict[pod_item])

        pod_filter_sorted = sorted(pod_filter_dict.items(), key=lambda x: x[1], reverse=True)
        result = []
        j=0
        for item in pod_filter_sorted:
            if j==3:
                break
            j = j  + 1  
            temp = {}
            temp['pod']  = item[0]
            temp['score'] = item[1]
            temp['item'] = pod_dict[item[0]]
            temp['latent_force'] = pod_information_dict[item[0]]['latent_force']
            temp['confidence'] = pod_information_dict[item[0]]['confidence']
            temp['sum_latent_force'] = pod_information_dict[item[0]]['sum_latent_force']
            temp['length'] = pod_information_dict[item[0]]['length']
            result.append(temp)
            #print(item[0],item[1],temp)
        return(result)