# Fault Localization (online version 0.1)

## 1. environment
   1. python 2.7 with (flask flask_restful ...)
   2. expose 8383 port
   3. mysql 

## 2. Interface
#### RESTful API
正确请求
{
	"racId": "20200320001643",
	"type": "locate-ad",
	"domain": "ltsyd.qq.com",
	"name": "ltsyd.qq.com",
	"model": "iswift",
	"startTime": "20200319235600",
	"endTime": "20200320001300",
	"kpi": "OUT_FLOW",
	"remarks": "ltsyd.qq.com"
}
正确答复——成功
{
    "code": 200,
    "msg": "success",
    "success": "true"
}
正确答复——失败
{
	"code": 200,
	"success": "false",
	"msg": "missing parameter"
} 

{
	"code": 200,
	"success": "false",
	"msg": "kpi not in kpi list"
}
## 3. Main feature

#### 3.1 RESTful API module

#### 3.2 Thread Pool module 

#### 3.3 ES load module

#### 3.4 Groupby module

#### 3.5 Model Service module

#### 3.6 Database module

## 4.API
#### Mysql state状态说明
-1. 阻塞状态
0. 初始化
1. 下载ES数据完成
2. groupby完成
3. 开始故障定位算法
4. ES下载超时
5. 异常数据为空
6. 无定位结果
9. 完成故障定位


