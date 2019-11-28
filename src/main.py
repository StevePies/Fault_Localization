# -*- coding:utf-8 -*- 
#!/usr/bin/python
# coding=utf-8 

from flask import Flask
from flask_restful import Resource,Api
from flask_restful import reqparse
from util.thread_pool import ThreadPoolManger
from locate import Locate
import threading


#init restful api
app = Flask(__name__)
api = Api(app)

#init thread pool
thread_pool = ThreadPoolManger(4)

def handle_request(_task_id,_type,_name,_model,_start,_end,_kpi):
    locate = Locate(_task_id,_type,_name,_model,_start,_end,_kpi)
    print ('thread %s is running ' % threading.current_thread().name)
    print(_task_id,_type,_name,_model,_start,_end,_kpi)
    locate.getDataFromES()
    locate.groupby_3d()
    locate.algorithm()

class _restful(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument("task_id",type=str)
            parser.add_argument('type', type=str, help='Email address to create user')
            parser.add_argument('name', type=str, help='Email address to create user')
            parser.add_argument('model', type=str, help='Password to create user')
            parser.add_argument('start', type=str, help='Password to create user')
            parser.add_argument('end', type=str, help='Password to create user')
            parser.add_argument('kpi', type=str, help='Password to create user')
            args = parser.parse_args()

            _task_id = args['task_id']
            _type = args['type']
            _name = args['name']
            _model = args['model']
            _start = args['start']
            _end = args['end']
            _kpi = args['kpi']

            if (_task_id==None or _type==None or _name==None or _model==None or _start==None or _end==None or _kpi==None):
                return  {"code":200, "success":"false","msg":"missing parameter"}
            else:
                thread_pool.add_job(handle_request,*(_task_id,_type,_name,_model,_start,_end,_kpi))
                return  {"code":200, "success":"true","msg":"success"}
        except Exception as e:
            return {'error': str(e)}

api.add_resource(_restful,'/locate')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8383, debug=True)