#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: order.py
@Time: 2020-07-14 17:24:23
@Author: money 
"""
##################################【app订单模块】##################################
import os
import base64
import string
import time
import random
import datetime
import manage
from bson.son import SON
from flask import request, g
from utils.util import response
from constant import constant


def post_add_car():
    """加入购物车"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        works_id = request.json.get("works_id")
        price = request.json.get("price")
        is_buy = request.json.get("is_buy") # true购买 false加入购物车
        if not works_id:
            return response(msg="Bad Request: Miss params: 'works_id'.", code=1, status=400)
        if not price:
            return response(msg="Bad Request: Miss params: 'price'.", code=1, status=400)
        if price < 0:
            return response(msg="Bad Request: Params 'price' is error.", code=1, status=400)
        if is_buy not in [True, False]:
            return response(msg="Bad Request: Params 'is_buy' is error.", code=1, status=400)
        # 查询
        doc = manager.client["works"].find_one({"uid": works_id, "state": 2})
        if not doc:
            return response(msg="Bad Request: Param 'works_id' if error.", code=1, status=400)
        pic_id = doc.get("pic_id")[0]
        title = doc.get("title")
        price_id = doc.get("price_id")
        # 图片路径
        doc = manage.client["pic_material"].find_one({"uid": pic_id})
        pic_url = doc.get("pic_url")
        thumb_url = doc.get("thumb_url")
        # 规格
        doc = manage.client["price"].find_one({"uid": price_id})
        spec = doc.get("format")
        currency = doc.get("currency")
        price_unit = doc.get("price_unit")
        uid = base64.b64encode(os.urandom(32)).decode()
        # 插入订单
        condition = {
            "uid": uid, "user_id": user_id, "works_id": works_id, "title": title, "pic_url": pic_url, "spec": spec, "currency": currency, "price_unit": price_unit, "thumb_url": thumb_url,
            "price": price, "state": 1 if is_buy else 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        }
        if is_buy:
            # 订单号
            order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
            condition.update({"order": order, "order_time": int(time.time() * 1000)})
        manage.client["order"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_user_car_list(domain=constant.DOMAIN):
    """
    获取用户购物车列表
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 0}},
            {"$project": {"_id": 0, "uid": 1, "title": 1, "spec": 1, "currency": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_car_generate_order():
    """购物车合并订单"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        uid_list = request.json.get("uid_list") # array
        if not uid_list:
            return response(msg="Bad Request: Miss params: 'uid_list'.", code=1, status=400)
        # 订单号
        order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        doc = manage.client["order"].update({"uid": {"$in": uid_list}}, {"$set": {"order": order, "state": 1, "create_time": int(time.time() * 1000)}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_user_order_list():
    """用户订单列表"""
    data = {}
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        is_complete = request.json.get("is_complete") # true完成 false待付款
        if is_complete not in [True, False]:
            return response(msg="Bad Request: Params 'is_complete' is error.", code=1, status=400)
        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": 2 if is_complete else 1}},
            {"$project": {"_id": 0, "order": 1, "title": 1, "spec": 1, "currency": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "update_time": 1, "create_time": 1}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = []
        total_amount = 0
        order = 0
        create_time = 0
        update_time = 0
        for doc in cursor:
            if total_amount == 0:
                order = doc["uid"]
                create_time = doc["create_time"]
                update_time = doc["update_time"]
            total_amount += doc["price"]
            data_list.append(doc)
        data["order"] = order
        data["total_amount"] = total_amount
        data["data_list"] = data_list if data_list else []
        data["create_time"] = create_time
        data["update_time"] = update_time
        return response(data=data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def put_user_order():
    """取消订单"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        order_id = request.json.get("order_id")
        if not order_id:
            return response(msg="Bad Request: Miss params: 'order_id'.", code=1, status=400)
        # 更新
        doc = manage.client["order"].update({"order": order_id, "user_id": user_id, "state": 1}, {"$set": {"state": 0, "update_time": 1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)