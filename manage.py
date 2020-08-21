#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: manage.py
@Time: 2020-06-30 16:26:29
@Author: money 
"""
import os
import sys
import functools
import datetime
import pymongo
from flask_cors import CORS
from dateutil import parser  # pip3  install python-dateutil 
from core import app_login_api, app_list_api, app_user_api, app_order_api, app_works_api
from core import admin_login_api, admin_index_api, admin_front_api, admin_user_api, admin_opinion_api, \
    admin_operating_api, admin_system_api, admin_finance_api, admin_works_api
from utils import util
from flask import Flask, jsonify, request, g, Response
from constant.constant import DOMAIN


# 将根目录添加到sys路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


# 创建应用
app = Flask(__name__)
# 允许跨域
CORS(app, supports_credentials=True)
# 允许输出中文
app.config["JSON_AS_ASCII"] = False
# 生成密钥 base64.b64encode(os.urandom(64)).decode()
SECRET_KEY = "p7nHRvtLdwW07sQBoh/p9EBmHXv9DAcutk2vlj4MdSPNgFeTobUVJ3Ss2Wwl3T3tuv/ctTpPw+nQKMafU3MRJQ=="
app.secret_key = SECRET_KEY
# 允许上传的文件类型
# ALLOWED_EXTENSIONS = ["txt", "pdf", "png", "jpg", "jpeg", "gif", "mp3", "svg", "avi", "mov", "rmvb", "rm", "flv", "mp4", "3gp", "asf", "asx"]

# 创建日志
log = util.Logger("log_debug")
# 输出日志信息
log.info("The application has started.")
# 连接mongoDB
mongo = util.MongoDB(log)
# 连接数据库
client = mongo.client["local_writer"]["microfigure"]
# 云数据库链接
# CONN_ADDR1 = "dds-uf6c62f85a588a641741-pub.mongodb.rds.aliyuncs.com:3717" 
# CONN_ADDR2 = "dds-uf6c62f85a588a642965-pub.mongodb.rds.aliyuncs.com:3717"
# REPLICAT_SET = "mgset-32825379"
# username = "root"
# password = "Rd123!@#"
# # 获取mongoclient
# client = pymongo.MongoClient([CONN_ADDR1, CONN_ADDR2], replicaSet=REPLICAT_SET)
# # 管理员授权
# client.admin.authenticate(username, password)
# client = client["microfigure"]

# 路径
url = "/api/v1"
# 时间戳起始时间
init_date = "1970-01-01T08:00:00Z"
# python 没有IOSDate类型 需要借助parser.parse来转 # pip3  install python-dateutil 
init_stamp = parser.parse(init_date)


def auth_user_login(f):
    """用户状态判断"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            user_data = {
                "user_id": None,
                "user_info": None
            }
            token = request.headers.get("token")
            if token:
                pipeline = [
                    {"$match": {"token": token}},
                    {"$project": {"_id": 0, "uid": 1, "nick": 1, "sex": 1, "head_img_url": {"$concat": [DOMAIN, "$head_img_url"]}, "sign": 1, "mobile": 1, 
                                  "background_url": {"$concat": [DOMAIN, "$background_url"]}, "works_num": 1, "label": 1, "login_time": 1, "group": 1, 
                                  "create_time": 1, "update_time": 1, "auth": 1}}
                ]
                cursor = client["user"].aggregate(pipeline)
                data_list = [doc for doc in cursor]
                if not data_list:
                    return util.response(msg="登录失效", code=1, status=401)

                doc = data_list[0]
                # 判断token是否失效
                date0 = datetime.datetime.fromtimestamp(doc.get("login_time") // 1000)
                # 生成token
                date1 = datetime.datetime.strptime(date0.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                date2 = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
                delta = date2 - date1
                if delta.days > 1:
                    return util.response(msg="登录失效", code=1, status=401)
                uid = doc.get("uid")
                user_data = {
                "user_id": uid,
                "user_info": doc
                }
        except Exception as e:
            log.error(e)
        finally:
            g.user_data = user_data
        return f(*args, **kwargs)

    return wrapper


def auth_admin_login(f):
    """管理员登录校验"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 验证token
            token = request.headers.get("token")
            from utils.util import response
            if not token:
                return response(msg="Bad Request: Miss params 'token'.", code=1, status=400)
            doc = client["user"].find_one({"token": token, "type": {"$in": ["super","admin"]}}, 
                                          {"_id": 0, "uid": 1, "type": 1, "nick": 1, "sex": 1, "sign": 1, "mobile": 1, "role_id": 1})
            if not doc:
                return response(msg="Bad Request: The user doesn't exist.", code=1, status=400)   
            if doc["type"] not in ["super", "admin"]:
                return response(msg="Bad Request: You don't have permission", code=1, status=400)
            uid = doc.get("uid")
            user_data = {
                "user_id": uid,
                "user_info": doc
            }
            g.user_data = user_data
        except Exception as e:
            log.error(e)
            return
        return f(*args, **kwargs)

    return wrapper


def auth_amdin_role(f):
    """管理员角色权限校验"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # 验证token
            module_id = request.headers.get("module_id")
            permission_id = request.headers.get("permission_id")
            from utils.util import response
            if not module_id:
                return response(msg="Bad Request: Miss params 'module_id'.", code=1, status=400)
            if not permission_id:
                return response(msg="Bad Request: Miss params 'permission_id'.", code=1, status=400)
            user_id = g.user_data["user_id"]
            doc = client["role"].find_one({"module_id": module_id, "permission_id": permission_id})
            if not doc:
                return response(msg="您没有操作权限，请联系超级管理员", code=1)
        except Exception as e:
            log.error(e)
            return
        return f(*args, **kwargs)

    return wrapper


@app.after_request
def response_headers(response):
    """处理跨域问题"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Content-Struct-Type"] = "HotAppServerApi"
    return response


############################################################【微图APP前端API】############################################################


@app.route(f"{url}/banner", methods=["GET"])
def get_banner():
    """轮播图接口"""
    return app_list_api.get_banner()


@app.route(f"{url}/total", methods=["GET"])
@auth_user_login
def total_list():
    """发现页列表接口"""
    return app_list_api.get_total_list()


@app.route(f"{url}/pic", methods=["GET"])
@auth_user_login
def pic_list():
    """图集页列表接口"""
    return app_list_api.get_pic_list()


@app.route(f"{url}/video", methods=["GET"])
@auth_user_login
def video_list():
    """影集页列表接口"""
    return app_list_api.get_video_list()


@app.route(f"{url}/article", methods=["GET"])
@auth_user_login
def article_list():
    """图文页列表接口"""
    return app_list_api.get_article_list()


@app.route(f"{url}/atlas/detail", methods=["GET"])
@auth_user_login
def pic_detail():
    """图集详情页列表接口"""
    return app_list_api.get_pic_detail()


@app.route(f"{url}/video/detail", methods=["GET"])
@auth_user_login
def video_detail():
    """影集详情页列表接口"""
    return app_list_api.get_video_detail()


@app.route(f"{url}/article/detail", methods=["GET"])
@auth_user_login
def article_detail():
    """图文详情页列表接口"""
    return app_list_api.get_article_detail()


@app.route(f"{url}/article/hot", methods=["GET"])
@auth_user_login
def hot_article_list():
    """图文热点文章列表接口"""
    return app_list_api.get_hot_article_list()


@app.route(f"{url}/video/top", methods=["GET"])
@auth_user_login
def video_top_list():
    """影集置顶列表接口"""
    return app_list_api.get_video_top_list()


@app.route(f"{url}/label_kw", methods=["GET"])
@auth_user_login
def hot_kw_label():
    """标签、热搜词接口"""
    return app_list_api.get_label_kw()


@app.route(f"{url}/browse", methods=["POST"])
@auth_user_login
def browse_records():
    """浏览记录接口"""
    return app_list_api.post_browse_records()


@app.route(f"{url}/hot/keyword", methods=["GET"])
def hot_keyword():
    """热搜词接口"""
    return app_list_api.get_hot_keyword()


@app.route(f"{url}/search/keyword", methods=["GET"])
def search_keyword():
    """搜索关键词接口"""
    return app_list_api.get_search_keyword()


@app.route(f"{url}/search/works", methods=["GET"])
@auth_user_login
def search_works():
    """搜索作品接口"""
    return app_list_api.get_search_works()


@app.route(f"{url}/blacklist", methods=["POST"])
@auth_user_login
def user_blacklist():
    """拉黑用户或作品接口"""
    return app_list_api.post_blacklist()


@app.route(f"{url}/captcha", methods=["GET"])
def pic_captcha():
    """图片验证码接口"""
    return app_login_api.get_captcha()


@app.route(f"{url}/sms", methods=["POST"])
def sms_code():
    """短信验证码接口"""
    return app_login_api.post_sms_code()


@app.route(f"{url}/sms/verify", methods=["POST"])
def sms_code_verify():
    """短信验证码校验接口"""
    return app_login_api.post_sms_verify()


@app.route(f"{url}/register", methods=["POST"])
def user_register():
    """用户注册接口"""
    return app_login_api.post_register()


@app.route(f"{url}/login/account", methods=["POST"])
def login_account():
    """账户登录接口"""
    return app_login_api.post_account_login()


@app.route(f"{url}/login/mobile", methods=["POST"])
def login_mobile():
    """手机登录接口"""
    return app_login_api.post_mobile_login()


@app.route(f"{url}/oauth/bind", methods=["POST"])
def oauth_bind():
    """第三方绑定接口"""
    return app_login_api.post_oauth_bind()


@app.route(f"{url}/oauth/login", methods=["POST"])
def oauth_login():
    """第三方登录接口"""
    return app_login_api.post_oauth_login()


@app.route(f"{url}/logout", methods=["GET"])
@auth_user_login
def user_logout():
    """退出接口"""
    return app_login_api.get_user_logout()


@app.route(f"{url}/user/message", methods=["GET"])
@auth_user_login
def user_message():
    """我的消息"""
    return app_user_api.get_user_message()


@app.route(f"{url}/user/message/alter", methods=["PUT"])
@auth_user_login
def user_message_alter():
    """删除我的消息"""
    return app_user_api.put_user_message_alter()


@app.route(f"{url}/user/follow/search", methods=["GET"])
def user_follow_search():
    """我的关注搜索"""
    return app_user_api.get_user_follow_search()


@app.route(f"{url}/user/follow/cancel", methods=["PUT"])
@auth_user_login
def user_follow_cancel():
    """我的关注取消"""
    return app_user_api.put_user_follow_state()


@app.route(f"{url}/user/follow/news", methods=["GET"])
@auth_user_login
def user_follow_news():
    """我的关注作品最新动态"""
    return app_user_api.get_user_follow_works()


@app.route(f"{url}/user/info", methods=["GET"])
@auth_user_login
def user_info():
    """用户基本信息接口"""
    return app_user_api.get_userinfo()


@app.route(f"{url}/user/interest", methods=["GET"])
@auth_user_login
def user_interest_label():
    """用户推荐兴趣标签接口"""
    return app_user_api.get_user_interest_label()


@app.route(f"{url}/user/head/update", methods=["PUT"])
@auth_user_login
def user_head_img_update():
    """用户更换图像接口"""
    return app_user_api.put_user_head_img()


@app.route(f"{url}/user/background/update", methods=["PUT"])
@auth_user_login
def user_background_img_update():
    """用户更换背景图接口"""
    return app_user_api.put_user_background_img()


@app.route(f"{url}/user/info/alter", methods=["PUT"])
@auth_user_login
def user_info_alter():
    """修改基本信息接口"""
    return app_user_api.put_alter_userinfo()


@app.route(f"{url}/works/like", methods=["POST"])
@auth_user_login
def works_like():
    """作品点赞接口"""
    return app_list_api.post_works_like()


@app.route(f"{url}/comment/list", methods=["GET"])
@auth_user_login
def comment_list():
    """评论列表页接口"""
    return app_list_api.get_comment_list()


@app.route(f"{url}/works/comment", methods=["POST"])
@auth_user_login
def works_comment():
    """作品评论记录接口"""
    return app_list_api.post_comment_records()


@app.route(f"{url}/comment/like", methods=["POST"])
@auth_user_login
def works_comment_like():
    """作品评论点赞接口"""
    return app_list_api.post_comment_like()


@app.route(f"{url}/comment/delete", methods=["PUT"])
@auth_user_login
def works_comment_delete():
    """作品评论删除接口"""
    return app_list_api.put_delete_comment()


@app.route(f"{url}/comment/report", methods=["POST"])
@auth_user_login
def works_comment_report():
    """作品评论举报接口"""
    return app_list_api.post_comment_report()


@app.route(f"{url}/author/follow", methods=["POST"])
@auth_user_login
def author_follow():
    """作者关注接口"""
    return app_list_api.post_follow_user()


@app.route(f"{url}/custom/label/option", methods=["GET"])
def custom_label_option():
    """自定义供选标签接口"""
    return app_list_api.get_option_label()


@app.route(f"{url}/custom/label", methods=["POST"])
@auth_user_login
def custom_label():
    """自定义标签接口"""
    return app_list_api.post_custom_label()


@app.route(f"{url}/user/sales/record", methods=["GET"])
@auth_user_login
def user_sales_record():
    """用户销售记录接口"""
    return app_user_api.get_user_sales_records()


@app.route(f"{url}/user/data/statistic", methods=["GET"])
@auth_user_login
def user_data_statistic():
    """用户商品概况接口"""
    return app_user_api.get_user_data_statistic()


@app.route(f"{url}/withdrawal/bank", methods=["GET"])
@auth_user_login
def withdrawal_bank_show():
    """提现银行接口"""
    return app_user_api.get_user_withdrawal_bank()


@app.route(f"{url}/user/balance", methods=["GET"])
@auth_user_login
def user_balance():
    """用户账户余额接口"""
    return app_user_api.get_user_balance()


@app.route(f"{url}/user/withdrawal", methods=["POST"])
@auth_user_login
def user_withdrawal_apply():
    """用户提现申请接口"""
    return app_user_api.post_withdrawal_apply()


@app.route(f"{url}/user/home/page", methods=["GET"])
@auth_user_login
def user_home_page():
    """用户主页接口"""
    return app_user_api.get_user_home_page()


@app.route(f"{url}/user/follow/list", methods=["GET"])
def user_follow_list():
    """用户的关注列表"""
    return app_user_api.get_user_follow_list()


@app.route(f"{url}/user/fans/list", methods=["GET"])
def user_fans_list():
    """用户的粉丝列表"""
    return app_user_api.get_user_fans_list()


@app.route(f"{url}/user/works/manage", methods=["GET"])
@auth_user_login
def user_works_manage():
    """我的作品管理"""
    return app_user_api.get_works_manage()


@app.route(f"{url}/user/history/comment", methods=["GET"])
@auth_user_login
def user_history_comment():
    """我的历史评论记录"""
    return app_user_api.get_user_comment_history()


@app.route(f"{url}/user/history/like", methods=["GET"])
@auth_user_login
def user_history_comment_like():
    """我的点赞历史记录"""
    return app_user_api.get_user_like_history()


@app.route(f"{url}/user/goods/list", methods=["GET"])
@auth_user_login
def user_goods_list():
    """我的商品列表"""
    return app_user_api.get_user_goods_list()


@app.route(f"{url}/user/goods/state", methods=["PUT"])
@auth_user_login
def user_goods_state():
    """删除图片商品"""
    return app_user_api.put_user_goods_state()


@app.route(f"{url}/user/goods/detail", methods=["GET"])
@auth_user_login
def user_goods_detail():
    """我的商品详情"""
    return app_user_api.get_goods_detail()


@app.route(f"{url}/user/upload/common", methods=["POST"])
@auth_user_login
def user_material_upload():
    """素材上传通用接口"""
    return app_works_api.post_material_upload_common()


@app.route(f"{url}/user/audio/common", methods=["POST"])
@auth_user_login
def user_audio_upload():
    """音频上传通用接口"""
    return app_works_api.post_audio_upload_common()


@app.route(f"{url}/user/local/upload", methods=["POST"])
@auth_user_login
def user_local_upload():
    """用户本地上传接口"""
    return app_works_api.post_pic_material_upload()


@app.route(f"{url}/user/pic/material/list", methods=["GET"])
@auth_user_login
def user_pic_material_list():
    """用户图片素材库列表接口"""
    return app_works_api.get_pic_material()


@app.route(f"{url}/user/histroy/label", methods=["GET"])
@auth_user_login
def user_histroy_label():
    """用户历史标签接口"""
    return app_works_api.get_user_history_label()


@app.route(f"{url}/user/label/search", methods=["GET"])
@auth_user_login
def user_altas_label_searc():
    """图集搜索标签接口"""
    return app_works_api.get_altas_search_label()


@app.route(f"{url}/user/creation/pic", methods=["POST"])
@auth_user_login
def user_creation_pic_works():
    """用户创作图片作品接口"""
    return app_works_api.post_create_pic_works()


@app.route(f"{url}/user/creation/atlas", methods=["POST"])
@auth_user_login
def user_creation_atlas_works():
    """用户创作图集作品接口"""
    return app_works_api.post_pic_collect_works()


@app.route(f"{url}/user/creation/article", methods=["POST"])
@auth_user_login
def user_creation_article_works():
    """用户创作图文作品接口"""
    return app_works_api.post_create_article_works()


@app.route(f"{url}/user/material/list", methods=["GET"])
@auth_user_login
def user_info_material_list():
    """我的素材库列表接口"""
    return app_user_api.get_pic_material_list()


@app.route(f"{url}/user/material/title", methods=["PUT"])
@auth_user_login
def user_info_material_title():
    """我的素材修改标题接口"""
    return app_user_api.put_pic_material_title()


@app.route(f"{url}/user/material/label", methods=["PUT"])
@auth_user_login
def user_info_material_label():
    """我的素材修改标签接口"""
    return app_user_api.put_pic_material_label()


@app.route(f"{url}/user/material/state", methods=["PUT"])
@auth_user_login
def user_info_material_state():
    """我的素材删除接口"""
    return app_user_api.put_pic_material_state()


@app.route(f"{url}/user/material/upload", methods=["POST"])
@auth_user_login
def user_info_material_upload():
    """我的素材上传接口"""
    return app_user_api.post_pic_material_upload()


@app.route(f"{url}/user/audio/list", methods=["GET"])
@auth_user_login
def user_info_audio_list():
    """我的音频素材列表接口"""
    return app_user_api.get_audio_material_list()


@app.route(f"{url}/user/audio/title", methods=["PUT"])
@auth_user_login
def user_info_audio_title():
    """我的音频素材修改标题接口"""
    return app_user_api.put_audio_material_title()


@app.route(f"{url}/user/audio/label", methods=["PUT"])
@auth_user_login
def user_info_audio_label():
    """我的音频素材修改标题接口"""
    return app_user_api.put_audio_material_label()


@app.route(f"{url}/user/audio/state", methods=["PUT"])
@auth_user_login
def user_info_audio_state():
    """删除音频素材"""
    return app_user_api.put_audio_material_state()


@app.route(f"{url}/user/audio/upload", methods=["POST"])
@auth_user_login
def user_info_audio_upload():
    """上传音频素材"""
    return app_user_api.post_audio_material_upload_pic()


@app.route(f"{url}/user/works/list", methods=["GET"])
@auth_user_login
def user_info_works_list():
    """我的图片作品列表"""
    return app_user_api.get_pic_wokrs_list()


@app.route(f"{url}/user/works/delete", methods=["PUT"])
@auth_user_login
def user_info_works_delete():
    """删除作品"""
    return app_user_api.put_pic_works_state()


@app.route(f"{url}/user/works/pic/detail", methods=["GET"])
@auth_user_login
def user_info_works_manage():
    """图片申请上架详情页面"""
    return app_user_api.get_pic_works_details()


# 弃用
@app.route(f"{url}/user/portrait", methods=["POST"])
@auth_user_login
def user_portrait():
    """肖像权接口"""
    return app_user_api.post_pic_portrait()


@app.route(f"{url}/user/portrait/detail", methods=["GET"])
@auth_user_login
def user_portrait_detail():
    """肖像权详情接口"""
    return app_user_api.get_pic_portrait_detail()


@app.route(f"{url}/user/portrait/editor", methods=["PUT"])
@auth_user_login
def user_portrait_editor():
    """肖像权编辑接口"""
    return app_user_api.put_pic_portrait_editor()


# 弃用
@app.route(f"{url}/user/property", methods=["POST"])
@auth_user_login
def user_property():
    """物产权接口"""
    return app_user_api.post_pic_property()


@app.route(f"{url}/user/property/detail", methods=["GET"])
@auth_user_login
def user_property_detail():
    """物产权详情接口"""
    return app_user_api.get_pic_products_detail()


@app.route(f"{url}/user/property/editor", methods=["PUT"])
@auth_user_login
def user_property_editor():
    """物产权编辑接口"""
    return app_user_api.put_pic_property_editor()


@app.route(f"{url}/user/works/apply", methods=["POST"])
@auth_user_login
def user_works_apply():
    """图片作品上架申请"""
    return app_user_api.post_pic_apply()


@app.route(f"{url}/user/works/pic/editor", methods=["PUT"])
@auth_user_login
def user_works_pic_editor():
    """图片作品编辑"""
    return app_user_api.put_pic_works_editor()


@app.route(f"{url}/user/altas/detail", methods=["GET"])
@auth_user_login
def user_altas_detail():
    """图集上架申请详情"""
    return app_user_api.get_user_altas_detail()


@app.route(f"{url}/user/altas/apply", methods=["POST"])
@auth_user_login
def user_altas_apply():
    """图集上架申请"""
    return app_user_api.post_altas_apply()


@app.route(f"{url}/user/altas/editor", methods=["PUT"])
@auth_user_login
def user_altas_editor():
    """图集上架申请编辑"""
    return app_user_api.post_altas_detail_editor()



@app.route(f"{url}/user/works/article", methods=["GET"])
@auth_user_login
def user_works_article():
    """图文作品列表接口"""
    return app_user_api.get_article_wokrs_list()


@app.route(f"{url}/user/works/batch", methods=["POST"])
@auth_user_login
def user_works_batch_apply():
    """图集批量上架接口"""
    return app_user_api.put_works_shelvers_apply()


@app.route(f"{url}/area", methods=["GET"])
@auth_user_login
def area_list():
    """区域地址接口"""
    return app_user_api.get_area_list()


@app.route(f"{url}/cameraman/auth", methods=["POST"])
@auth_user_login
def area_auth_cameraman():
    """摄影师认证接口"""
    return app_user_api.post_user_auth_cameraman()


@app.route(f"{url}/works/share", methods=["POST"])
def user_works_share():
    """作品分享接口"""
    return app_user_api.post_share_works()


@app.route(f"{url}/car/add", methods=["POST"])
@auth_user_login
def user_car_add():
    """加入购物车接口"""
    return app_order_api.post_add_car()


@app.route(f"{url}/car/delete", methods=["DELETE"])
@auth_user_login
def user_car_delete():
    """加入购物车接口"""
    return app_order_api.delete_user_car_goods()


@app.route(f"{url}/car/list", methods=["GET"])
@auth_user_login
def user_car_list():
    """购物车列表接口"""
    return app_order_api.get_user_car_list()


@app.route(f"{url}/car/merge", methods=["PUT"])
@auth_user_login
def user_car_merge():
    """购物车合并订单接口"""
    return app_order_api.post_car_generate_order()


@app.route(f"{url}/order/list", methods=["GET"])
@auth_user_login
def user_order_list():
    """订单列表接口"""
    return app_order_api.get_user_order_list()


@app.route(f"{url}/order/detail", methods=["GET"])
@auth_user_login
def user_order_detail():
    """订单详情接口"""
    return app_order_api.get_order_detail()


@app.route(f"{url}/order/state", methods=["PUT"])
@auth_user_login
def user_order_state():
    """取消订单接口"""
    return app_order_api.put_user_order()


@app.route(f"{url}/order/payment", methods=["POST"])
@auth_user_login
def order_payment():
    """订单支付接口"""
    return app_order_api.post_order_payment()


@app.route(f"{url}/alipay/callback", methods=["GET", "POST"])
@auth_user_login
def alipay_callback_verify():
    """支付宝回调验证接口"""
    return app_order_api.post_alipay_callback_verify()


@app.route(f"{url}/wechat/callback", methods=["GET", "POST"])
@auth_user_login
def wechat_callback_verify():
    """微信支付回调验证接口"""
    return app_order_api.post_wechat_callback_verify()


@app.route(f"{url}/app/callback", methods=["POST"])
@auth_user_login
def app_callback():
    """支付成功后app回调接口"""
    return app_order_api.post_app_callback()


@app.route(f"{url}/balance/recharge", methods=["POST"])
@auth_user_login
def balance_recharge():
    """余额充值接口"""
    return app_order_api.post_top_up()


@app.route(f"{url}/recharge/alipay/callback", methods=["POST"])
@auth_user_login
def balance_recharge_callback_alipay():
    """余额充值支付宝回调接口"""
    return app_order_api.post_top_up_alipay_callback_verify()


@app.route(f"{url}/recharge/wechat/callback", methods=["POST"])
@auth_user_login
def balance_recharge_callback_wechat():
    """余额充值微信回调接口"""
    return app_order_api.post_top_up_wechat_callback_verify()


@app.route(f"{url}/video/label/search", methods=["GET"])
@auth_user_login
def user_video_label_searc():
    """影集搜索标签接口"""
    return app_works_api.get_video_search_label()


@app.route(f"{url}/video/pic/upload", methods=["POST"])
@auth_user_login
def user_video_pic_upload():
    """影集图片素材上传接口"""
    return app_works_api.post_video_material_upload()


@app.route(f"{url}/user/video/create", methods=["POST"])
@auth_user_login
def user_video_works_create():
    """影集作品制作接口"""
    return app_works_api.post_video_collect_works()


############################################################【后台管理系统API】############################################################


@app.route(f"{url}/admin/login", methods=["POST"])
def admin_login():
    """后台登录"""
    return admin_login_api.post_admin_login()


@app.route(f"{url}/admin/alter/password", methods=["PUT"])
@auth_admin_login
def admin_alter_password():
    """后台管理员修改密码"""
    return admin_login_api.put_admin_password()


@app.route(f"{url}/admin/index/collect", methods=["GET"])
@auth_admin_login
def admin_index_top_collect():
    """后台首页顶部统计接口"""
    return admin_index_api.get_top_statistics()


@app.route(f"{url}/admin/index/trend", methods=["GET"])
@auth_admin_login
def admin_index_trend_collect():
    """后台首页趋势统计接口"""
    return admin_index_api.get_data_statistics()


@app.route(f"{url}/admin/banner/list", methods=["GET"])
@auth_admin_login
def admin_front_banner():
    """后台前台banner接口"""
    return admin_front_api.get_banner()


@app.route(f"{url}/admin/banner/link", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_link():
    """后台前台banner修改链接接口"""
    return admin_front_api.put_banner_link()


@app.route(f"{url}/admin/banner/order", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_order():
    """后台前台banner修改序号接口"""
    return admin_front_api.put_banner_order()


@app.route(f"{url}/admin/banner/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_state():
    """后台前台banner删除接口"""
    return admin_front_api.put_banner_state()


@app.route(f"{url}/admin/banner/upload", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_front_banner_upload():
    """后台前台banner上传接口"""
    return admin_front_api.post_upload_banner()


@app.route(f"{url}/admin/hot/keyword", methods=["GET"])
@auth_admin_login
def admin_front_hot_keyword():
    """后台前台热搜词列表接口"""
    return admin_front_api.get_hot_keyword_list()


@app.route(f"{url}/admin/keyword/add", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_front_hot_keyword_add():
    """后台前台添加热搜词接口"""
    return admin_front_api.post_add_keyword()


@app.route(f"{url}/admin/keyword/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_hot_keyword_delete():
    """后台前台删除热搜词接口"""
    return admin_front_api.put_delete_keyword()


@app.route(f"{url}/admin/label/list", methods=["GET"])
@auth_admin_login
def admin_front_label_list():
    """后台前台可选标签列表接口"""
    return admin_front_api.get_label_list()


@app.route(f"{url}/admin/label/priority", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_label_priority():
    """后台前台可选标签优先级接口"""
    return admin_front_api.put_lable_priority()


@app.route(f"{url}/admin/label/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_label_state():
    """后台前台可选标签列表接口"""
    return admin_front_api.put_show_label()


@app.route(f"{url}/admin/top/video/list", methods=["GET"])
@auth_admin_login
def admin_front_video_list():
    """后台前台置顶影集列表接口"""
    return admin_front_api.get_video_top_list()


@app.route(f"{url}/admin/top/video/sort", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_video_sort():
    """后台前台置顶影集排序接口"""
    return admin_front_api.put_video_order_sort()


@app.route(f"{url}/admin/top/video/delete", methods=["DELETE"])
@auth_admin_login
@auth_amdin_role
def admin_front_video_delete():
    """后台前台置顶影集删除接口"""
    return admin_front_api.delete_video_works()


@app.route(f"{url}/admin/top/video/choose", methods=["GET"])
@auth_admin_login
def admin_front_video_choose():
    """后台前台置添加置顶影集时，提供可选影集列表接口"""
    return admin_front_api.get_option_video_list()


@app.route(f"{url}/admin/top/video/add", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_front_video_add():
    """后台前台置添加置顶影集接口"""
    return admin_front_api.put_video_works()


@app.route(f"{url}/admin/material/pic/list", methods=["GET"])
@auth_admin_login
def admin_material_list():
    """后台内容管理图片素材列表接口"""
    return admin_works_api.get_admin_pic_material_list()


@app.route(f"{url}/admin/material/pic/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_material_state():
    """后台内容管理图片素材删除接口"""
    return admin_works_api.put_pic_material_state()


@app.route(f"{url}/admin/material/pic/detail", methods=["GET"])
@auth_admin_login
def admin_material_detail():
    """后台内容管理图片素材详情接口"""
    return admin_works_api.get_pic_material_detail()


@app.route(f"{url}/admin/material/pic/editor", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_material_editor():
    """后台内容管理图片素材编辑接口"""
    return admin_works_api.put_pic_material()


@app.route(f"{url}/admin/material/audio/list", methods=["GET"])
@auth_admin_login
def admin_audio_list():
    """后台内容管理音频素材列表接口"""
    return admin_works_api.get_audio_material_list()


@app.route(f"{url}/admin/material/audio/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_audio_state():
    """后台内容管理音频素材删除接口"""
    return admin_works_api.put_audio_material_state()


@app.route(f"{url}/admin/material/audio/detail", methods=["GET"])
@auth_admin_login
def admin_audio_detail():
    """后台内容管理音频素材详情接口"""
    return admin_works_api.get_audio_material_detail()


@app.route(f"{url}/admin/material/audio/editor", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_audio_editor():
    """后台内容管理音频素材编辑接口"""
    return admin_works_api.put_audio_material()


@app.route(f"{url}/admin/material/audio/cover", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_audio_cover():
    """后台内容管理音频素材封面更新接口"""
    return admin_works_api.put_audio_material_cover()


@app.route(f"{url}/admin/works/list", methods=["GET"])
@auth_admin_login
def admin_pic_atlas_list():
    """后台内容管理图片、图集、图文作品列表接口"""
    return admin_works_api.get_all_works_list()


@app.route(f"{url}/admin/works/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_pic_atlas_state():
    """后台内容管理图片、图集作品状态接口"""
    return admin_works_api.put_pic_works_state()


@app.route(f"{url}/admin/works/pic/editor", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_pic_editor():
    """后台内容管理图片作品编辑接口"""
    return admin_works_api.put_pic_works_info()


@app.route(f"{url}/admin/works/audit/list", methods=["GET"])
@auth_admin_login
def admin_works_audit_list():
    """后台内容管理作品审核列表接口"""
    return admin_works_api.get_works_audit_list()


@app.route(f"{url}/admin/works/audit", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_works_audit():
    """后台内容管理作品审核接口"""
    return admin_works_api.put_pic_works_autio_state()


@app.route(f"{url}/admin/works/pic/detail", methods=["GET"])
@auth_admin_login
def admin_works_pic_detail():
    """后台内容管理图片作品详情接口"""
    return admin_works_api.get_pic_works_detail()


@app.route(f"{url}/admin/works/atlas/detail", methods=["GET"])
@auth_admin_login
def admin_works_atlas_detail():
    """后台内容管理图集作品详情接口"""
    return admin_works_api.get_atals_detail()


@app.route(f"{url}/admin/atlas/material/list", methods=["GET"])
@auth_admin_login
def admin_atlas_detail_material():
    """后台内容管理图集作品详情图片素材库接口"""
    return admin_works_api.get_altas_deital_material_list()


@app.route(f"{url}/admin/atlas/pic/add", methods=["PUT"])
@auth_admin_login
def admin_atlas_detail_add_pic_id():
    """后台内容管理图集作品详情添加图片接口"""
    return admin_works_api.put_altas_works_pic_id()


@app.route(f"{url}/admin/atlas/pic/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_atlas_detail_pic_delete():
    """后台内容管理图集作品详情删除图片接口"""
    return admin_works_api.put_altas_works_pic_delete()


@app.route(f"{url}/admin/works/atlas/editor", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_atlas_detail_editor():
    """后台内容管理图集作品详情编辑接口"""
    return admin_works_api.put_altas_works_editor()


@app.route(f"{url}/admin/works/article/detail", methods=["GET"])
@auth_admin_login
def admin_works_article_detail():
    """后台内容管理图文作品详情接口"""
    return admin_works_api.get_article_works_detail()


# 舍弃
@app.route(f"{url}/admin/user/list", methods=["GET"])
@auth_admin_login
def admin_user_list():
    """后台用户列表接口"""
    return admin_user_api.get_user_list()


@app.route(f"{url}/admin/user/filter", methods=["GET"])
@auth_admin_login
def admin_user_filter():
    """后台用户列表筛选接口"""
    return admin_user_api.get_user_filter_list()


@app.route(f"{url}/admin/user/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_state():
    """后台用户冻结恢复接口"""
    return admin_user_api.put_user_state()


@app.route(f"{url}/admin/user/group", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_group():
    """后台用户移动组接口"""
    return admin_user_api.put_user_group()


@app.route(f"{url}/admin/user/detail", methods=["GET"])
@auth_admin_login
def admin_user_detail():
    """后台用户详情接口"""
    return admin_user_api.get_user_detail()


@app.route(f"{url}/admin/user/reset/password", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_reset_password():
    """后台用户重置密码接口"""
    return admin_user_api.put_user_password()


@app.route(f"{url}/admin/user/alter/mobile", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_alter_mobile():
    """后台用户更改手机接口"""
    return admin_user_api.put_user_mobile()


@app.route(f"{url}/admin/user/send/message", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_user_send_message():
    """后台给用户发送消息接口"""
    return admin_user_api.post_user_message()


@app.route(f"{url}/admin/user/balance/operation", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_balance_operatin():
    """后台用户余额操作接口"""
    return admin_user_api.put_user_balance_operation()


@app.route(f"{url}/admin/user/balance/record", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_user_balance_record():
    """后台用户余额记录接口"""
    return admin_user_api.get_user_balance_records()


@app.route(f"{url}/admin/org/list", methods=["GET"])
@auth_admin_login
def admin_org_list():
    """后台机构用户列表接口"""
    return admin_user_api.get_org_list()


@app.route(f"{url}/admin/org/filter", methods=["GET"])
@auth_admin_login
def admin_org_filter():
    """后台机构用户列表筛选接口"""
    return admin_user_api.get_org_filter_list()


@app.route(f"{url}/admin/org/name", methods=["GET"])
@auth_admin_login
def admin_org_name():
    """后台机构名接口"""
    return admin_user_api.get_org_name_list()


@app.route(f"{url}/admin/create/org", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_create_org():
    """后台创建机构接口"""
    return admin_user_api.post_create_org_account()


# 舍弃
@app.route(f"{url}/admin/user/audit", methods=["GET"])
@auth_admin_login
def admin_user_audit():
    """后台用户待审核列表接口"""
    return admin_user_api.get_user_audit()


@app.route(f"{url}/admin/user/audit/filter", methods=["GET"])
@auth_admin_login
def admin_user_audit_filter():
    """后台用户待审核列表搜索接口"""
    return admin_user_api.get_user_audit_filter()


@app.route(f"{url}/admin/user/audit/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_user_audit_state():
    """后台用户待审核列表审核接口"""
    return admin_user_api.put_user_audit_state()


@app.route(f"{url}/admin/user/audit/detail", methods=["GET"])
@auth_admin_login
def admin_user_audit_detail():
    """后台用户待审核详情接口"""
    return admin_user_api.get_user_audit_detail()


@app.route(f"{url}/admin/comment/list", methods=["GET"])
@auth_admin_login
def admin_comment_list():
    """后台评论列表接口"""
    return admin_opinion_api.get_report_comment_list()


@app.route(f"{url}/admin/comment/search", methods=["GET"])
@auth_admin_login
def admin_comment_list_search():
    """后台评论列表搜索接口"""
    return admin_opinion_api.get_report_comment_search()


@app.route(f"{url}/admin/comment/audit", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_comment_audit():
    """后台评论审核接口"""
    return admin_opinion_api.put_report_comment_state()


@app.route(f"{url}/admin/comment/statistical", methods=["GET"])
@auth_admin_login
def admin_comment_list_statistical():
    """后台评论统计接口"""
    return admin_opinion_api.get_report_comment_top()


@app.route(f"{url}/admin/bad/list", methods=["GET"])
@auth_admin_login
def admin_comment_bad_show():
    """后台敏感词展示接口"""
    return admin_opinion_api.get_bad_keyword_list()


@app.route(f"{url}/admin/comment/keyword/add", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_comment_keyword_add():
    """后台添加敏感关键词接口"""
    return admin_opinion_api.post_add_bad_keyword()


@app.route(f"{url}/admin/price/show", methods=["GET"])
@auth_admin_login
def admin_platform_price_show():
    """后台平台定价信息展示接口"""
    return admin_operating_api.get_platform_info()


@app.route(f"{url}/admin/price", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_platform_price():
    """后台平台定价接口"""
    return admin_operating_api.post_platform_pricing()


@app.route(f"{url}/admin/recomm/list", methods=["GET"])
@auth_admin_login
def admin_recomm_list():
    """后台推荐作品列表接口"""
    return admin_operating_api.get_recomm_works_list()


@app.route(f"{url}/admin/recomm/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_recomm_delete():
    """后台推荐作品删除接口"""
    return admin_operating_api.put_recomm_state()


@app.route(f"{url}/admin/recomm/option", methods=["GET"])
@auth_admin_login
def admin_recomm_option():
    """后台推荐作品选择接口"""
    return admin_operating_api.get_option_works_list()


@app.route(f"{url}/admin/recomm/option/search", methods=["GET"])
@auth_admin_login
def admin_recomm_option_search():
    """后台推荐作品选择搜索接口"""
    return admin_operating_api.get_option_works_list_search()


@app.route(f"{url}/admin/recomm/add", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_recomm_add():
    """后台添加推荐作品接口"""
    return admin_operating_api.post_add_recomm_works()


@app.route(f"{url}/admin/manage/list", methods=["GET"])
@auth_admin_login
def admin_manage_list():
    """后台管理员列表接口"""
    return admin_system_api.get_admin_account_list()


@app.route(f"{url}/admin/manage/search", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_manage_search():
    """后台管理员列表搜索接口"""
    return admin_system_api.get_admin_account_search()


@app.route(f"{url}/admin/manage/create", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_manage_create_account():
    """后台管理员列表搜索接口"""
    return admin_system_api.post_create_account()


@app.route(f"{url}/admin/manage/delete", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_manage_list_delete():
    """后台管理员列表删除接口"""
    return admin_system_api.put_admin_account_state()



@app.route(f"{url}/admin/permission/list", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_manage_permission_list():
    """后台管理员权限列表接口"""
    return admin_system_api.get_admin_permission_list()


@app.route(f"{url}/admin/reset/password", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_manage_reset_password():
    """后台管理员重置密码接口"""
    return admin_system_api.put_admin_password_reset()


@app.route(f"{url}/admin/info/alter", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_manage_account_alter():
    """后台管理员信息修改接口"""
    return admin_system_api.put_admin_account_alter()


@app.route(f"{url}/admin/create/role", methods=["POST"])
@auth_admin_login
@auth_amdin_role
def admin_permission_create_role():
    """后台管理员创建角色接口"""
    return admin_system_api.post_add_permissions_role()


@app.route(f"{url}/admin/editor/role", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_permission_create_role_editor():
    """后台角色编辑接口"""
    return admin_system_api.put_add_permissions_role_editor()


@app.route(f"{url}/admin/role/list", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_role_list():
    """后台角色列表接口"""
    return admin_system_api.get_role_list()


@app.route(f"{url}/admin/role/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_role_state():
    """后台角色删除接口"""
    return admin_system_api.put_role_state()


@app.route(f"{url}/admin/log/list", methods=["GET"])
@auth_admin_login
def admin_log_list():
    """后台日志列表接口接口"""
    return admin_system_api.get_admin_operation_log()


@app.route(f"{url}/admin/finance/list", methods=["GET"])
@auth_admin_login
def admin_finance_order_list():
    """后台订单列表接口"""
    return admin_finance_api.get_order_list()


@app.route(f"{url}/admin/finance/refund", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_finance_order_refund():
    """后台订单退款接口"""
    return admin_finance_api.put_order_refund()


@app.route(f"{url}/admin/finance/detail", methods=["GET"])
@auth_admin_login
def admin_finance_order_detail():
    """后台订单详情接口"""
    return admin_finance_api.get_order_detail()


@app.route(f"{url}/admin/finance/withdrawal", methods=["GET"])
@auth_admin_login
def admin_finance_withdrawal_records():
    """后台提现记录接口"""
    return admin_finance_api.get_withdrawal_records()


@app.route(f"{url}/admin/finance/recharge", methods=["GET"])
@auth_admin_login
def admin_finance_recharge_records():
    """后台充值记录接口"""
    return admin_finance_api.get_order_recharge()


@app.route(f"{url}/admin/finance/recharge/channel", methods=["GET"])
@auth_admin_login
def admin_finance_recharge_channel():
    """后台充值渠道接口"""
    return admin_finance_api.get_recharge_channel()


@app.route(f"{url}/admin/finance/withdrawal/audit", methods=["GET"])
@auth_admin_login
def admin_finance_withdrawal_audit():
    """后台提现审核列表接口"""
    return admin_finance_api.get_withdrawal_records_audit()


@app.route(f"{url}/admin/finance/withdrawal/state", methods=["PUT"])
@auth_admin_login
@auth_amdin_role
def admin_finance_withdrawal_state():
    """后台提现审核接口"""
    return admin_finance_api.put_withdrawal_records_state()


@app.route(f"{url}/admin/finance/withdrawal/export", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_finance_withdrawal_export():
    """后台提现记录导出接口"""
    return admin_finance_api.get_withdrawal_records_export()


@app.route(f"{url}/admin/finance/recharge/export", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_finance_recharge_export():
    """后台充值记录导出接口"""
    return admin_finance_api.get_order_recharge_export()


@app.route(f"{url}/admin/finance/audit/export", methods=["GET"])
@auth_admin_login
@auth_amdin_role
def admin_finance_withdrawal_audit_export():
    """后台提现审核记录导出接口"""
    return admin_finance_api.get_withdrawal_records_audit_export()


@app.route(f"{url}/test", methods=["GET", "POST"])
def test():
    data = request.args
    # import xmltodict
    # xml = xmltodict.unparse({"xml": data}, pretty=True, full_document=False).encode("utf-8")
    # return jsonify({"return_code": "SUCCESS", "return_msg": "OK"})
    # return Response(xml)
    # rest = request.form.to_dict()
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)