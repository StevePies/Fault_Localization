import es_load 

class Locate:
    def __init__(self, _task_id,_type,_model,_start,_end,_kpi):
        self._task_id = _task_id
        self._type = _type
        self._model = _model
        self._start = _start
        self._end = _end
        self._kpi = _kpi
       

    def getDataFromES():
        self.es_data = es_load.search(self._start,self._end,self._kpi)
        for item in self.es_data:
            print(item)
        
    def groupby_3d():
        i=0
        
    def iswift():
        i=0


    def insert_to_db():
        i=0
