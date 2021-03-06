# -*- coding:utf-8 -*- 
#!/usr/bin/python
# coding=utf-8 

from flask import Flask
from flask_restful import Resource,Api
from flask_restful import reqparse
from util.thread_pool import ThreadPoolManger
from locate import Locate
import threading,yaml,logging,time,datetime
from util.db_util import MysqldbHelper

now = time.strftime("%Y%m%d", time.localtime(time.time()))
logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
                    format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s-%(thread)d:%(message)s',
                    filename = 'logs/'+now+'.log',
                    filemode = 'a')

file = open("config/config.yaml")
config = yaml.load(file)
file.close()

_host = config["flask"]['host']
_port = config["flask"]['port']
_api = config["flask"]['api']
_thread_num = config["thread"]['thread_num']
kpi_list = config["kpis"]
#kpi_list = []



#init restful api
app = Flask(__name__)
api = Api(app)

#init thread pool
thread_pool = ThreadPoolManger(_thread_num)

def handle_request(_rac_id,_type,_name,_model,_start,_end,_kpi,_remarks,_domain):
    locate = Locate(_rac_id,_type,_name,_model,_start,_end,_kpi,_remarks)
    logging.info('thread %s is running ' % threading.current_thread().name)
    logging.info(str(_rac_id)+" status: getDataFromES")
    es_return = locate.getDataFromES()
    if(es_return == 1):
        return
    logging.info(str(_rac_id)+" status: groupby_3d")
    locate.groupby_3d()
    logging.info(str(_rac_id)+" status: algorithm")
    locate.algorithm()
    logging.info(str(_rac_id)+" status: done")

class _restful(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("racId",type=str)
            parser.add_argument('type', type=str)
            parser.add_argument('name', type=str)
            parser.add_argument('model', type=str)
            parser.add_argument('startTime', type=str)
            parser.add_argument('endTime', type=str)
            parser.add_argument('kpi', type=str)
            parser.add_argument('remarks', type=str)  
            parser.add_argument('domain', type=str)          
            args = parser.parse_args()

            _rac_id = args['racId']
            _type = args['type']
            _name = args['name']
            _model = args['model']
            _start = args['startTime']
            _end = args['endTime']
            _kpi = args['kpi']
            _remarks = args['remarks']
            _domain = args['domain']

            #filter 
            if(_kpi == "OUT_RATE"):
                _kpi = "CDN_OUT_RATE" 
            elif(_kpi=="HIT_TTFB"):
                _kpi="CDN_HIT_TTFB"
            elif(_kpi=="MISS_TTFB"):
                _kpi="CDN_MISS_TTFB"
            elif(_kpi=="CDN_CODE_4XX_PER"):
                _kpi="CDN_EX_4XX_PER"
            elif(_kpi=="HY_CODE_4XX_PER"):
                _kpi="HY_EX_4XX_PER"
            elif(_kpi=="CDN_CODE_5XX_PER"):
                _kpi="CDN_EX_5XX_PER"
            elif(_kpi=="HY_CODE_5XX_PER"):
                _kpi="HY_EX_5XX_PER"


            if (_rac_id==None or _type==None or _name==None or _model==None or _start==None or _end==None or _kpi==None or _domain == None):
                return  {"code":200, "success":"false","msg":"missing parameter"}
                logging.info(str(_rac_id)+" missing parameter")
            else:
                self.db=MysqldbHelper()   
                create_time= datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                if(_kpi not in kpi_list):
                    sql = "insert into rca_task_table (rcaId,type,name,startTime,endTime,kpi,model,createTime,overTime,state,remarks,domain) values ('"+\
                    _rac_id+"','"+_type+"','"+_name+"','"+_start+"','"+_end+"','"+_kpi+"','"+_model+"','"+create_time+"','"+create_time+"','"+str(7)+"','"+_remarks+"','"+_domain+"')"
                    self.db.update(sql)
                    logging.info(str(_rac_id)+" request kpi not in kpi list")
                    return {"code":200, "success":"true","msg":"kpi not in kpi list"}
                else:
                    sql = "insert into rca_task_table (rcaId,type,name,startTime,endTime,kpi,model,createTime,state,remarks,domain) values ('"+\
                        _rac_id+"','"+_type+"','"+_name+"','"+_start+"','"+_end+"','"+_kpi+"','"+_model+"','"+create_time+"','"+str(-1)+"','"+_remarks+"','"+_domain+"')"
                    self.db.update(sql)
                    logging.info(_rac_id+","+_type+","+_name+","+_start+","+_end+","+_kpi+","+_model+","+create_time+","+_remarks+","+_domain)
                    thread_pool.add_job(handle_request,*(_rac_id,_type,_name,_model,_start,_end,_kpi,_remarks,_domain))
                    return  {"code":200, "success":"true","msg":"success"}
        except Exception as e:
            logging.error('server_error:'+str(e))
            return {'server_error': str(e)}

api.add_resource(_restful,_api)

if __name__ == "__main__":
    app.run(host=_host, port=_port, debug=True)