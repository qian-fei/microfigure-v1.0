#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: order.py
@Time: 2020-07-14 17:24:23
@Author: money 
"""
##################################【app订单及充值模块】##################################
import os
import base64
import string
import time
import random
import datetime
import manage
from bson.son import SON
from flask import request, g, jsonify, Response
from utils.util import response
from constant import constant
from utils.alipay import AliPay
from utils.wechat import WechatPay


def add_user_goods_api(order, buyer_id , seller_id):
    """
    添加到用户商品
    :param order: 商品订单
    :param buyer_id: 买家id
    :param seller_id: 卖家id
    """
    try:
        cursor = manage.client["order"].find({"order": order})
        data1 = {}
        for doc in cursor:
            if doc["works_id"] not in data1:
                data1[doc["works_id"]] = [doc["spec"]]
            else:
                temp = data1[doc["works_id"]]
                temp.append(doc["spec"])
                data1[doc["works_id"]] = list(set(temp))
        works_id_list = list(data1.keys())
        data2 = {}
        cursor = manage.client["works"].find({"uid": {"$in": works_id_list}})
        for doc in cursor:
            data2[doc["uid"]] = doc["pic_id"][0]
        uid = base64.b64encode(os.urandom(16)).decode()
        condition = []
        for i in works_id_list:
            temp = {"uid": uid, "user_id": buyer_id, "works_id": i, "pic_id": data2[i], "spec": data1[i], "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            condition.append(temp)
        manage.client["goods"].insert(condition)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


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
        doc = manage.client["works"].find_one({"uid": works_id, "state": 2})
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
        doc = manage.client["price"].find_one({"uid": price_id, "price": price})
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
        return response(data= order if is_buy else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_order_detail(domain=constant.DOMAIN):
    """
    订单详情
    :param domain: 域名
    """
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        order = request.args.get("order")
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        pipeline = [
            {"$match": {"user_id": user_id, "order": order}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"balance": "$user_info.balance"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "order": 1, "title": 1, "spec": 1, "currency": 1, "balance": 1, "state": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "update_time": 1, "create_time": 1}},
            {"$group": {"_id": {"order": "$order", "create_time": "$create_time", "state": "$state", "balance": "$balance"}, "total_amount": {"$sum": "$price"}, "works_item": {"$push": "$$ROOT"}}},
            {"$project": {"_id": 0, "order": "$_id.order", "create_time": "$_id.create_time", "works_item": 1, "total_amount": 1, "state": "$_id.state", "balance": "$_id.balance"}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = []
        for doc in cursor:
            create_time = doc["create_time"]
            now_time = int(time.time() * 1000)
            doc["delta_time"] = (create_time + 1800000 - now_time) // 1000
            data_list.append(doc)
        return response(data=data_list[0] if data_list else None)
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


def delete_user_car_goods():
    """删除购物车商品"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        # 商品id
        uid_list = request.json.get("uid_list") # array
        if not uid_list:
            return response(msg="Bad Request: Miss param 'uid_list'.", code=1, status=400)
        manage.client["order"].update({"uid": {"$in": uid_list}}, {"$set": {"state": -1}}, multi=True)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_car_generate_order(domain=constant.DOMAIN):
    """
    购物车合并订单
    :param domain: 域名
    """
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
        doc = manage.client["order"].update({"uid": {"$in": uid_list}}, {"$set": {"order": order, "state": 1, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        # 返回订单信息
        pipeline = [
            {"$match": {"user_id": user_id, "order": order}},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"balance": "$user_info.balance"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "order": 1, "title": 1, "spec": 1, "balance": 1, "currency": 1, "state": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "create_time": 1}},
            {"$group": {"_id": {"order": "$order", "balance": "$balance", "create_time": "$create_time", "state": "$state"}, "total_amount": {"$sum": "$price"}, "works_item": {"$push": "$$ROOT"}}},
            {"$project": {"_id": 0, "order": "$_id.order", "create_time": "$_id.create_time", "balance": "$_id.balance", "state": "$_id.state", "works_item": 1, "total_amount": 1}},
            {"$sort": SON([("create_time", -1)])}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = []
        for doc in cursor:
            create_time = doc["create_time"]
            now_time = int(time.time() * 1000)
            doc["delta_time"] = (create_time + 1800000 - now_time) // 1000
            data_list.append(doc)
        return response(data=data_list[0] if data_list else None)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_user_order_list(domain=constant.DOMAIN):
    """
    用户订单列表
    :param domain: 域名
    """
    data = {}
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        is_complete = request.args.get("is_complete") # true完成 false待付款
        page = request.args.get("page")
        num = request.args.get("num")
        if is_complete not in ["true", "false"]:
            return response(msg="Bad Request: Params 'is_complete' is error.", code=1, status=400)
        if not page:
            return response(msg="Bad Request: Miss param 'page'.", code=1, status=400)
        if not num:
            return response(msg="Bad Request: Miss param 'num'.", code=1, status=400)
        if int(num) < 1 or int(page) < 1:
            return response(msg="Bad Request: Param 'page' or 'num' is error.", code=1, status=400)
        # 更新订单状态
        cursor = manage.client["order"].find({"user_id": user_id, "state": 1})
        for doc in cursor:
            create_time = doc["create_time"]
            now_time = int(time.time() * 1000)
            if ((now_time - create_time) // 60000) >= 30:
                manage.client["order"].update({"order": doc["order"]}, {"$set": {"state": -1}}, multi=True)

        # 查询
        pipeline = [
            {"$match": {"user_id": user_id, "state": {"$in": [-1, 2]} if is_complete == "true" else 1}},
            {"$skip": (int(page) - 1) * int(num)},
            {"$limit": int(num)},
            {"$lookup": {"from": "user", "let": {"user_id": "$user_id"}, "pipeline": [{"$match": {"$expr": {"$eq": ["$uid", "$$user_id"]}}}], "as": "user_item"}},
            {"$addFields": {"user_info": {"$arrayElemAt": ["$user_item", 0]}}},
            {"$addFields": {"balance": "$user_info.balance"}},
            {"$unset": ["user_item", "user_info"]},
            {"$project": {"_id": 0, "uid": 1, "order": 1, "title": 1, "spec": 1, "balance": 1, "currency": 1, "state": 1, "thumb_url": {"$concat": [domain, "$thumb_url"]}, "price": 1, "update_time": 1, "create_time": 1}},
            {"$group": {"_id": {"order": "$order", "create_time": "$create_time", "state": "$state", "balance": "$balance"}, "total_amount": {"$sum": "$price"}, "works_item": {"$push": "$$ROOT"}}},
            {"$project": {"_id": 0, "order": "$_id.order", "create_time": "$_id.create_time", "works_item": 1, "total_amount": 1, "balance": "$_id.balance", "state": "$_id.state"}}
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        if is_complete == "false":
            data_list = []
            for doc in cursor:
                create_time = doc["create_time"]
                now_time = int(time.time() * 1000)
                doc["delta_time"] = (create_time + 1800000 - now_time) // 1000
                data_list.append(doc)
        else:
            data_list = [doc for doc in cursor]
        return response(data=data_list if data_list else [])
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def get_not_complete_order_count():
    """未付款的订单数"""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        pipeline = [
            {"$match": {"user_id": user_id, "state": 1}},
            {"$group": {"_id": "$order"}},
            {"$count": "count"},
        ]
        cursor = manage.client["order"].aggregate(pipeline)
        data_list = [doc for doc in cursor]
        count = data_list[0]["count"] if data_list else 0
        return response(data=count)
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
        doc = manage.client["order"].update({"order": order_id, "user_id": user_id, "state": 1}, {"$set": {"state": -1, "update_time": 1}}, multi=True)
        if doc["n"] == 0:
            return response(msg="Update failed.", code=1, status=400)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s.", code=1, status=500)


def post_order_payment():
    """订单支付"""
    request_param = ""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        order = request.json.get("order")
        pay_method = request.json.get("channel") # 余额 支付宝 微信
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        if pay_method not in ["微信", "支付宝", "余额"]:
            return response(msg="Bad Request: Params 'pay_method' is error.", code=1, status=400)
        total_amount = 0
        cursor = manage.client["order"].find({"order": order})
        n = 0
        for doc in cursor:
            total_amount += doc["price"]
            if n == 0:
                goods_id = doc["works_id"]
                n += 1
        doc = manage.client["user"].find_one({ "uid": user_id})
        balance = doc.get("balance")
        # 生成交易信息
        trade_id = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        condition = {"trade_id": trade_id, "type": "balance" if pay_method == "余额" else ("alipay" if pay_method == "支付宝" else "wxpay"), "trade_amount": total_amount, 
                     "goods_id": goods_id, "state": 1, "order": order, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
        manage.client["trade"].insert(condition)
        # 余额支付
        if pay_method == "余额":
            trade_data = {"trade_id": trade_id, "balance": balance, "trade_amount": total_amount}
            import json
            trade_str = json.dumps(trade_data)
            request_param = trade_str
        # 支付宝支付
        if pay_method == "支付宝":
            alipay = AliPay(order, str(total_amount))
            request_param = alipay.generate_request_param(order, str(total_amount))
        # 微信支付
        if pay_method == "微信":
            wechatpay = WechatPay(order, total_amount * 100)
            prepay_id = wechatpay.wechat_payment_request()
            if not prepay_id:
                return response(msg="请求微信失败", code=1)
            request_param = wechatpay.generate_app_call_data(prepay_id)
        return response(data=request_param)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_alipay_callback_verify():
    """支付宝回调验证"""
    try:
        data = request.args
        out_trade_no, total_amount, _ = AliPay.callback_verify_sign(data)
        if not out_trade_no:
            return Response("failure")
        cursor = manage.client["order"].find({"order": out_trade_no})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc.get("price")
        if not data_list:
            return Response("failure")
        if temp_amount != total_amount:
            return Response("failure")
        return Response("success")
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_wechat_callback_verify():
    """微信支付回调验证"""
    try:
        data = request.args
        out_trade_no, total_fee, _ = WechatPay.verify_wechat_call_back(data)
        if not all([out_trade_no, total_fee]):
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        cursor = manage.client["order"].find({"order": out_trade_no})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc.get("price")
        if not data_list:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        if temp_amount != total_fee / 100:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        xml_data = wxpay.generate_xml_data({"return_code": "SUCCESS", "return_msg": "OK"})
        return Response(xml_data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_app_callback():
    """支付成功后app回调"""
    try:
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1)
        # 参数
        order = request.json.get("order")
        total_amount = request.json.get("total_amount")
        if not order:
            return response(msg="Bad Request: Miss params: 'order'.", code=1, status=400)
        if not total_amount:
            return response(msg="Bad Request: Miss params: 'total_amount'.", code=1, status=400)
        cursor = manage.client["order"].find({"order": order})
        data_list = []
        temp_amount = 0
        for doc in cursor:
            data_list.append(doc)
            temp_amount += doc["price"]
        if temp_amount != total_amount:
            return response(msg="Bad Request: Params 'total_amount' is error.", code=1, status=400)
        if not data_list:
            return response(msg="Bad Request: Params 'order' is error.", code=1, status=400)
        works_id = data_list[0]["works_id"]
        doc = manage.client["works"].find_one({"uid": works_id})
        seller_id = doc["user_id"]
        doc = manage.client["user"].update({"uid": seller_id}, {"$set": {"balance": total_amount}})
        if doc["n"] == 0:
            raise Exception("User balance update failed")
        # 更新订单状态
        manage.client["order"].update({"order": order}, {"$set": {"state": 2}})
        # 更新作品销量
        manage.client["works"].update({"uid": works_id}, {"$inc": {"sale_num": 1}})
        # 统计
        dtime = datetime.datetime.now()
        time_str = dtime.strftime("%Y-%m-%d") + " 0{}:00:00".format(0)
        timeArray = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray.timetuple()) * 1000)
        doc = manage.client["user_statistical"].update({"user_id": user_id, "date": timestamp}, {"$inc": {"sale_num": 1, "amount": total_amount}})
        if doc["n"] == 0:
            condition = {"user_id": user_id, "date": timestamp, "works_num": 0, "sale_num": 1, "browse_num": 0, "amount": total_amount, "like_num": 0, "goods_num": 0, "register_num": 0,
                         "comment_num": 0, "share_num": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
            manage.client["user_statistical"].insert(condition)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_top_up():
    """余额充值"""
    request_param = ""
    try:
        # 参数
        user_id = g.user_data["user_id"]
        if not user_id:
            return response(msg="Bad Request: User not logged in.", code=1, status=400)
        channel = request.json.get("channel") # 支付宝 微信
        total_amount = request.json.get("total_amount")
        if pay_method not in ["微信", "支付宝", "余额"]:
            return response(msg="Bad Request: Params 'pay_method' is error.", code=1, status=400)
        if not total_amount:
            return response(msg="Bad Request: Miss params: 'total_amount'.", code=1, status=400)
        if total_amount < 0 or type(total_amount) != float:
            return response(msg="Bad Request: Parmas 'total_amount' is error.", code=1, status=400)
        # order = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        # # 创建充值订单
        # condition = {
        #     "order": order, "user_id": user_id, "channel": channel, "amount": total_amount, "state": 0, "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)
        # }
        # manage.client["recharge_records"].insert(condition)
        # 生成交易id
        trade_id = str(int(time.time() * 1000)) + str(int(time.clock() * 1000000))
        condition = {"trade_id": trade_id, "type": "alipay" if channel == "支付宝" else "wxpay", "trade_amount": total_amount, "goods_id": "", "state": 1, "order": "",
                     "create_time": int(time.time() * 1000), "update_time": int(time.time() * 1000)}
        manage.client["trade"].insert(condition)
        # 支付宝支付
        if pay_method == "支付宝":
            alipay = AliPay(order, total_amount)
            request_param = alipay.generate_request_param()
        # 微信支付
        if pay_method == "微信":
            wechatpay = WechatPay(order, total_amount * 100)
            prepay_id = wechatpay.wechat_payment_request()
            if not prepay_id:
                return response(msg="请求微信失败", code=1)
            request_param = wechatpay.generate_app_call_data(prepay_id)
        return response(data=request_param)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_top_up_alipay_callback_verify():
    """余额充值-支付宝回调验证"""
    try:
        data = request.args
        out_trade_no, total_amount, trade_no = AliPay.callback_verify_sign(data)
        if not out_trade_no:
            return Response("failure")
        doc = manage.client["recharge_records"].find_one({"order": out_trade_no})
        if not doc:
            return Response("failure")
        if doc.get("amount") != total_amount:
            return Response("failure")
        manage.client["recharge_records"].update({"order": out_trade_no}, {"$set": {"trade_id": trade_no, "state": 1}})
        return Response("success")
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def post_top_up_wechat_callback_verify():
    """余额充值-微信回调验证"""
    try:
        data = request.args
        out_trade_no, total_fee, transaction_id = WechatPay.verify_wechat_call_back(data)
        if not all([out_trade_no, total_fee]):
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        doc = manage.client["recharge_records"].find_one({"order": out_trade_no})
        if not doc:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        if doc.get("amount") != total_fee / 100:
            xml_data = wxpay.generate_xml_data({"return_code": "FAIL", "return_msg": "验证失败"})
            return Response(xml_data)
        xml_data = wxpay.generate_xml_data({"return_code": "SUCCESS", "return_msg": "OK"})
        manage.client["recharge_records"].update({"order": out_trade_no}, {"$set": {"trade_id": transaction_id, "state": 1}})
        return Response(xml_data)
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)


def get_balance_payment():
    """余额支付"""
    try:
        user_id = g.user_data["user_id"]
        # 参数
        trade_id = request.json.get("trade_id")
        password = request.json.get("password")
        if not password:
            return response(msg="Bad Request: Miss params: 'trade_id'.", code=1, status=400)
        if not password:
            return response(msg="请输入密码", code=1)
        # 校验密码
        password_b64 = base64.b64encode(password.encode()).decode()
        doc = manage.client["user"].find_one({"uid": user_id, "password": password_b64})
        if not doc:
            return response(msg="密码错误", code=1)
        trade_doc = manage.client["trade"].find_one({"trade_id": trade_id})
        trade_amount = trade_doc["trade_amount"]
        order = trade_doc["order"]
        balance = doc["balance"]
        # 自己不能购买自己的商品
        cursor = manage.client["order"].find({"order": order})
        data_list = [doc for doc in cursor]
        works_id = data_list[0]["works_id"]
        doc = manage.client["works"].find_one({"uid": works_id})
        seller_id = doc["user_id"]
        if user_id == seller_id:
            return response(msg="自己不能购买自己的商品", code=1)
        if balance < trade_amount:
            return response(msg="余额不足", code=1)
        # 支付
        doc = manage.client["user"].update({ "uid": user_id}, {"$inc": {"balance": -trade_amount}})
        if doc["n"] == 0:
            return response(msg="支付失败", code=1)
        # 支付完成
        doc = manage.client["order"].update({"order": order}, {"$set": {"state": 2}}, multi=True)
        if doc["n"] == 0:
            raise Exception("'order' state update failed")
        # 卖家balance更新
        doc = manage.client["user"].update({ "uid": seller_id}, {"$inc": {"balance": trade_amount}})
        if doc["n"] == 0:
            raise Exception(f"seller '{seller_id}' balance update failed")
        # 将商品添加到用户图片库
        add_user_goods_api(order, user_id, seller_id)
        return response()
    except Exception as e:
        manage.log.error(e)
        return response(msg="Internal Server Error: %s." % str(e), code=1, status=500)