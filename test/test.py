#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File: test.py
@Time: 2020-06-30 16:26:41
@Author: money 
'''
import random
import sys
import string
import os
import base64
import time
import datetime
import pymongo
t = base64.b64encode(os.urandom(64)).decode()

import sys,os
print(os.path.abspath(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

# dict = {
#     'name':'hah',
#     'sex': '男'
# }
# dict.update({'age':87})
# print(dict)

# print(string.ascii_letters)

# last_time_str = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
# timeArray = time.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
# last_time_timestamp = int(time.mktime(timeArray)) * 1000
# print(last_time_timestamp)

# #获取当前时间
# dtime = datetime.datetime.now()
# print(dtime)
# t = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)

# timeArray = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
# print(timeArray)
# timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
# print(timestamp)
# un_time = int(time.mktime((timeArray - datetime.timedelta(days=7)).timetuple())) * 1000
# print(un_time)

# set = {1,2,3,2}
# set.add(6)
# print(set)

# client = pymongo.MongoClient('127.0.0.1', 27017)

# cursor = client["student"]["visit"].aggregate([
#     {"$match": {"test": {"$in": [5, 9]}}}
# ])
# doc = [doc for doc in cursor]
# print(doc)

# uuid = base64.b64encode(os.urandom(8)).decode().lower()
# print(uuid + "111111111111111111111111111")

# list = [1,3,4]
# list.insert(1, 9)
# print(list)

# dict = {"$match": {}}
# dict["$match"].update({"name": "前"})
# print(dict)


# def test(a):
#     try:
#         if a >2:
#             raise Exception("错误")
#     except Exception as e:
#         print(e, "是的")
# test(4)

# print(os.getcwd())

# date = datetime.datetime.now()
# print(f"{date.year}{date.month}{date.day}")

# path = os.getcwd() + "/file/"

# if not os.path.exists(path):
#     os.makedirs(path)

# t = 1593532800000 - 1593619200000
# tt = 24 * 3600 * 1000
# print(t, tt)


# test_dict = {"user": 111, "mobile": 333}
# t = test_dict.get("sex")
# print(t)
# if t:
#     print("存在")
# uuid = base64.b64encode(os.urandom(32)).decode()
# print(uuid)   

# import manage

# state = manage.client["test"].insert([{"user": 3, "name": 3}, {"user": 2, "name": 2}])
# print(state)
# list = [doc for doc in state]

# cursor = manage.client["test"].find({"_id": {"$in": list}})
# for doc in cursor:
#     print(doc)
# import datetime
# import time
# today = datetime.date.month
# today_time = int(time.mktime(today.timetuple())*1000)
# print(today)

# random_str = "%02d" % random.randint(0, 100)
# print(random_str)

# size = os.path.getsize() // 1024

# str = "http://101.136.132.180/20200713103921.png"
# str = str.replace("http", "")
# print(str)
# print(size)

# import time
# itme_id = str(int(time.time()*1000)) + str(int(time.clock()*1000000))
# print(itme_id, time.clock())

# temp_str = "/".join("/abcdefg/2020/7/5a1391214425e1721c1e063fa15a49f51922_5d8b2446e7bce75e7ef4b513.jpg".split("/")[:-1])
# print(temp_str)

# uid = base64.b64encode(os.urandom(16)).decode()
# print(uid)
# str = "23432532t"
# str.replace("t", "")
# print(str)

# timeArray = datetime.datetime.strptime("2020-05-07", "%Y-%m-%d")
# timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
# print(timestamp)

# # reg = '/(^(?:(?![IOZSV])[\dA-Z]){2}\d{6}(?:(?![IOZSV])[\dA-Z]){10}$)|(^\d{15}$)/';
# import re
# reg = re.match(r'^(?:(?![IOZSV])[\dA-Z]){2}\d{6}(?:(?![IOZSV])[\dA-Z]){10}$)|(^\d{15}$', "9131000059169930XE")

# print(reg)


# import records
 
# rows = [
#   {"x": 1, "y": 2},
#   {"x": 2, "y": 3},
#   {"x": 3, "y": 4},
#   {"x": 4, "y": 5}
# ]
# results = records.RecordCollection(iter(rows))
# with open('demo.xlsx', 'wb') as f:
#     f.write(results.export('xlsx'))
import xlwt
# wb = xlwt.Workbook()
# # 添加一个表
# ws = wb.add_sheet('test')


# 3个参数分别为行号，列号，和内容
# 需要注意的是行号和列号都是从0开始的
data_list = [
    {"name": "前", "nick": "哈", "mobile": "1772501251"},
    {"name": "fei", "nick": "hah", "mobile": "1772501252"},
    {"name": "前qian", "nick": "heh哈", "mobile": "1772501253"},
]
# ws.write(0, 0, 'name')
# ws.write(0, 1, 'nick')
# ws.write(0, 2, 'mobile')
# n = 1
# for doc in data_list:
#     ws.write(n, 0, doc.get('name'))
#     ws.write(n, 1, doc.get('nick'))
#     ws.write(n, 2, doc.get('mobile'))
#     n += 1
# # 保存excel文件
# wb.save('./test.xls')


class ExportExcle(object):
    """导出excel"""
    def __init__(self, fieldname: tuple, tabelname: str):
        """
        初始化
        :param key: 字段名
        :param tabelname: 表名
        """
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet(tabelname)
        self.c = 0
        self.fieldname = fieldname
        for i in self.fieldname:
            self.ws.write(0, self.c, i)
            self.c += 1
    def export_excle(self, data: list, foldername: str, filename: str):
        """
        导出
        :param data: 数据
        :param foldername: 目录名
        :param filename: 文件名
        """
        n = 1
        for doc in data:
            for (i, field) in enumerate(self.fieldname):
                self.ws.write(n, i, doc.get(field))
            n += 1
        DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = DIRNAME + f"/statics/{foldername}/"
        if not os.path.exists(path):
            os.makedirs(path)
        self.wb.save(DIRNAME + f"/statics/{foldername}/" + f"{filename}.xls")

# test = ExportExcle(("name","nick","mobile"), "testssss")
# test.export_excle(data_list, "export_excle", "qian")

temp = {
    "order": "提现单号", 
    "create_time": "申请时间",
    "amount": "提现金额",
    "account": "申请账号",
    "state": "订单状态",
    "update_time": "处理时间",
    "channel": "提现渠道",
    "trade_id": "支付号码",
    "trade_name": "支付姓名",
}

# for i,j in enumerate(temp):
#     print(i,j)

# import rsa
# import base64
# public_key, private_key  = rsa.newkeys(1024)
# k = private_key.save_pkcs1()
# p = public_key.save_pkcs1()
# with open("1.py", "wb") as f:
#     f.write(k)
# with open("2.py", "wb") as f:
#     f.write(p)
# k = rsa.PrivateKey._load_pkcs1_pem(k)
# k = rsa.sign("是吗".encode("utf-8"), k, "SHA-256")
# k = base64.b64encode(k)
# print(k)

# dtime = datetime.datetime.now()
# print(dtime)
# t = dtime.strftime("%Y-%m-%d %H:%M:%S")
# print(t)

# dict = {
#     "name": 1,
#     "age": 18
# }
# dict.pop("name")
# print(dict)
# import urllib
# url = "www.baidu.com?id=123&name=mu&re=mmm&some=ooooo"
# query = urllib.parse.urlparse(url).query
# print(query)
# lst = dict([(k, v[0]) for k, v in urllib.parse.parse_qs(query).items()])
# print(lst)

# tuple = {1,3,4}
# print(type(tuple))
# from dateutil import parser 
# t = parser.parse(datetime.datetime.utcnow().isoformat())
# print(t, type(t))
# from manage import client_me

# cursor = client_me["me_music"].find({})

# for doc in cursor:
#     print(doc)
# Successfully installed bcrypt-3.1.7 cryptography-3.0 paramiko-2.7.1 pynacl-1.4.0 sshtunnel-0.1.5
# from sshtunnel import SSHTunnelForwarder
# import pymongo
# server = SSHTunnelForwarder(
#     ssh_address_or_host="120.26.218.247",
#     ssh_username = "root",
#     ssh_password = "wwwgli20160503CN" ,
#     remote_bind_address = ("127.0.0.1", 27018))
# server.start()
# client = pymongo.MongoClient('127.0.0.1',server.local_bind_port) ## 这里一定要填入ssh映射到本地的端口
# cursor = client["Lean"]["me_music"].find({})
# for doc in cursor:
#     print(doc)

# def get():
#     return 1, 2, 3

# t, r, h = get()
# print(t, r)

# import manage

# manage.client["test"].update({"uid": "001"}, {"$set": {"name": "哈哈"}})
# import os
# import hashlib
# print(hashlib.md5(os.urandom(32)).hexdigest())
# import time
# t1 = 1597116590000
# t2 = 1597120250000
# print((t2 - t1) // 60000)
# dtime = datetime.datetime.now()
# dtime_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
# timeArray = datetime.datetime.strptime(dtime_str, "%Y-%m-%d %H:%M:%S")
# now_timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
# yesterday_timestamp = int(time.mktime((timeArray - datetime.timedelta(days=1)).timetuple())) * 1000
# print(now_timestamp, yesterday_timestamp)

# lst = [{"nage": 1, "age": 2}, {"nage": 4, "age": 3}]

# # with open("demo.json", "wb") as f:
# #     f.write(str(lst).encode("utf-8"))
# import json
# with open("demo.json", "rb") as f:
#     cont = f.read()


# # # # rest = eval(cont.decode("utf-8"))
# # # temp = cont.decode("utf-8")
# # # print(temp, type(temp))
# g = cont.decode("utf-8")
# print(g, type(g))
# rest = json.loads(str(g))
# print(rest, type(rest))
# for doc in rest:
#     print(doc)\

# trade_data = {"trade_id": ["0"], "balance": 3, "trade_amount": 3}

# print(trade_data["trade_id"])


# mobile = "17725021251"
# print(mobile[-4:])
# today = datetime.date.today()
# today_stamp = int(time.mktime(today.timetuple()) * 1000)
# print(today_stamp)
exclude = []
for doc in exclude:
    exclude_amount += doc["price"]