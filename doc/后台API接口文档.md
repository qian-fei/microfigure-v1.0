#### 微图后台API接口文档

##### 通用说明

```js
1.请求方式
获取数据：GET	// JSON格式
提交数据：POST	// JSON格式	文件上传为Form格式
修改数据：PUT	// JSON格式
2.返回字段
{
	data: 数据	// None无数据返回
    msg: 信息		// 错误信息
    code: 错误码	// 1错误 0正常
}
3.前端请求携带token
将token存入请求头中上传	// 后端直接从headers中获取token
4.前端请求携带模块id和权限id	// 只有需要权限校验的接口才需要携带
将module_id和permission_id存入请求头中上传
4.服务器返回token
将token存入响应头中返回

注意：后台除登录接口以外，其余全部接口都需要携带token。
```

#### 一、登录退出模块

##### 1.登录接口

请求URL：

```
/api/v1/admin/login
```

请求方式：

```
POST
```

接口说明：

```
管理员登录。
```

请求参数: 

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| account  |  是  |  String  | 账号     |
| password |  是  |  String  | 密码     |

返回字段：

|    返回字段     | 必须 | 字段类型 | 字段说明 | 备注                                 |
| :-------------: | :--: | :------: | :------- | ------------------------------------ |
|    role_info    |  是  |  Object  | 角色信息 | 外层结构                             |
|    user_info    |  是  |  Object  | 用户信息 | 外层结构                             |
|   module_list   |  是  |  Array   | 模块列表 | 【属于role_info】                    |
| permission_list |  是  |  Array   | 权限列表 | 【属于role_info】                    |
|    module_id    |  否  |  String  | 模块id   | 【属于module_list、permission_list】 |
|   module_name   |  否  |  String  | 模块名   | 【属于module_list】                  |
|  permission_id  |  否  |  String  | 权限id   | 【属于permission_list】              |
| permission_name |  否  |  String  | 权限名   | 【属于permission_list】              |
|       uid       |  是  |  String  | 用户id   |                                      |
|      nick       |  是  |  String  | 昵称     |                                      |
|       sex       |  是  |  String  | 性别     |                                      |
|      sign       |  是  |  String  | 签名     |                                      |

返回示例：

```json
{
    "data": {
        "role_info": {
            "module_list": [{
                    "module_id": "001",
                    "module_name": "首页",
                	"permission_list": [{
                        	"permission_id": "002",
                    		"permission_name": "会员审核"
                    	},
                        ...
                    ]
                },
                ...
            ],
            "permission_list": [{
                    "module_id": "001",
                    "permission_id": "002",
                    "permission_name": "会员审核"
                },
                ...
            ]
        },
        "user_info": {
            "mobile": "17725021251",
            "nick": "我是祖国的花朵",
            "sex": "男",
            "sign": "我是大哥",
            "type": "super",
            "uid": "fjdasgnd"
        }
    },
    "code": 0,
    "msg": "Request successful."
}
```

#### 二、首页模块

##### 1.顶、底部统计接口

请求URL：

```
/api/v1/admin/index/collect
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回日收入、用户数、商品数、新增作品、作品审核、会员审核数据。
```

请求参数:  无

返回字段：

|   返回字段    | 必须 | 字段类型 | 字段说明   |
| :-----------: | :--: | :------: | :--------- |
| register_num  |  是  | Integer  | 用户数     |
|   goods_num   |  是  | Integer  | 商品数     |
|  amount_num   |  是  | Integer  | 今日收入   |
| inc_works_num |  是  | Integer  | 新增作品数 |
|   works_num   |  是  | Integer  | 作品审核数 |
|   user_num    |  是  | Integer  | 用户审核数 |

返回示例：

```json
{
    "data": {
        "register_num": 2500,
        "goods_num": 2500,
        "amount_num": 250,
        "inc_works_num": 250,
        "works_num": 250,
        "user_num": 250
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.收入趋势接口

请求URL：

```
/api/v1/admin/index/trend
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回累计收入、售出商品、同比、收入趋势数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   day    |  是  | Integer  | 7天/30天 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明       | 备注                 |
| :----------: | :--: | :------: | :------------- | -------------------- |
| compare_data |  是  |  Object  | 收入、售出汇总 | 外层结构             |
|  data_list   |  是  |  Array   | 收入趋势       | 外层结构             |
| total_amount |  是  | Integer  | 累计收入       | 【属于compare_data】 |
| amount_delta |  是  |  Float   | 同比上升       | 【属于compare_data】 |
|  total_sale  |  是  | Integer  | 出售商品       | 【属于compare_data】 |
|  sale_delta  |  是  |  Float   | 同比上升       | 【属于compare_data】 |
|    amount    |  是  |  Float   | 日收入         | 【属于data_list】    |
|     date     |  是  |  String  | 日期           | 【属于data_list】    |

返回示例：

```json
{
    "data": {
        "compare_data": {
            "total_amount": 2500.00,
            "amount_delta": 250,
            "total_sale": 0.1,
            "sale_delta": 0.1,
            
        },
        "data_list": [{
 				"amount": 800.00,
            	"date": "2020-07-28"
        	}
        
        ]
    }
    "msg": "Request successful.",
    "code": 0
}
```

#### 三、前台设置

##### 1.banner列表

请求URL：

```
/api/v1/admin/banner/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回banner数据。
```

请求参数:  无

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注                 |
| :---------: | :--: | :------: | :------- | -------------------- |
|     uid     |  是  |  String  |          | 外层结构             |
|    order    |  是  | Integer  | 序号     | 外层结构             |
|   pic_url   |  是  |  String  | 图片路径 | 【属于compare_data】 |
|    link     |  是  |  String  | 链接     | 【属于compare_data】 |
| create_time |  是  |  String  | 创建时间 |                      |
| update_time |  是  |  String  | 创建时间 |                      |

返回示例：

```json
{
    "data": [{
        	"uid": "001",
        	"order": 1,
        	"pic_url": "http://www.baidu.com/img/1.jpg",
        	"link": "http://www.baidu.com",
        	"create_time": "2020-07-28",
        	"update_time": "2020-07-28"
    	},
        ...
    ]
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.修改banner链接

请求URL：

```
/api/v1/admin/banner/link
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改banner链接。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数  | 必须 | 参数类型 | 参数说明    |
| :-------: | :--: | :------: | :---------- |
|   link    |  是  |  String  |             |
| banner_id |  是  |  String  | banner的uid |

返回字段: 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.修改banner序号接口

请求URL：

```
/api/v1/admin/banner/order
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改banner序号。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数  | 必须 | 参数类型 | 参数说明          |
| :-------: | :--: | :------: | :---------------- |
|    inc    |  是  | Integer  | 向上传1，向下传-1 |
| banner_id |  是  |  String  | banner的uid       |

返回字段: 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.banner删除接口

请求URL：

```
/api/v1/admin/banner/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除banner。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数  | 必须 | 参数类型 | 参数说明    |
| :-------: | :--: | :------: | :---------- |
| banner_id |  是  |  String  | banner的uid |

返回字段: 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.热搜词列表接口

请求URL：

```
/api/v1/admin/hot/keyword
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取热搜词。
```

请求参数:  无

返回字段: 

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 热搜词   |

返回示例：

```json
{
    "data": [
        "中国",
        "5G",
        "华为",
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.添加热搜词接口

请求URL：

```
/api/v1/admin/keyword/add
```

请求方式：

```
POST
```

接口说明：

```
添加关键词。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回字段:  无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.删除关键词接口

请求URL：

```
/api/v1/admin/keyword/delete
```

请求方式：

```
PUT
```

接口说明：

```
删除关键词。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回字段:  无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.可选栏目列表接口

请求URL：

```
/api/v1/admin/label/list
```

请求方式：

```
GET
```

接口说明：

```
获取标签数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                    |
| :------: | :--: | :------: | :------- | ----------------------- |
|   num    |  是  | Integer  | 页数     | 从1开始                 |
|   page   |  是  | Integer  | 页码     | 从1开始                 |
|   type   |  是  |  String  | 类型     | 图集传pic， 影集传video |

返回字段：

|  返回字段  | 必须 | 字段类型 | 字段说明     | 备注                                   |
| :--------: | :--: | :------: | :----------- | -------------------------------------- |
| label_list |  是  |  Array   | 标签列表数据 | 外层结构                               |
|   count    |  是  | Integer  | 数据通条数   | 外层结构                               |
|    uid     |  是  |  String  | 唯一标识     | 【属于label_list】                     |
|  priority  |  是  |  Float   | 优先级       | 【属于label_list】                     |
|    type    |  是  |  String  | 类型         | pic图集，video影集。【属于label_list】 |
|   label    |  是  |  String  | 标签         | 【属于label_list】                     |
| works_num  |  是  | Integer  | 作品数       | 【属于label_list】                     |
|   state    |  是  | Integer  | 状态         | 0隐藏，1正常。【属于label_list】       |

返回示例：

```json
{
    "data": {
        "count": 250,
        "label_list": [{
        	"uid": "123456",
        	"priority": 1.0,
        	"type": "pic",
        	"label": "别墅",
        	"works_num": 2000,
        	"state": 1
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.标签的显示、隐藏、删除接口

请求URL：

```
/api/v1/admin/label/state
```

请求方式：

```
PUT
```

接口说明：

```
关键词的显示、隐藏、删除。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                        |
| :------: | :--: | :------: | :------- | --------------------------- |
| keyword  |  是  |  Array   | 关键词   | 一个或多个都采用array       |
|  state   |  是  | Integer  | 状态     | 显示传1，隐藏传0， 删除传-1 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.上传banner

请求URL：

```
/api/v1/admin/banner/upload
```

请求方式：

```
POST
```

接口说明：

```
上传banner。请求头需要携带module_id和permission_id
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| pic_list | 是   | Array    | 文件字段 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.设置标签优先级

请求URL：

```
/api/v1/admin/label/priority
```

请求方式：

```
PUT
```

接口说明：

```
设置标签优先级。请求头需要携带module_id和permission_id
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| -------- | ---- | -------- | -------- | ---- |
| label_id | 是   | String   | 标签id   |      |
| priority | 是   | Integer  | 优先级数 |      |

返回字段：无

返回示例: 

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

#### 四、用户管理模块

##### 1.用户列表接口（舍弃）

请求URL：

```
/api/v1/admin/user/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                            |
| :------: | :--: | :------: | :------- | ----------------------------------------------- |
|   num    |  是  | Integer  | 页数     | 从1开始                                         |
|   page   |  是  | Integer  | 页码     | 从1开始                                         |
|  group   |  是  |  String  | 类型     | 全部传default, 一般用户传comm, 认证摄影师传auth |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 | 备注                         |
| :----------: | :--: | :------: | :------- | ---------------------------- |
|     uid      |  是  |  String  | 用户id   |                              |
| head_img_url |  是  |  String  | 头像路径 |                              |
|     nick     |  是  |  String  | 昵称     |                              |
|   account    |  是  |  String  | 账号     |                              |
| create_time  |  是  |  String  | 时间     |                              |
|    group     |  是  |  String  | 组       | comm一般用户，auth认证摄影师 |

返回字段：

```json
{
    "data": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.用户列表筛选接口

请求URL：

```
/api/v1/admin/user/filter
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                      |
| :------: | :--: | :------: | :------- | ------------------------- |
|   num    |  是  | Integer  | 页数     | 从1开始                   |
|   page   |  是  | Integer  | 页码     | 从1开始                   |
| category |  是  |  String  | 分类     | 账号传account, 昵称传nick |
| content  |  否  |  String  | 关键词   | 搜索内容                  |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明     | 备注                                     |
| :----------: | :--: | :------: | :----------- | ---------------------------------------- |
|     list     |  是  |  Array   | 用户列表数据 | 外层结构                                 |
|    count     |  是  | Integer  | 数据总条数   | 外层结构                                 |
|     auth     |  是  | Integer  | 摄影师数     | 外层结构                                 |
|     comm     |  是  | Integer  | 一般用户数   | 外层结构                                 |
|     uid      |  是  |  String  | 用户id       | 【属于list】                             |
| head_img_url |  是  |  String  | 头像路径     | 【属于list】                             |
|     nick     |  是  |  String  | 昵称         | 【属于list】                             |
|   account    |  是  |  String  | 账号         | 【属于list】                             |
| create_time  |  是  |  String  | 时间         | 【属于list】                             |
|    group     |  是  |  String  | 组           | comm一般用户，auth认证摄影师【属于list】 |

返回字段：

```json
{
    "data": {
        "count":250,
        "auth": 120,
        "comm": 130,
        "list":[{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth"
    		},
        	...
    	],
    }
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.用户冻结、恢复接口

请求URL：

```
/api/v1/admin/user/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，操作用户账号状态。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注             |
| :------: | :--: | :------: | :------- | ---------------- |
| user_id  |  是  |  Array   | 用户uid  |                  |
|  state   |  是  | Integer  | 状态     | 冻结传0, 恢复传1 |

返回字段： 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.用户详情接口

请求URL：

```
/api/v1/admin/user/detail
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，操作用户账号状态。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| user_id  |  是  |  String  | 用户uid  |      |

返回字段：

|    返回字段    | 必须 | 字段类型 | 字段说明   | 备注                         |
| :------------: | :--: | :------: | :--------- | ---------------------------- |
|      uid       |  是  |  String  | 用户id     |                              |
|      nick      |  是  |  String  | 昵称       |                              |
|  head_img_url  |  是  |  String  | 头像路径   |                              |
| background_url |  是  |  String  | 模板       |                              |
|    account     |  是  |  String  | 时间       |                              |
|     label      |  是  |  Array   | 组         |                              |
|     state      |  是  | Integer  | 状态       | 0冻结，1正常                 |
|      sex       |  是  |  String  | 性别       |                              |
|     group      |  是  |  String  | 分组       | comm一般用户，auth认证摄影师 |
|     mobile     |  是  |  String  | 手机       |                              |
|    balance     |  是  |  Float   | 余额       |                              |
|      sign      |  是  |  String  | 签名       |                              |
|    org_name    |  否  |  String  | 机构名称   |                              |
|     belong     |  否  |  String  | 账号类型   |                              |
|    pic_num     |  是  | Integer  | 微图作品数 |                              |
|   atlas_num    |  是  | Integer  | 图集作品数 |                              |
|   video_num    |  是  | Integer  | 影集作品数 |                              |
|  create_time   |  是  |  String  | 时间       |                              |

返回字段：

```json
{
    "data": {
        "uid": "1232546",
        "nick": "我是祖国的花朵",
        "head_img_url": "http://www.baidu.com/img/1.png",
        "background_url": "http://www.baidu.com/img/1.png",
        "account": "12345678911",
        "label": ["开朗", "顽皮"],
        "state": 1,
        "sex": "保密",
        "group": "auth",
        "mobile": "17725021251",
        "balance": 120.00,
        "org_name": "金夫人",
        "belong": "主账号",
        "sign": "我是祖国的花朵",
        "pic_num": 150,
        "atlas_num": 150,
        "video_num": 150,
        "create_time": "2020-07-28"
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.重置密码接口

请求URL：

```
/api/v1/admin/user/reset/password
```

请求方式：

```
PUT
```

接口说明：

```
重置密码。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| user_id  |  是  |  String  | 用户uid  |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.修改用户手机接口

请求URL：

```
/api/v1/admin/user/alter/mobile
```

请求方式：

```
PUT
```

接口说明：

```
修改手机。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| user_id  |  是  |  String  | 用户uid  |
|  mobile  |  是  |  String  | 用户手机 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.给用户发送消息接口

请求URL：

```
/api/v1/admin/user/send/message
```

请求方式：

```
POST
```

接口说明：

```
给用户发送消息。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| user_id  |  是  |  String  | 用户uid  |
| content  |  是  |  String  | 消息内容 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.用户余额操作接口

请求URL：

```
/api/v1/admin/user/balance/operation
```

请求方式：

```
PUT
```

接口说明：

```
操作用户余额。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明           |
| :------: | :--: | :------: | :----------------- |
| user_id  |  是  |  String  | 用户uid            |
|   inc    |  是  | Integer  | 充值为正，扣除为负 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.用户余额记录列表接口

请求URL：

```
/api/v1/admin/user/balance/record
```

请求方式：

```
GET
```

接口说明：

```
余额记录表。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                   |
| :--------: | :--: | :------: | :------- | ---------------------- |
|    page    |  是  | Integer  | 页码     |                        |
|    num     |  是  | Integer  | 页数     |                        |
|  user_id   |  是  |  String  | 用户uid  |                        |
| start_time |  是  |  String  | 开始时间 |                        |
|  end_time  |  是  |  String  | 结束时间 | 开始与结束之间最长30天 |

返回字段：

|  返回字段   | 必须 | 字段类型 |   字段说明   |                             备注                             |
| :---------: | ---- | :------: | :----------: | :----------------------------------------------------------: |
| record_list | 是   |  Array   | 金额记录列表 |                           外层结构                           |
|    count    | 是   | Integer  |   数据条数   |                           外层结构                           |
|   user_id   | 是   |  String  |    用户id    |                     【属于record_list】                      |
|    type     | 是   |  String  |     类型     | goods商品售卖，user_income充值，user_reduce提现，admin_income后台充值，admin_reduce后台提现。【属于record_list】 |
|    order    | 是   |  String  |     单号     |                     【属于record_list】                      |
|   amount    | 是   |  String  |     金额     |                     【属于record_list】                      |
|   balance   | 是   |  Float   |     余额     |                     【属于record_list】                      |
| create_time | 是   |  String  |   创建时间   |                     【属于record_list】                      |

返回示例：

```json
{
    "data": {
        "count": 250,
        "record_list": [{
        	"user_id": "011111",
        	"type": "user_income",
        	"order": "211595130000000",
        	"amount": "+250.0",
        	"balance": 1500.00,
        	"create_time": "2020-07-28"
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 10.机构列表接口（舍弃）

请求URL：

```
/api/v1/admin/org/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回机构用户的数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                     |
| :------: | :--: | :------: | :------- | ---------------------------------------- |
|   page   |  是  | Integer  | 页码     | 从1开始                                  |
|   num    |  是  | Integer  | 页数     | 从1开始                                  |
|  belong  |  是  |  String  | 账号类型 | 全部传default, 主账号master, 子账号slave |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |             备注             |
| :----------: | ---- | :------: | :------: | :--------------------------: |
|     uid      | 是   |  String  |  用户id  |                              |
|   org_name   | 是   |  String  | 机构名称 |                              |
|    belong    | 是   |  String  | 账号类型 |  master主账号，slave从账号   |
| head_img_url | 是   |  String  | 头像路径 |                              |
|    group     | 是   |  String  |   分组   | comm一般用户，auth认证摄影师 |
|   account    | 是   |  String  |   账号   |                              |
| create_time  | 是   |  String  |   时间   |                              |
|     nick     | 是   |  String  |   昵称   |                              |

返回示例：

```json
{
    "data": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth",
        	"belong": "master",
        	"org_name": "重庆摄影"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 11.机构列表筛选接口

请求URL：

```
/api/v1/admin/org/filter
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回机构用户的数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                     |
| :------: | :--: | :------: | :------- | ---------------------------------------- |
|   page   |  是  | Integer  | 页码     | 从1开始                                  |
|   num    |  是  | Integer  | 页数     | 从1开始                                  |
| category |  是  |  String  | 分类     | 机构名称org_name, 昵称传nick             |
| content  |  是  |  String  | 搜索内容 |                                          |
|  belong  |  是  |  String  | 账号类型 | 全部传default, 主账号master, 子账号slave |

返回字段：

|   返回字段   | 必须 | 字段类型 |   字段说明   |                    备注                    |
| :----------: | ---- | :------: | :----------: | :----------------------------------------: |
|     list     | 是   |  Array   | 机构列表数据 |                  外层结构                  |
|    count     | 是   | Integer  |   数总条数   |                  外层结构                  |
|     uid      | 是   |  String  |    用户id    |                【属于list】                |
|   org_name   | 是   |  String  |   机构名称   |                【属于list】                |
|    belong    | 是   |  String  |   账号类型   |  master主账号，slave从账号。【属于list】   |
| head_img_url | 是   |  String  |   头像路径   |              【属于org_list】              |
|    group     | 是   |  String  |     分组     | comm一般用户，auth认证摄影师。【属于list】 |
|   account    | 是   |  String  |     账号     |                【属于list】                |
| create_time  | 是   |  String  |     时间     |                【属于list】                |
|     nick     | 是   |  String  |     昵称     |                【属于list】                |
|    state     | 是   | Integer  |     状态     |          0冻结，1正常【属于list】          |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth",
        	"belong": "master",
        	"org_name": "重庆摄影"
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 12.用户审核列表接口（舍弃）

请求URL：

```
/api/v1/admin/user/audit
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户待审核的数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注    |
| :------: | :--: | :------: | :------- | ------- |
|   page   |  是  | Integer  | 页码     | 从1开始 |
|   num    |  是  | Integer  | 页数     | 从1开始 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 | 备注                         |
| :----------: | :--: | :------: | :------- | ---------------------------- |
|     uid      |  是  |  String  | 用户id   |                              |
| head_img_url |  是  |  String  | 头像路径 |                              |
|     nick     |  是  |  String  | 昵称     |                              |
|   account    |  是  |  String  | 账号     |                              |
| update_time  |  是  |  String  | 时间     |                              |
|    group     |  是  |  String  | 组       | comm一般用户，auth认证摄影师 |
| id_card_name |  是  |  String  | 真实姓名 |                              |
|   id_card    |  是  |  String  | 身份证号 |                              |

返回示例：

```json
{
    "data": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth",
        	"id_card_name": "张三",
        	"id_card": "50022819941111111"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 13.用户审核列表搜索接口

请求URL：

```
/api/v1/admin/user/audit/filter
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户待审核的数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                      |
| :------: | :--: | :------: | :------- | ------------------------- |
|   page   |  是  | Integer  | 页码     | 从1开始                   |
|   num    |  是  | Integer  | 页数     | 从1开始                   |
| category |  是  |  String  | 分类     | 账号传account, 昵称传nick |
| content  |  是  |  String  | 搜索内容 |                           |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明     | 备注                                       |
| :----------: | :--: | :------: | :----------- | ------------------------------------------ |
|     list     |  是  |  Array   | 用户列表数据 | 外层结构                                   |
|    count     |  是  |  String  | 数据总数     | 外层结构                                   |
|     uid      |  是  |  String  | 用户id       | 【属于list】                               |
| head_img_url |  是  |  String  | 头像路径     | 【属于list】                               |
|     nick     |  是  |  String  | 昵称         | 【属于list】                               |
|   account    |  是  |  String  | 账号         | 【属于list】                               |
| update_time  |  是  |  String  | 时间         | 【属于list】                               |
|    group     |  是  |  String  | 组           | comm一般用户，auth认证摄影师。【属于list】 |
| id_card_name |  是  |  String  | 真实姓名     | 【属于list】                               |
|   id_card    |  是  |  String  | 身份证号     | 【属于list】                               |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"head_img_url": "http://www.baidu.com/img/1.png",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"group": "auth",
        	"id_card_name": "张三",
        	"id_card": "50022819941111111"
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 14.用户审核列表审核接口

请求URL：

```
/api/v1/admin/user/audit/state
```

请求方式：

```
PUT
```

接口说明：

```
审核账号。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注             |
| :------: | :--: | :------: | :------- | ---------------- |
| user_id  |  是  |  Array   | 用户id   |                  |
|   auth   |  是  | Integer  | 是否通过 | 通过传2, 驳回传0 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 15.用户管理移动组

请求URL：

```
/api/v1/admin/user/group
```

请求方式：

```
PUT
```

接口说明：

```
移动用户组。请求头需要携带module_id和permission_id
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                         |
| -------- | ---- | -------- | -------- | ---------------------------- |
| user_id  | 是   | Array    | 用户id   |                              |
| group    | 是   | Integer  | 分组     | comm一般用户，auth认证摄影师 |

返回字段：无

返回示例: 

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 16.获取机构名称

请求URL：

```
/api/v1/admin/org/name
```

请求方式：

```
GET
```

接口说明：

```
获取机构名
```

请求参数：无

返回字段：无

返回示例: 

```json
{
    "data": [
        "金夫人",
        "银夫人",
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 17.创建机构账号

请求URL：

```
/api/v1/admin/create/org
```

请求方式：

```
POST
```

接口说明：

```
创建机构用户。请求头需要携带module_id和permission_id
```

请求参数：

| 请求参数       | 必须 | 参数类型 | 参数说明 | 备注                         |
| -------------- | ---- | -------- | -------- | ---------------------------- |
| nick           | 是   | String   | 昵称     |                              |
| account        | 是   | String   | 账号     |                              |
| label          | 是   | Array    | 标签     | 最多20个                     |
| sex            | 是   | String   | 性别     | 男 女 保密                   |
| mobile         | 是   | String   | 手机     |                              |
| sign           | 是   | String   | 签名     |                              |
| belong         | 是   | String   | 账号类型 | 主账号master, 子账号slave    |
| org_name       | 是   | String   | 机构名   |                              |
| group          | 是   | String   | 用户组   | comm一般用户，auth认证摄影师 |
| head_img_url   | 否   | String   | 头像     |                              |
| background_url | 否   | String   | 背景图   |                              |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 18.用户审核详情接口

请求URL：

```
/api/v1/admin/user/audit/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户详情数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| user_id  |  是  |  String  | 用户id   |

返回字段：

|   返回字段    | 必须 | 字段类型 | 字段说明   | 备注 |
| :-----------: | :--: | :------: | :--------- | ---- |
|     nick      |  是  |  String  | 昵称       |      |
|    account    |  是  |  String  | 账号       |      |
|    mobile     |  是  |  String  | 手机       |      |
| head_img_url  |  是  |  String  | 头像       |      |
| id_card_name  |  是  |  String  | 身份证姓名 |      |
|    id_card    |  是  |  String  | 身份证号   |      |
| id_card_a_url |  是  |  String  | 身份证正面 |      |
| id_card_b_url |  是  |  String  | 身份证反面 |      |
|  repre_works  |  是  |  Array   | 代表作品   |      |
|   home_addr   |  是  |  String  | 现居地址   |      |
| id_card_addr  |  是  |  String  | 身份证地址 |      |

返回示例：

```json
{
    "data": {
        "nick": "哈哈哈",
        "account": "17725021251",
        "mobile": "17725021251",
        "head_img_url": "http://www.baidu.com/img/1.png",
        "id_card_name": "张三",
        "id_card": "5002281xxxxxxx",
        "id_card_a_url": "http://www.baidu.com/img/1.png",
        "id_card_b_url": "http://www.baidu.com/img/1.png",
        "home_addr": "重庆市",
        "id_card_addr": "重庆市万州区",
        "repre-works": [
            "http://www.baidu.com/img/1.png",
            "http://www.baidu.com/img/1.png",
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```



#### 五、舆情监控模块

##### 1.评论列表接口（舍弃）

请求URL：

```
/api/v1/admin/comment/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回评论列表数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注    |
| :------: | :--: | :------: | :------- | ------- |
|   page   |  是  | Integer  | 页码     | 从1开始 |
|   num    |  是  | Integer  | 页数     | 从1开始 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 | 备注 |
| :----------: | :--: | :------: | :------- | ---- |
|     uid      |  是  |  String  | 评论id   |      |
| user_account |  是  |  String  | 用户账号 |      |
| works_title  |  是  |  String  | 作品标题 |      |
|   content    |  是  |  String  | 评论内容 |      |
| create_time  |  是  |  String  | 时间     |      |

返回示例：

```json
{
    "data": [{
        	"uid": "123456",
        	"user_account": "17725021251"
        	"works_title": "别墅",
        	"content": "这个别墅很菜",
        	"create_time": "2020-07-28"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.评论列表搜索接口

请求URL：

```
/api/v1/admin/comment/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回评论列表数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                      |
| :--------: | :--: | :------: | :------- | ------------------------- |
|    page    |  是  | Integer  | 页码     | 从1开始                   |
|    num     |  是  | Integer  | 页数     | 从1开始                   |
|  content   |  是  |  String  | 搜索内容 |                           |
| start_time |  否  |  String  | 开始时间 |                           |
|  end_time  |  否  |  String  | 结束时间 |                           |
|   state    |  是  | Integer  | 状态     | 正常评论传1， 举报评论传0 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 | 备注         |
| :----------: | :--: | :------: | :------- | ------------ |
|     list     |  是  |  Array   | 评论列表 | 外层结构     |
|    count     |  是  | Integer  | 总数     | 外层结构     |
|     uid      |  是  |  String  | 评论id   | 【属于list】 |
| user_account |  是  |  String  | 用户账号 | 【属于list】 |
| works_title  |  是  |  String  | 作品标题 | 【属于list】 |
|   content    |  是  |  String  | 评论内容 | 【属于list】 |
| create_time  |  是  |  String  | 时间     | 【属于list】 |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
        	"uid": "123456",
        	"user_account": "17725021251"
        	"works_title": "别墅",
        	"content": "这个别墅很菜",
        	"create_time": "2020-07-28"
    		},
      		...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.评论审核接口

请求URL：

```
/api/v1/admin/comment/audit
```

请求方式：

```
PUT
```

接口说明：

```
审核评论。请求头需要携带module_id和permission_id
```

请求参数:  

|   请求参数   | 必须 | 参数类型 | 参数说明 | 备注              |
| :----------: | :--: | :------: | :------- | ----------------- |
| comment_list |  是  |  Array   | 评论uid  |                   |
|    state     |  是  | Integer  | 状态     | -1删除，1标记正常 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.评论统计结构

请求URL：

```
    /api/v1/admin/comment/statistical
```

请求方式：

```
GET
```

接口说明：

```
评论统计
```

请求参数:  无

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明       |
| :----------: | :--: | :------: | :------------- |
|  bad_count   |  是  | Integer  | 敏感词数       |
| normal_count |  是  | Integer  | 新增其他评论数 |
| report_count |  是  | Integer  | 举报评论数     |

返回示例：

```json
{
    "data": {
        "bad_count": 250,
        "normal_count": 250,
        "report_count": 250
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.增加敏感词接口

请求URL：

```
/api/v1/admin/comment/keyword/add
```

请求方式：

```
POST
```

接口说明：

```
增加敏感词。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明     |
| :------: | :--: | :------: | :----------- |
| content  |  是  |  String  | 关键词字符串 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.敏感词展示接口

请求URL：

```
/api/v1/admin/bad/list
```

请求方式：

```
GET
```

接口说明：

```
敏感词展示。
```

请求参数:  无

请求字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

#### 六、运营管理模块

##### 1.平台定价接口

请求URL：

```
/api/v1/admin/price
```

请求方式：

```
POST
```

接口说明：

```
平台定价。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明           | 备注 |
| :------: | :--: | :------: | :----------------- | ---- |
| s_price  |  是  |  Float   | 规格S的价格        | ≥0   |
| m_price  |  是  |  Float   | 规格M的价格        | ≥0   |
| l_price  |  是  |  Float   | 规格L的价格        | ≥0   |
| k_price  |  是  |  Float   | 规格扩大授权的价格 | ≥0   |
|   fees   |  是  |  Float   | 手续费             | ≥0   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.推荐作品列表接口

请求URL：

```
/api/v1/admin/recomm/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回推荐作品数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                  |
| :------: | :--: | :------: | :------- | ------------------------------------- |
|   num    |  是  | Integer  | 页数     | ≥1                                    |
|   page   |  是  | Integer  | 页码     | ≥1                                    |
|   type   |  是  |  String  | 类型     | 发现传default, 微图传pic, 影集传video |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                               |
| :---------: | :--: | :------: | :--------- | -------------------------------------------------- |
| works_list  |  是  |  Array   | 作品列表   | 外层结构                                           |
|    count    |  是  | Integer  | 数据总条数 | 外层结构                                           |
|     uid     |  是  |  String  | 作品id     | 【属于works_list】                                 |
|    title    |  是  |  String  | 标题       | 【属于works_list】                                 |
|    type     |  是  |  String  | 类型       | tp图片，tj图集，yj影集，tw图文。【属于works_list】 |
|   author    |  是  |  String  | 作者       | 【属于works_list】                                 |
| browse_num  |  是  |  String  | 浏览量     | 【属于works_list】                                 |
| create_time |  是  |  String  | 时间       | 【属于works_list】                                 |

返回示例：

```json
{
    "data": {
        "count": 250,
        "works_list": [{
        	"uid": "123460",
        	"title": "自然",
        	"type": "tj",
        	"author": "我是祖国的花朵",
        	"browse_num": 999,
        	"create_time": "2020-07-28"
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.删除作品接口

请求URL：

```
/api/v1/admin/recomm/delete
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，返回推荐作品数据。请求头需要携带module_id和permission_id
```

请求参数: 

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| works_id |  是  |  String  | 作品id   |      |

返回字段： 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.作品选择列表接口（舍弃）

请求URL：

```
/api/v1/admin/recomm/option
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回未推荐作品数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                  |
| :------: | :--: | :------: | :------- | ------------------------------------- |
|   num    |  是  | Integer  | 页数     | ≥1                                    |
|   page   |  是  | Integer  | 页码     | ≥1                                    |
|   type   |  是  |  String  | 类型     | 发现传default, 微图传pic, 影集传video |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注                           |
| :---------: | :--: | :------: | :------- | ------------------------------ |
|     uid     |  是  |  String  | 作品id   |                                |
|    title    |  是  |  String  | 标题     |                                |
|    type     |  是  |  String  | 类型     | tp图片，tj图集，yj影集，tw图文 |
|   author    |  是  |  String  | 作者     |                                |
| browse_num  |  是  |  String  | 浏览量   |                                |
| create_time |  是  |  String  | 时间     |                                |

返回示例：

```json
{
    "data": [{
        	"uid": "123460",
        	"title": "自然",
        	"type": "tj",
        	"author": "我是祖国的花朵",
        	"browse_num": 999,
        	"create_time": "2020-07-28"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.作品选择搜索接口

请求URL：

```
/api/v1/admin/recomm/option/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回未推荐作品数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                                  |
| :--------: | :--: | :------: | :------- | ------------------------------------- |
|    num     |  是  | Integer  | 页数     | ≥1                                    |
|    page    |  是  | Integer  | 页码     | ≥1                                    |
|    type    |  是  |  String  | 类型     | 发现传default, 微图传pic, 影集传video |
|  content   |  否  |  String  | 搜索内容 |                                       |
|  category  |  否  |  String  | 分类     | 标题传title, 作者传author             |
| start_time |  是  |  String  | 开始时间 | 开始时间与结束时间不能超过30天        |
|  end_time  |  是  |  String  | 结束时间 |                                       |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                         |
| :---------: | :--: | :------: | :--------- | -------------------------------------------- |
|    list     |  是  |  Array   | 作品列表   | 外层结构                                     |
|    count    |  是  | Integer  | 数据总条数 | 外层结构                                     |
|     uid     |  是  |  String  | 作品id     | 【属于list】                                 |
|    title    |  是  |  String  | 标题       | 【属于list】                                 |
|    type     |  是  |  String  | 类型       | tp图片，tj图集，yj影集，tw图文。【属于list】 |
|   author    |  是  |  String  | 作者       | 【属于list】                                 |
| browse_num  |  是  |  String  | 浏览量     | 【属于list】                                 |
| create_time |  是  |  String  | 时间       | 【属于list】                                 |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
        	"uid": "123460",
        	"title": "自然",
        	"type": "tj",
        	"author": "我是祖国的花朵",
        	"browse_num": 999,
        	"create_time": "2020-07-28"
    		},
        	...
    	],
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.添加推荐作品

请求URL：

```
/api/v1/admin/recomm/add
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，添加推荐作品。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注       |
| :--------: | :--: | :------: | :------- | ---------- |
| works_list |  是  |  Array   | 作品uid  | 长度最长10 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.平台定价信息展示

请求URL：

```
/api/v1/admin/price/show
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回平台定价信息。
```

请求参数:  无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| l_price  |  是  |  Float   | 价格     |
| m_price  |  是  |  Float   | 价格     |
| s_price  |  是  |  Float   | 价格     |
| k_price  |  是  |  Float   | 价格     |
|   fees   |  是  |  Float   | 价格     |

返回示例：

```json
{
    "data": {
        "l_price": 55.0,
        "m_price": 55.0,
        "s_price": 55.0,
        "k_price": 55.0,
        "fees": 0.01
    },
    "msg": "Request successful.",
    "code": 0
}
```



#### 七、系统管理模块

##### 1.管理员列表接口（舍弃）

请求URL：

```
/api/v1/admin/manage/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取管理员数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
|   num    |  是  | Integer  | 页数     | ≥1   |
|   page   |  是  | Integer  | 页码     | ≥1   |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注 |
| :---------: | :--: | :------: | :------- | ---- |
|     uid     |  是  |  String  | 用户uid  |      |
|    nick     |  是  |  String  | 昵称     |      |
|   account   |  是  |  String  | 账号     |      |
|   mobile    |  是  |  String  | 手机     |      |
|    sole     |  是  |  String  | 角色     |      |
| create_time |  是  |  String  | 时间     |      |

返回示例：

```json
{
    "data": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"sole": "超级管理员",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"mobile": "17725021251"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.管理员列表搜索接口

请求URL：

```
/api/v1/admin/manage/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取管理员数据。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                |
| :------: | :--: | :------: | :------- | ----------------------------------- |
|   num    |  是  | Integer  | 页数     | ≥1                                  |
|   page   |  是  | Integer  | 页码     | ≥1                                  |
| content  |  是  |  String  | 搜索内容 |                                     |
|   type   |  是  |  String  | 类型     | 账号account 昵称nick 联系电话mobile |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注              |
| :---------: | :--: | :------: | :------- | ----------------- |
|    list     |  是  |  Array   | 作品列表 | 外层结构          |
|    count    |  是  | Integer  | 数据总数 | 外层结构          |
|     uid     |  是  |  String  | 用户uid  | 【属于list】      |
|    nick     |  是  |  String  | 昵称     | 【属于list】      |
|   account   |  是  |  String  | 账号     | 【属于list】      |
|   mobile    |  是  |  String  | 手机     | 【属于list】      |
|    role     |  是  |  String  | 角色     | 【属于list】      |
|  role_list  |  是  |  Array   | 角色列表 | 【属于list】      |
| create_time |  是  |  String  | 时间     | 【属于user_list】 |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
        	"uid": "123462",
        	"nick": "我是祖国的花朵",
        	"role": "超级管理员",
        	"account": "17725021251",
        	"create_time": "2020-07-28",
        	"mobile": "17725021251",
            "role_list": [{
                	"uid": "001",
                	"nick": "哈哈哈"
            	},
                ...
            ]
    		},
        	...
    	],
    }
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.管理员列表删除接口

请求URL：

```
/api/v1/admin/manage/delete
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除相关数据。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| user_id  |  是  |  String  | 用户uid  |      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.权限明细列表

请求URL：

```
/api/v1/admin/permission/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取权限明细。请求头需要携带module_id和permission_id
```

请求参数:  无

返回字段：

|    返回字段     | 必须 | 字段类型 | 字段说明 | 备注       |
| :-------------: | :--: | :------: | :------- | ---------- |
|    module_id    |  是  |  String  | 模块id   | 【第一级】 |
|   module_name   |  是  |  String  | 模块名   | 【第一级】 |
|      item       |  是  |  Array   | 菜单栏   | 【第一级】 |
|      menu       |  是  |  String  | 菜单名称 | 【第二级】 |
| permission_item |  是  |  Array   | 按钮栏   | 【第二级】 |
|      name       |  是  |  String  | 按钮名   | 【第三级】 |
|       uid       |  是  |  String  | 按钮uid  | 【第三级】 |

返回示例：

```json
{
  "data": [
    {
      "module_id": "004",
      "module_name": "用户管理",
      "item": [
        {
          "menu": "用户审核",
          "permission_item": [
            {
              "name": "通过",
              "uid": "071"
            },
			...
          ]
        },
        ...
      ]
    },
    ...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 5.创建权限角色

请求URL：

```
/api/v1/admin/create/role
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，创建角色。请求头需要携带module_id和permission_id
```

请求参数:  

|    请求参数     | 必须 | 参数类型 | 参数说明 | 备注                                                |
| :-------------: | :--: | :------: | :------- | --------------------------------------------------- |
|      nick       |  是  |  String  | 昵称     |                                                     |
|      desc       |  是  |  String  | 描述     |                                                     |
| permission_list |  是  |  Array   | 权限列表 | [{"module_id": "001", "permission_id": "001"}, ...] |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 6.获取角色列表接口

请求URL：

```
/api/v1/admin/role/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取角色列表。请求头需要携带module_id和permission_id
```

请求参数:  无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
|   uid    |  是  |  String  | 角色id   |
|   nick   |  是  |  String  | 模块名   |
|   desc   |  是  |  String  | 菜单栏   |

返回示例：

```json
{
  "data": [{
      "uid": "152451235",
      "nick": "用户管理员",
      "desc": "用户管理"
  	},
    ...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 7.角色删除接口

请求URL：

```
/api/v1/admin/role/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除角色。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| role_id  |  是  |  String  | 角色id   |      |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 8.日志列表接口

请求URL：

```
/api/v1/admin/log/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回日列表接口。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                            |
| :--------: | :--: | :------: | :------- | ------------------------------- |
|    num     |  是  | Integer  | 页数     |                                 |
|    page    |  是  | Integer  | 页码     |                                 |
|  content   |  是  |  String  | 内容     |                                 |
|    type    |  是  |  String  | 类型     | account账号 nick昵称 mobile电话 |
| start_time |  是  |  String  | 开始时间 |                                 |
|  end_time  |  是  |  String  | 结束时间 |                                 |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   |      |
| :---------: | :--: | :------: | :--------- | ---- |
|    count    |  是  | Integer  | 总数       |      |
|    list     |  是  |  Array   | 数据列表   |      |
|     uid     |  是  |  String  | 角色id     |      |
|    nick     |  是  |  String  | 昵称       |      |
|   account   |  是  |  String  | 账号       |      |
|     ip      |  是  |  String  | 操作用户ip |      |
|   content   |  是  |  String  | 操作内容   |      |
| create_time |  是  |  String  |            |      |

返回示例：

```json
{
  "data": [{
    	"uid": "001",
      	"nick": "我是祖国的花朵",
      	"account": "17725021250",
      	"ip": "101.132.138.152",
      	"content": "功能权限（页面）：按钮/字段权限",
      	"create_time": "2020-07-28"
  	},
    ...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 9.创建账号

请求URL：

```
/api/v1/admin/manage/create
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数, 创建账号。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                                  |
| :------: | :--: | :------: | :------- | ----------------------------------------------------- |
| account  |  是  |  String  | 账号     |                                                       |
|   nick   |  是  |  String  | 昵称     |                                                       |
|  mobile  |  是  |  String  | 手机     |                                                       |
|   role   |  是  |  Array   | 角色     | [{"id": , "name": }, ...] id为角色uid，nick为角色nick |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 10.素材上传通用接口

请求URL：

```
/api/v1/user/upload/common
```

请求方式：

```
POST
```

接口说明：

```
图片通用接口。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| pic_list | 是   | Array    | 文件字段 |

返回字段：

| 返回字段       | 必须 | 字段类型 | 字段说明         |
| -------------- | ---- | -------- | ---------------- |
| file_path      | 是   | String   | 图片路径         |
| size           | 是   | Integer  | 文件大小，单位kb |
| file_extension | 是   | String   |                  |

返回示例：

```json
{
    "data": [{
        "file_path": "http://www.baidu.com/img/1.png",
        "size": 250,
        "file_extension": "PNG",
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 11.重置密码接口

请求URL：

```
/api/v1/admin/reset/password
```

请求方式：

```
PUT
```

接口说明：

```
重置管理员密码
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| user_id  | 是   | String   | 用户id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 
}
```

##### 12.管理员信息修改接口

请求URL：

```
/api/v1/admin/info/alter
```

请求方式：

```
PUT
```

接口说明：

```
修改管理员账号信息
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                                              |
| -------- | ---- | -------- | ----------------------------------------------------- |
| user_id  | 是   | String   | 用户id                                                |
| account  | 是   | String   | 账号                                                  |
| nick     | 是   | String   | 昵称                                                  |
| mobile   | 是   | String   | 手机                                                  |
| role_id  | 是   | Array    | [{"id": , "name": }, ...] id为角色uid，nick为角色nick |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 
}
```

##### 13.角色编辑接口

请求URL：

```
/api/v1/admin/editor/role
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，编辑角色。请求头需要携带module_id和permission_id
```

请求参数:  

|    请求参数     | 必须 | 参数类型 | 参数说明 | 备注                                                |
| :-------------: | :--: | :------: | :------- | --------------------------------------------------- |
|       uid       |  是  |    是    | 昵称id   |                                                     |
|      nick       |  是  |    是    | 昵称     |                                                     |
|      desc       |  是  |  String  | 描述     |                                                     |
| permission_list |  是  |  Array   | 权限列表 | [{"module_id": "001", "permission_id": "001"}, ...] |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 

#### 八、内容管理模块

##### 1.图片素材列表接口

请求URL：

```
/api/v1/admin/material/pic/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图片素材列表数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                             |
| :------: | :--: | :------: | :------- | -------------------------------- |
|   num    |  是  | Integer  | 页数     |                                  |
|   page   |  是  | Integer  | 页码     |                                  |
| content  |  否  |  String  | 内容     |                                  |
| category |  是  |  String  | 类型     | 标题title, 昵称传nick, 标签label |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注         |
| :---------: | :--: | :------: | :--------- | ------------ |
|    count    |  是  | Integer  | 总数       | 外层结构     |
|    list     |  是  |  Array   | 数据列表   | 外层结构     |
|     uid     |  是  |  String  | 图片id     | 【属于list】 |
|    title    |  是  |  String  | 标题       | 【属于list】 |
|    label    |  是  |  String  | 标签       | 【属于list】 |
|    nick     |  是  |  String  | 上传者昵称 | 【属于list】 |
| big_pic_url |  是  |  String  | 图片路径   | 【属于list】 |
| create_time |  是  |  String  | 时间       | 【属于list】 |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"uid": "001",
      	"nick": "我是祖国的花朵",
      	"title": "我是哈哈哈哈哈哈哈",
      	"label": ["快乐", "神仙"],
      	"big_pic_url": "http://www.baidu.com/img/1.png",
      	"create_time": "2020-07-28"
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 2.图片素材删除接口

请求URL：

```
/api/v1/admin/material/pic/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 删除图片素材。请求头需要携带module_id和permission_id
```

请求参数: 

|  请求参数   | 必须 | 参数类型 | 参数说明   |
| :---------: | :--: | :------: | :--------- |
| pic_id_list |  是  |  Array   | 图片素材id |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 3.图片素材详情接口

请求URL：

```
/api/v1/admin/material/pic/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图片素材详情。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
|  pic_id  |  是  |  String  | 图片素材id |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明    |
| :---------: | :--: | :------: | :---------- |
|     uid     |  是  |  String  | 图片id      |
|    title    |  是  |  String  | 标题        |
|    label    |  是  |  String  | 标签        |
|    nick     |  是  |  String  | 上传者昵称  |
|   account   |  是  |  String  | 上传者账号  |
| big_pic_url |  是  |  String  | 图片路径    |
|    size     |  是  | Integer  | 大小        |
|   format    |  是  |  String  | 格式        |
| create_time |  是  |  String  | 时间        |
|  spec_list  |  是  |  Array   | 规格S、M、L |

返回示例：

```json
{
    "data": {
        "uid": "001",
        "nick": "我是祖国的花朵",
        "title": "我是哈哈哈哈哈哈哈",
        "account": "17725021251",
        "label": ["嘻哈", "哈哈"]
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "size": 150,
        "format": JPG,
        "create_time": "2020-07-28",
        "spec_list": [
            {
                "format": "S",
                "pic_url": "http://www.baidu.com/img/1.jpg"
            },
            ...
        ]
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 4.图片素材编辑接口

请求URL：

```
/api/v1/admin/material/pic/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 编辑图片素材详情。请求头需要携带module_id和permission_id
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注             |
| :------: | :--: | :------: | :------- | ---------------- |
|  title   |  是  |  String  | 标题     | 标题最长32个字符 |
|  label   |  是  |  Array   | 标签     | 标签最多20个     |
|  pic_id  |  是  |  String  | 图片id   |                  |

返回字段：无

返回示例：

```json
{
    "data": null,
    "code": 0,
    "msg": "Request successful."
}
```

##### 5.音频素材列表接口

请求URL：

```
/api/v1/admin/material/audio/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回音频素材列表数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                             |
| :------: | :--: | :------: | :------- | -------------------------------- |
|   num    |  是  | Integer  | 页数     |                                  |
|   page   |  是  | Integer  | 页码     |                                  |
| content  |  否  |  String  | 内容     |                                  |
| category |  是  |  String  | 类型     | 标题title, 昵称传nick, 标签label |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注         |
| :----------: | :--: | :------: | :--------- | ------------ |
|    count     |  是  | Integer  | 总数       | 外层结构     |
|     list     |  是  |  Array   | 数据列表   | 外层结构     |
|     uid      |  是  |  String  | 图片id     | 【属于list】 |
|    title     |  是  |  String  | 标题       | 【属于list】 |
|    label     |  是  |  String  | 标签       | 【属于list】 |
|     nick     |  是  |  String  | 上传者昵称 | 【属于list】 |
|  cover_url   |  是  |  String  | 封面路径   | 【属于list】 |
| head_img_url |  是  |  String  | 头像路径   | 【属于list】 |
|  audio_url   |  是  |  String  | 音频路径   | 【属于list】 |
| create_time  |  是  |  String  | 时间       | 【属于list】 |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"uid": "001",
      	"nick": "我是祖国的花朵",
      	"title": "我是哈哈哈哈哈哈哈",
      	"label": ["快乐", "神仙"],
        "head_img_url": "http://www.baidu.com/img/1.png",
      	"audio_url": "http://www.baidu.com/img/1.png",
        "cover_url": "http://www.baidu.com/img/1.png",
      	"create_time": "2020-07-28"
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 6.音频素材删除接口

请求URL：

```
/api/v1/admin/material/audio/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 删除音频素材。请求头需要携带module_id和permission_id
```

请求参数: 

|   请求参数    | 必须 | 参数类型 | 参数说明   |
| :-----------: | :--: | :------: | :--------- |
| audio_id_list |  是  |  Array   | 音频素材id |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 7.音频素材详情接口

请求URL：

```
/api/v1/admin/material/audio/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回音频素材详情。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| audio_id |  是  |  String  | 音频素材id |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   |
| :---------: | :--: | :------: | :--------- |
|     uid     |  是  |  String  | 图片id     |
|    title    |  是  |  String  | 标题       |
|    label    |  是  |  String  | 标签       |
|    nick     |  是  |  String  | 上传者昵称 |
|   account   |  是  |  String  | 上传者账号 |
|  cover_url  |  是  |  String  | 封面路径   |
|  audio_url  |  是  |  String  | 音频路径   |
|    size     |  是  | Integer  | 大小       |
|   format    |  是  |  String  | 格式       |
| create_time |  是  |  String  | 时间       |

返回示例：

```json
{
    "data": {
        "uid": "001",
        "nick": "我是祖国的花朵",
        "title": "我是哈哈哈哈哈哈哈",
        "account": "17725021251",
        "label": ["哈哈", "嘻哈"],
        "cover_url": "http://www.baidu.com/img/1.png",
        "audio_url": "http://www.baidu.com/img/1.png",
        "size": 150,
        "format": mp3,
        "create_time": "2020-07-28",
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 8.音频素材编辑接口

请求URL：

```
/api/v1/admin/material/audio/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 编辑素材详情。请求头需要携带module_id和permission_id
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注             |
| :------: | :--: | :------: | :------- | ---------------- |
|  title   |  是  |  String  | 标题     | 标题最长32个字符 |
|  label   |  是  |  Array   | 标签     | 标签最多20个     |
| audio_id |  是  |  String  | 音频id   |                  |

返回字段：无

返回示例：

```json
{
    "data": null,
    "code": 0,
    "msg": "Request successful."
}
```

##### 9.音频素材封面更换接口

请求URL：

```
/api/v1/admin/material/audio/cover
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 更换音频封面。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                 |
| :------: | :--: | :------: | :------- | -------------------- |
| pic_list |  是  |  Array   | 文件字段 | 上传文件时对应的字段 |
| audio_id |  是  |  String  | 音频id   |                      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "code": 0,
    "msg": "Request successful."
}
```

##### 10.图片、图集、图文、影集作品接口

请求URL：

```
/api/v1/admin/works/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图片、图集、图片、影集列表数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                                        |
| :------: | :--: | :------: | :------- | ------------------------------------------- |
|   num    |  是  | Integer  | 页数     |                                             |
|   page   |  是  | Integer  | 页码     |                                             |
| content  |  是  |  String  | 内容     |                                             |
| category |  是  |  String  | 分类     | 标题title, 昵称传nick, 标签label            |
|  state   |  是  | Integer  | 状态     | 0未审核，1审核中，2已上架, 3违规下架，4全部 |
|   type   |  是  |  String  | 类型     | 图片传tp， 图集传tj, 图文tw，影集传yj       |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                                     |
| :---------: | :--: | :------: | :--------- | -------------------------------------------------------- |
|    count    |  是  | Integer  | 总数       | 外层结构                                                 |
|    list     |  是  |  Array   | 数据列表   | 外层结构                                                 |
|     uid     |  是  |  String  | 图片id     | 【属于list】                                             |
|    title    |  是  |  String  | 标题       | 【属于list】                                             |
|    label    |  是  |  String  | 标签       | 【属于list】                                             |
|    nick     |  是  |  String  | 上传者昵称 | 【属于list】                                             |
|  cover_url  |  否  |  String  | 封面路径   | 【属于list】                                             |
|  pic_item   |  是  |  Array   | 图片信息   | 【属于list】                                             |
|   number    |  是  |  String  | 文件编号   | 【属于list】                                             |
|    state    |  是  | Integer  | 状态       | 0未审核（默认），1审核中，2已上架, 3违规下架【属于list】 |
| create_time |  是  |  String  | 时间       | 【属于list】                                             |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
                "uid": "001",
                "nick": "我是祖国的花朵",
                "title": "我是哈哈哈哈哈哈哈",
                "label": ["快乐", "神仙"],
                "cover_url": "http://www.baidu.com/img/1.png",
                "create_time": "2020-07-28",
            	"number": "bf124562",
            	"state": 1,
                "pic_item": [
                    { "thumb_url": "http://www.baidu.com/img/1.png" },
                    ...
                ]
            },
            ...
        ],
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 11.图片、图集作品状态更改接口

请求URL：

```
/api/v1/admin/works/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 更改图片、图集状态。请求头需要携带module_id和permission_id
```

请求参数: 

| 请求参数 | 必须 | 参数类型 | 参数说明                   |
| :------: | :--: | :------: | :------------------------- |
|  pic_id  |  是  |  Array   | 图片、图集作品id           |
|  state   |  是  | Integer  | 删除传-1, 下架传3, 恢复传2 |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 12.图片作品编辑接口

请求URL：

```
/api/v1/admin/works/pic/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 编辑图片作品。请求头需要携带module_id和permission_id
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   | 备注                            |
| :------: | :--: | :------: | :--------- | ------------------------------- |
|  title   |  是  |  String  | 标题       | 标题最长32个字符                |
|  label   |  是  |  Array   | 标签       | 标签最多20个                    |
|  state   |  是  | Integer  | 状态       | 0未审核 1审核中 2上架 3违规下架 |
|   tag    |  是  |  String  | 标记       | 商/编                           |
| works_id |  是  |  String  | 图片作品id |                                 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "code": 0,
    "msg": "Request successful."
}
```

##### 13.待审核作品列表接口

请求URL：

```
/api/v1/admin/works/audit/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回待审核作品列表数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                          |
| :------: | :--: | :------: | :------- | ----------------------------- |
|   num    |  是  | Integer  | 页数     |                               |
|   page   |  是  | Integer  | 页码     |                               |
| content  |  否  |  String  | 内容     |                               |
| category |  是  |  String  | 分类     | 标题title, 账号account        |
|   type   |  是  |  String  | 类型     | 图片传tp， 图集传tj, 图文传tw |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注         |
| :---------: | :--: | :------: | :------- | ------------ |
|    count    |  是  | Integer  | 总数     | 外层结构     |
|    list     |  是  |  Array   | 数据列表 | 外层结构     |
|     uid     |  是  |  String  | 图片id   | 【属于list】 |
|    title    |  是  |  String  | 标题     | 【属于list】 |
|    label    |  是  |  String  | 标签     | 【属于list】 |
|    nick     |  是  |  String  | 昵称     | 【属于list】 |
|   account   |  是  |  String  | 账号     | 【属于list】 |
|  cover_url  |  否  |  String  | 封面路径 | 【属于list】 |
|  pic_item   |  是  |  Array   | 图片信息 | 【属于list】 |
|   format    |  是  |  String  | 文件类型 | 【属于list】 |
| create_time |  是  |  String  | 时间     | 【属于list】 |

返回示例：

```json
{
    "data": {
        "count": 250,
        "list": [{
                "uid": "001",
                "nick": "我是祖国的花朵",
                "title": "我是哈哈哈哈哈哈哈",
                "label": ["快乐", "神仙"],
                "cover_url": "http://www.baidu.com/img/1.png",
                "create_time": "2020-07-28",
            	"format": bf124562,
            	"account": "17725021251",
                "pic_item": [
                    { "thumb_url": "http://www.baidu.com/img/1.png" },
                    ...
                ]
            },
            ...
        ],
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 14.作品审核

请求URL：

```
/api/v1/admin/works/audit
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 更改作品状态。请求头需要携带module_id和permission_id
```

请求参数: 

| 请求参数 | 必须 | 参数类型 | 参数说明    |
| :------: | :--: | :------: | :---------- |
| works_id |  是  |  Array   | 作品id      |
|  state   |  是  | Integer  | 通过2 驳回0 |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 15.图片作品详情

请求URL：

```
/api/v1/admin/works/pic/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图片作品详情。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
|  pic_id  |  是  |  String  | 图片素材id |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明                                                 |
| :---------: | :--: | :------: | :------------------------------------------------------- |
|     uid     |  是  |  String  | 图片id                                                   |
|    title    |  是  |  String  | 标题                                                     |
|    label    |  是  |  String  | 标签                                                     |
|    nick     |  是  |  String  | 昵称                                                     |
|   account   |  是  |  String  | 账号                                                     |
|    size     |  是  | Integer  | 大小                                                     |
|   format    |  是  |  String  | 文件类型                                                 |
|     tag     |  是  |  String  | 商                                                       |
|   pic_url   |  是  |  String  | 图片链接                                                 |
| price_item  |  是  |  Array   | 价格信息                                                 |
|    state    |  是  | Integer  | 状态 0未审核（默认），1审核中，2已上架/已公开，3违规下架 |
| create_time |  是  |  String  | 时间                                                     |
|  portrait   |  是  |  Object  | 肖像权，不为空代表有                                     |
|   product   |  是  |  Object  | 物产权，不为空代表有                                     |

返回示例：

```json
{
    "data": {
        "uid": "001",
        "nick": "我是祖国的花朵",
        "title": "我是哈哈哈哈哈哈哈",
        "account": "17725021251",
        "label": ["嘻哈", "哈哈"]
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "size": 150,
        "format": "nm123456",
        "tag": "商",
        "state": 1,
        "create_time": "2020-07-28",
        "price_item": [
        	"format": "S",
        	"price": 550.0,
        	"pic_url": "http://www.baidu.com/img/1.png"
        ],
        "portrait": {
                "uid": "001", // id
                "pic_url": "https://www.baidu.com/images/1.png", // 参考图
                "shoot_time": 1595743329000, // 拍摄时间
                "shoot_addr": "重庆市", // 拍摄地址
                "authorizer": [{ // 授权人信息
                        "name": "李四", // 授权人姓名
                        "id_card": "5020xxxxxxxxx", // 授权人身份证
                        "sex": "男", // 授权人性别
                        "mobile": "17725021251", // 授权人手机
                        "home_addr": "重庆市xxxxx", // 授权人地址
                        "is_adult": true // 是否成年,
        				"g_name": "哈哈",
        				"g_id_card": "500228111xxxxx",
        				"g_mobile": "1772502xxxx"
                    },
                    ....
                ],
                "b_name": "王五", // 乙方姓名
                "b_id_card": "5002281994xxxxxxxxx", // 乙方身份证
                "b_mobile": "17725021251", // 乙方手机
                "b_home_addr": "重庆市xxxxx", // 乙方地址
                "create_time": 1595743329000, // 创建时间
                "update_time": 1595743329000 // 更新时间
    	},
    	"product"：{
            "uid": "001", // id
            "a_name": "张三", // 甲方姓名
            "a_id_card": "5002281994xxxxxxxxx", // 甲方身份证
            "a_mobile": "17725021250", // 甲方手机
            "a_email": "825076979@qq.com", // 甲方邮箱
            "a_home_addr": "重庆市梁平县xxxxxx", // 甲方地址
            "pic_url": "https://www.baidu.com/images/1.png", // 参考图
            "shoot_time": 1595743329000, // 拍摄时间
            "shoot_addr": "重庆市", // 拍摄地址
            "a_property_addr": "重庆市xxx", // 甲方财产地址
            "a_property_desc": "很好很好", // 甲方财产描述
            "b_name": "王五", // 乙方姓名
            "b_email": "825076979@qq.com", // 乙方邮箱
            "b_id_card": "5002281994xxxxxxxxx", // 乙方身份证
            "b_mobile": "17725021251", // 乙方手机
            "b_home_addr": "重庆市xxxxx", // 乙方地址
            "create_time": 1595743329000, // 创建时间
            "update_time": 1595743329000 // 更新时间
        },
    "code": 0,
    "msg": "Request successful."
}
```

##### 16.图集详情接口

请求URL：

```
/api/v1/admin/works/atlas/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图集作品详情。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| works_id |  是  |  String  | 图集作品id |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 |
| :---------: | :--: | :------: | :------- |
|     uid     |  是  |  String  | 图片id   |
|    title    |  是  |  String  | 标题     |
|   user_id   |  是  |  String  | 用户id   |
|    label    |  是  |  String  | 标签     |
|    nick     |  是  |  String  | 昵称     |
|   account   |  是  |  String  | 账号     |
|  cover_url  |  是  |  String  | 封面路径 |
|    state    |  是  | Integer  | 状态     |
|  pic_item   |  是  |  String  | 商       |
| create_time |  是  |  String  | 时间     |

返回示例：

```json
{
    "data": {
        "uid": "001",
        "nick": "我是祖国的花朵",
        "title": "我是哈哈哈哈哈哈哈",
        "label": ["快乐", "神仙"],
        "user_id": "001",
        "cover_url": "http://www.baidu.com/img/1.png",
        "create_time": "2020-07-28",
        "state": 1,
        "pic_item": [{
                "thumb_url": "http://www.baidu.com/img/1.png",
                "title": "哈哈哈",
                "uid": "001", // 素材id
                "works_state": 2 // 0未审核，1审核中，2已上架
            },
            ...
        ]
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 17.图文详情接口

请求URL：

```
/api/v1/admin/works/article/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回图文作品详情。
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| works_id |  是  |  String  | 图集作品id |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |
| :----------: | :--: | :------: | :------- |
|     uid      |  是  |  String  | 图片id   |
|    title     |  是  |  String  | 标题     |
|   content    |  是  |  String  | 内容     |
|     nick     |  是  |  String  | 昵称     |
| head_img_url |  是  |  String  | 头像路径 |
|  browse_num  |  是  | Integer  | 浏览数   |
| comment_num  |  是  | Integer  | 评论数   |
|   like_num   |  是  | Integer  | 点赞数   |
|  share_num   |  是  | Integer  | 分享数   |
| create_time  |  是  |  String  | 时间     |

返回示例：

```json
{
    "data": {
        "uid": "001",
        "nick": "我是祖国的花朵",
        "content": "哈哈哈哈哈哈哈......................."
        "title": "我是哈哈哈哈哈哈哈",
        "head_img_url": "http://www.baidu.com/img/1.png",
        "create_time": "2020-07-28",
		"browse_num": 250,
        "comment_num": 250,
        "like_num": 250,
        "share_num": 250
    },
    "code": 0,
    "msg": "Request successful."
}
```

##### 18.图集详情素材库列表接口

请求URL：

```
/api/v1/admin/atlas/material/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回素材库数据。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| user_id  |  是  |  String  | 用户id   |      |
|   num    |  是  | Integer  | 页数     |      |
|   page   |  是  | Integer  | 页码     |      |
| content  |  否  |  String  | 内容     |      |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注         |
| :---------: | :--: | :------: | :--------- | ------------ |
|    count    |  是  | Integer  | 总数       | 外层结构     |
|    list     |  是  |  Array   | 数据列表   | 外层结构     |
|     uid     |  是  |  String  | 图片id     | 【属于list】 |
|    title    |  是  |  String  | 标题       | 【属于list】 |
|    label    |  是  |  String  | 标签       | 【属于list】 |
|   account   |  是  |  String  | 账号       | 【属于list】 |
|  thumb_url  |  是  |  String  | 缩略图路径 | 【属于list】 |
| create_time |  是  |  String  | 时间       | 【属于list】 |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"uid": "001",
      	"account": "17725021251",
      	"title": "我是哈哈哈哈哈哈哈",
      	"label": ["快乐", "神仙"],
      	"thumb_url": "http://www.baidu.com/img/1.png",
      	"create_time": "2020-07-28"
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 19.图集详情添加图片作品

请求URL：

```
/api/v1/admin/atlas/pic/add
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 图集作品添加图片。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| works_id |  是  |  String  | 图集作品id |
|  pic_id  |  是  |  Array   | 图片id     |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 20.图集详情编辑接口

请求URL：

```
/api/v1/admin/works/atlas/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 编辑图集详情。请求头需要携带module_id和permission_id
```

请求参数:

| 请求参数 | 必须 | 参数类型 | 参数说明   | 备注                            |
| :------: | :--: | :------: | :--------- | ------------------------------- |
|  title   |  是  |  String  | 标题       | 标题最长32个字符                |
|  label   |  是  |  Array   | 标签       | 标签最多20个                    |
|  state   |  是  | Integer  | 状态       | 0未审核 1审核中 2上架 3违规下架 |
| works_id |  是  |  String  | 图集作品id |                                 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "code": 0,
    "msg": "Request successful."
}
```

##### 21.图集详情页图片删除接口

请求URL：

```
/api/v1/admin/atlas/pic/delete
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 图集作品删除图片。请求头需要携带module_id和permission_id
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| works_id |  是  |  String  | 图集作品id |
|  pic_id  |  是  |  String  | 图片id     |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 

#### 九、财务管理模块

##### 1.订单列表接口

请求URL：

```
/api/v1/admin/finance/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回订单列表数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                     |
| :--------: | :--: | :------: | :------- | ------------------------ |
|    num     |  是  | Integer  | 页数     |                          |
|    page    |  是  | Integer  | 页码     |                          |
|  content   |  否  |  String  | 内容     |                          |
|  category  |  是  |  String  | 类型     | order订单号，account账号 |
|   state    |  是  | Integer  | 状态     | 1未付款，2已完成，3全部  |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天     |
|  end_time  |  是  |  String  | 结束时间 |                          |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注                                  |
| :---------: | :--: | :------: | :------- | ------------------------------------- |
|    count    |  是  | Integer  | 总数     | 外层结构                              |
|    list     |  是  |  Array   | 数据列表 | 外层结构                              |
|    order    |  是  |  String  | 订单号   | 【属于list】                          |
|   amount    |  是  |  Float   | 金额     | 【属于list】                          |
|   account   |  是  |  String  | 账号     | 【属于list】                          |
|   user_id   |  是  |  String  | 用户id   | 【属于list】                          |
|    state    |  是  | Integer  | 状态     | 【属于list】1未付款，2已付款，3已退款 |
| create_time |  是  |  String  | 时间     | 【属于list】                          |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"order": "0000000001",
      	"amount": 250.0,
      	"account": "17725021251",
      	"user_id": "0001",
      	"state": 2,
      	"create_time": "2020-07-28"
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 2.订单退款接口

请求URL：

```
/api/v1/admin/finance/refund
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数, 订单退款。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| user_id  |  是  |  String  | 用户id   |      |
|  amount  |  是  | Integer  | 金额     |      |
|  order   |  是  |  String  | 订单号   |      |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 3.订单详情接口

请求URL：

```
/api/v1/admin/finance/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 订单详情。
```

请求参数:  

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| user_id  |  是  |  String  | 买家id   |      |
|  order   |  是  |  String  | 订单号   |      |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                        |
| :---------: | :--: | :------: | :--------- | ------------------------------------------- |
| works_list  |  是  |  Array   | 作品列表   | 外层结构                                    |
|  user_info  |  是  |  Object  | 买家信息   | 外层结构                                    |
| order_info  |  是  |  Object  | 订单信息   | 外层结构                                    |
|    order    |  是  |  String  | 订单号     | 【属于order_info】                          |
|   amount    |  是  |  Float   | 商品总额   | 【属于order_info】                          |
|    count    |  是  | Integer  | 商品数     | 【属于order_info】                          |
|    state    |  是  | Integer  | 状态       | 【属于order_info】1未付款，2已付款，3已退款 |
| create_time |  是  |  String  | 创建时间戳 | 【属于order_info】                          |
| update_time |  是  |  String  | 完成时间戳 | 【属于order_info】                          |
|    nick     |  是  |  String  | 昵称       | 【属于user_info】                           |
|   account   |  是  |  String  | 账户       | 【属于user_info】                           |
|   mobile    |  是  |  String  | 手机       | 【属于user_info】                           |
|    title    |  是  |  String  | 标题       | 【属于works_list】                          |
|    spec     |  是  |  String  | 规格       | 【属于works_list】                          |
|  thumb_url  |  是  |  String  | 缩略图路径 | 【属于works_list】                          |
|    price    |  是  |  Float   | 价格       | 【属于works_list】                          |
|  currency   |  是  |  String  | 币种       | 【属于works_list】                          |

返回示例：

```json
{
  "data": {
      "user_info": {
          "nick": "大傻子",
          "account": "17725021251",
          "mobile": "17725021251"
      },
      "order_info": {
    	"order": "0000000001",
      	"amount": 250.0,
      	"count": 250,
      	"state": 2,
      	"create_time": "2020-07-28",
        "update_time": "2020-07-28"
  		},
      "works_list": [{
        	"title": "哈哈哈哈",
          	"spec": "M",
          	"thumb_url": "http://www.baidu.com/img/1.png",
          	"price": 50.0,
          	"currency": "￥"
      	},
        ...
      ]
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 4.提现记录列表接口

请求URL：

```
/api/v1/admin/finance/withdrawal
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 提现记录数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                     |
| :--------: | :--: | :------: | :------- | ------------------------ |
|    num     |  是  | Integer  | 页数     |                          |
|    page    |  是  | Integer  | 页码     |                          |
|  content   |  否  |  String  | 内容     |                          |
|  category  |  是  |  String  | 类型     | order订单号，account账号 |
|   state    |  是  | Integer  | 状态     | 1驳回，2已完成           |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天     |
|  end_time  |  是  |  String  | 结束时间 |                          |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注                       |
| :---------: | :--: | :------: | :--------- | -------------------------- |
|    count    |  是  | Integer  | 总数       | 外层结构                   |
|    list     |  是  |  Array   | 数据列表   | 外层结构                   |
|    order    |  是  |  String  | 订单号     | 【属于list】               |
|   amount    |  是  |  Float   | 金额       | 【属于list】               |
|   account   |  是  |  String  | 账号       | 【属于list】               |
|    state    |  是  | Integer  | 状态       | 【属于list】1未处理，2完成 |
| create_time |  是  |  String  | 申请时间   | 【属于list】               |
| trade_name  |  是  |  String  | 提现账户名 | 【属于list】               |
|  trade_id   |  是  |  String  | 提现账号   | 【属于list】               |
| update_time |  是  |  String  | 处理时间   | 【属于list】               |
|   channel   |  是  |  String  | 提现渠道   | 【属于list】               |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"order": "0000000001",
      	"amount": 250.0,
      	"account": "17725021251",
      	"state": 2,
        "trade_name": "支付宝",
        "trade_id": "172502xxxx",
        "channel": "支付宝",
      	"create_time": "2020-07-28"，
        "update_time": "2020-07-28"
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 5.充值记录接口

请求URL：

```
/api/v1/admin/finance/recharge
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回充值记录数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                                      |
| :--------: | :--: | :------: | :------- | ----------------------------------------- |
|    num     |  是  | Integer  | 页数     |                                           |
|    page    |  是  | Integer  | 页码     |                                           |
|  content   |  否  |  String  | 内容     |                                           |
|  channel   |  是  |  String  | 渠道     | 支付宝/微信/default                       |
|  category  |  是  |  String  | 类型     | order订单号，account充值账号，trade交易号 |
|   state    |  是  | Integer  | 状态     | 0未支付，1已支付完成, 2全部               |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天                      |
|  end_time  |  是  |  String  | 结束时间 |                                           |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 | 备注                         |
| :---------: | :--: | :------: | :------- | ---------------------------- |
|    count    |  是  | Integer  | 总数     | 外层结构                     |
|    list     |  是  |  Array   | 数据列表 | 外层结构                     |
|    order    |  是  |  String  | 订单号   | 【属于list】                 |
|   amount    |  是  |  Float   | 金额     | 【属于list】                 |
|   account   |  是  |  String  | 账号     | 【属于list】                 |
|    state    |  是  | Integer  | 状态     | 【属于list】0未支付，1已支付 |
| create_time |  是  |  String  | 申请时间 | 【属于list】                 |
|  trade_id   |  是  |  String  | 提现账号 | 【属于list】                 |
|   channel   |  是  |  String  | 提现渠道 | 【属于list】                 |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"order": "0000000001",
      	"amount": 250.0,
      	"account": "17725021251",
      	"state": 2,
        "trade_id": "172502xxxx",
        "channel": "支付宝",
      	"create_time": "2020-07-28"，
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 6.充值渠道接口

请求URL：

```
/api/v1/admin/finance/recharge/channel
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回充值渠道数据。
```

请求参数:  无

返回字段：无

返回示例：

```json
{
  "data": [
      "微信",
      "支付宝",
      ...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 7.提现审核列表

请求URL：

```
/api/v1/admin/finance/withdrawal/audit
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 返回待审核提现数据。
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                                |
| :--------: | :--: | :------: | :------- | ----------------------------------- |
|    num     |  是  | Integer  | 页数     |                                     |
|    page    |  是  | Integer  | 页码     |                                     |
|  content   |  否  |  String  | 内容     |                                     |
|  channel   |  是  |  String  | 渠道     | 全部传default, 其余对应传，如支付宝 |
|  category  |  是  |  String  | 类型     | order订单号，account申请账号        |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天                |
|  end_time  |  是  |  String  | 结束时间 |                                     |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   | 备注         |
| :---------: | :--: | :------: | :--------- | ------------ |
|    count    |  是  | Integer  | 总数       | 外层结构     |
|    list     |  是  |  Array   | 数据列表   | 外层结构     |
|    order    |  是  |  String  | 订单号     | 【属于list】 |
|   amount    |  是  |  Float   | 金额       | 【属于list】 |
|   account   |  是  |  String  | 账号       | 【属于list】 |
| create_time |  是  |  String  | 申请时间   | 【属于list】 |
| trade_name  |  是  |  String  | 提现账号名 | 【属于list】 |
|  trade_id   |  是  |  String  | 提现账号   | 【属于list】 |
|   channel   |  是  |  String  | 提现渠道   | 【属于list】 |

返回示例：

```json
{
  "data": {
      "count": 250,
      "list": [{
    	"order": "0000000001",
      	"amount": 250.0,
      	"account": "17725021251",
      	"trade_name": "哈哈哈哈哈哈",
        "trade_id": "172502xxxx",
        "channel": "支付宝",
      	"create_time": "2020-07-28"，
  		},
    	...
  	],
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 8.提现审核接口

请求URL：

```
/api/v1/admin/finance/withdrawal/state
```

请求方式：

```
PUT
```

接口说明：

```
审核账号。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注             |
| :--------: | :--: | :------: | :------- | ---------------- |
| order_list |  是  |  Array   | 订单号   |                  |
|   state    |  是  | Integer  | 状态     | 通过传2, 驳回传0 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.提现记录导出接口

请求URL：

```
/api/v1/admin/finance/withdrawal/export
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 导出提现记录数据。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                     |
| :--------: | :--: | :------: | :------- | ------------------------ |
|  content   |  否  |  String  | 内容     |                          |
|  category  |  是  |  String  | 类型     | order订单号，account账号 |
|   state    |  是  | Integer  | 状态     | 1驳回，2已完成           |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天     |
|  end_time  |  是  |  String  | 结束时间 |                          |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 10.充值记录导出

请求URL：

```
/api/v1/admin/finance/recharge/export
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 导出充值记录数据。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                                      |
| :--------: | :--: | :------: | :------- | ----------------------------------------- |
|  content   |  否  |  String  | 内容     |                                           |
|  channel   |  是  |  String  | 渠道     | 支付宝/微信/default                       |
|  category  |  是  |  String  | 类型     | order订单号，account充值账号，trade交易号 |
|   state    |  是  | Integer  | 状态     | 0未支付，1已支付完成, 2全部               |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天                      |
|  end_time  |  是  |  String  | 结束时间 |                                           |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

##### 11.体现审核记录接口

请求URL：

```
/api/v1/admin/finance/audit/export
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数, 导出待审核提现数据。请求头需要携带module_id和permission_id
```

请求参数:  

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                                |
| :--------: | :--: | :------: | :------- | ----------------------------------- |
|  content   |  否  |  String  | 内容     |                                     |
|  channel   |  是  |  String  | 渠道     | 全部传default, 其余对应传，如支付宝 |
|  category  |  是  |  String  | 类型     | order订单号，account申请账号        |
| start_time |  是  |  String  | 开始时间 | 查询区间不能超过30天                |
|  end_time  |  是  |  String  | 结束时间 |                                     |

返回字段：无

返回示例：

```json
{
  "data": null,
  "code": 0,
  "msg": "Request successful."
}
```

