#### 微图API接口文档

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
3.用户校验
将token存入请求头中上传	// 后端直接从headers中获取token
将游客uid存入请求头中上传 // 字段名为user_id
4.服务器返回token
将token存入响应头中返回
```

#### 一、列表页

##### 1.轮播图接口

请求URL：

```
/api/v1/banner
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取轮播图相关数据。
```

请求参数: 无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
|  order   |  是  | Integer  | 序号     |
| pic_url  |  是  |  String  | 图片路径 |
|   link   |  是  |  String  | 链接     |

返回示例：

```json
{
    "data": [{
        "order": 1,
        "pic_url": "www.baidu.com/img/1.png",
        "link": "www.baidu.com"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```



##### 2.发现列表页接口

请求URL：

```
/api/v1/total
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取综合列表页选相关数据。
```

请求参数:

|  请求参数  | 必须 | 参数类型 | 参数说明                                        |
| :--------: | :--: | :------: | :---------------------------------------------- |
|    page    |  是  |   Int    | 页码， 从1开始                                  |
|    num     |  是  |   Int    | 每页个数                                        |
|  sort_way  |  是  | Integer  | 排序方式。倒序传-1，正序传1                     |
| sort_field |  是  |  String  | 排序字段。推荐排序默认传defualt，time按时间排序 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   pic_item   |  否  |  Array   | 素材       |                                          |
|  video_url   |  否  |  String  | 视频路径   |                                          |
|  audio_url   |  否  |  String  | 音频路径   |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|  works_num   |  是  | Integer  | 作品数量   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中                       |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                  |

返回示例：

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "pic_item": [{
            	"uid": "7893432",	// 图片唯一id
                "works_id": "123456", // 作品id
                "big_pic_url": "www.baidu.com/img/1.png",	// 大图
                "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                ...
            	},
            	...
            ],
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,
        	"head_img_url": "www.baidu.com/img/1.png",
        	"video_url": "www.baidu.com/video/1.mp4",
        	"audio_url": "www.baidu.com/audio/1.mp3",
        	"works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": Null,
            "content": Null,
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
        	"type": "tj",
            "is_like": true,
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.图集列表页接口

请求URL：

```
/api/v1/pic
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取图集列表页选相关数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                    |
| :------: | :--: | :------: | :-------------------------- |
|   page   |  是  |   Int    | 页码，从1开始               |
|   num    |  是  |   Int    | 每页个数                    |
| sort_way |  否  | Integer  | 排序方式。倒序传-1，正序传1 |
|  label   |  否  |  String  | 标签。推荐排序默认传default |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   pic_item   |  否  |  Array   | 素材       |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|  works_num   |  是  | Integer  | 作品数量   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                  |

返回示例：

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "pic_item": [{
            	"uid": "7893432",	// 图片唯一id
                "works_id": "123456", // 作品id
                "big_pic_url": "www.baidu.com/img/1.png",	// 大图
                "thumbn_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                ...
            	},
            	...
            ],
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,
        	"head_img_url": "www.baidu.com/img/1.png",
        	"works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
        	"type": "tj",
            "is_like": true,
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.标签、热搜词接口

请求URL：

```
/api/v1/label_kw
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取相关标签、热搜词数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明              |
| :------: | :--: | :------: | :-------------------- |
|   type   |  是  |  String  | pic图集， video影集。 |

返回字段： 

| 返回字段 | 必须 | 字段类型 | 字段说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
|  hot_kw  |  是  |  Array   | 热搜词   |      |
|  label   |  是  |  Array   | 标签     |      |

返回示例

```json
{
	"data": {
        "hot_kw": [
           "美好",
           "人生",
            ...
        ],
        "label":[
           "加油",
           "和谐",
    		...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```



##### 5.图集详情页接口

请求URL：

```
/api/v1/atlas/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取综合列表页选相关数据。
```

请求参数

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   uid    |  是  |  String  | 图片uid  |
| works_id |  是  |  String  | 作品id   |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明     | 备注                                     |
| :----------: | :--: | :------: | :----------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id   |                                          |
|   pic_item   |  否  |  Array   | 素材         |                                          |
|    number    |  是  |  String  | 文件编号     |                                          |
|    format    |  是  |  String  | 文件格式     |                                          |
|   user_id    |  是  |  String  | 用户id       |                                          |
|     nick     |  是  |  String  | 昵称         |                                          |
| head_img_url |  是  |  String  | 头像         |                                          |
|  works_num   |  是  | Integer  | 作品量       |                                          |
|   price_id   |  是  |  String  | 定价id       |                                          |
|    title     |  是  |  String  | 标题         |                                          |
|     desc     |  是  |  String  | 描述         |                                          |
|    label     |  否  |  Array   | 标签         | 图文无标签                               |
|    state     |  是  | Integer  | 状态         | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐     | true推荐  false取消推荐                  |
| is_portrait  |  是  | Boolean  | 是否有肖像权 | true有，false无                          |
| is_products  |  是  | Boolean  | 是否有物产权 | true有，false无                          |
|     type     |  是  |  String  | 分类         | tj图集  yj影集  tw图文 lj链接 pc图片     |
|   pic_num    |  否  | Integer  | 图片量       | 图文无图片量  图片为1                    |
|   like_num   |  是  | Integer  | 点赞量       |                                          |
| comment_num  |  是  | Integer  | 评论量       |                                          |
|  share_num   |  是  | Integer  | 分享量       |                                          |
|  browse_num  |  是  | Integer  | 浏览量       |                                          |
| create_time  |  是  | Integer  | 创建时间     | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间     | 毫秒时间戳                               |
|  is_follow   |  是  | Boolean  | 是否关注     | true已关注，false未关注                  |
|   is_like    |  是  | Boolean  | 是否点赞     | true已关注，false未关注                  |

返回示例

```json
{
	"data": {
       "pic_data": {	// 图片信息
           "uid": "123456",	// 作品唯一id
           "pic_item": [{
              "uid": "7893432",	// 图片唯一id
              "works_id": "123456", // 作品id
              "big_pic_url": "www.baidu.com/img/1.png",	// 大图
           	  "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
               "title": "洱海"
              	...
          		},
            	...
            ],
            "number": "fm123456",
            "format": "PNG",
            "price_id": "2309530",
            "user_id": "123567",
			"nick": "喜好",
        	"head_img_url": "www.baidu.com/img/1.png",
        	"works_num": 250,
        	"title": "生活",
        	"desc": "一个人生活",
        	"content": Null,
            "label": ["美好", "幸福"],
            "state": 2,
            "tag": "商",
            "is_recommend": true,
            "is_portrait": true,
            "is_products": true,
            "is_follow": true,
           	"is_like": true,
            "type": "tj",
            "pic_num": 1,
            "like_num": 666,
            "comment_num": 666,
            "share_num": 666,
            "browse_num": 666,
            "create_time": 1593565215000,
            "update_time": 1593565215000,
    	},
    	"price_data": [{  // 价格规格信息
            "type": 0,	// 平台定价  0平台定价(默认)  1自行定价
            "format": "S",	// 格式  S、M、L、扩大授权
            "currency": "¥",	// 币种
            "price": "55.00",	// 价格
            "price_unit": "元",	// 价格单位
            "width": 500,	// 宽度
            "height": 800,	// 高度
            "size_unit": "px",	// 单位
            ...
        	},
            ...
        ],
    	"altas_data": [{	// 图集信息
            "uid": "234378",	// 素材唯一uid
            "works_id": "123456",	// 作品uid
            "works_status": 2,	// 作品状态  0未审核，1审核中，2已上架
            "thumb_url": "www.baidu.com/thumb/2.png", // 缩略图路径
            "label": ["美好", "幸福"]
            ...
         	},
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.影集列表页接口

请求URL：

```
/api/v1/video
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取影集列表页选相关数据。
```

请求参数

| 请求参数 | 必须 | 参数类型 | 参数说明                        |
| :------: | :--: | :------: | :------------------------------ |
|   page   |  是  |   Int    | 页码，从1开始                   |
|   num    |  是  |   Int    | 每页个数                        |
| sort_way |  否  | Integer  | 排序方式。倒序传-1，正序传1     |
|  label   |  否  |  String  | 排序字段。推荐排序默认传defualt |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   pic_item   |  否  |  Array   | 素材       |                                          |
|  video_url   |  否  |  String  | 视频路径   |                                          |
|  audio_url   |  否  |  String  | 音频路径   |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                  |

返回示例

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "pic_item": [{
            	"uid": "7893432",	// 图片唯一id
                "works_id": "123456", // 作品id
                "big_pic_url": "www.baidu.com/img/1.png",	// 大图
                "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                ...
            	},
            	...
            ],
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,
        	"video_url": "www.baidu.com/video/1.mp4",
        	"audio_url": "www.baidu.com/audio/1.mp3",
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": "www.baidu.com/img/1.png",
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
        	"type": "yj",
            "is_like": true,
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```



##### 7.影集置顶接口

请求URL：

```
/api/v1/video/top
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取影集置顶相关数据。
```

请求参数：无

返回字段：

|   返回字段    | 必须 | 字段类型 | 字段说明                | 备注 |
| :-----------: | :--: | :------: | :---------------------- | ---- |
|      uid      |  是  |  String  | 作品唯一id              |      |
| top_cover_url |  是  |  String  | 置顶影集封面路径        |      |
|   top_title   |  是  |  String  | 置顶影集标题            |      |
|   like_num    |  是  | Integer  | 点赞量                  |      |
|  browse_num   |  是  | Integer  | 浏览量                  |      |
|    is_like    |  是  | Boolean  | true已点赞，false未点赞 |      |

返回示例

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "top_title": "生活",
            "top_cover_url": "www.baidu.com/img/2.png",
        	"like_num": 666,
        	"browse_num": 666,
            "is_like": true
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.影集详情页接口

请求URL：

```
/api/v1/video/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取影集置顶相关数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明    |
| :------: | :--: | :------: | :---------- |
| works_id |  是  |  String  | 影集作品uid |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                                         |
| :----------: | :--: | :------: | :--------- | ------------------------------------------------------------ |
|     uid      |  是  |  String  | 作品唯一id | 此uid和me作品id同为一个                                      |
|   pic_item   |  否  |  Array   | 素材       | [{uid, works_id, works_state, big_pic_url,thumb_url}] works_id和works_state不是一定存在 |
|  video_url   |  是  |  String  | 视频路径   |                                                              |
|  audio_url   |  是  |  String  | 音频路径   |                                                              |
|    number    |  是  |  String  | 文件编号   |                                                              |
|    format    |  是  |  String  | 文件格式   |                                                              |
|   user_id    |  是  |  String  | 用户id     |                                                              |
|     nick     |  是  |  String  | 昵称       |                                                              |
| head_img_url |  是  |  String  | 头像       |                                                              |
|  works_num   |  是  | Integer  | 作品量     |                                                              |
|    title     |  是  |  String  | 标题       |                                                              |
|     desc     |  是  |  String  | 描述       |                                                              |
|    label     |  否  |  Array   | 标签       | 图文无标签                                                   |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架                     |
|  recommend   |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                                      |
|     type     |  是  |  String  | 分类       | tj图集  yj影集  tw图文 lj链接 pc图片                         |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1                                        |
|   like_num   |  是  | Integer  | 点赞量     |                                                              |
| comment_num  |  是  | Integer  | 评论量     |                                                              |
|  share_num   |  是  | Integer  | 分享量     |                                                              |
|  browse_num  |  是  | Integer  | 浏览量     |                                                              |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                                                   |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                                                   |
|  is_follow   |  是  | Boolean  | 是否关注   | true已关注，false未关注                                      |

返回示例：

```json
{
	"data": 
       {	// 图片信息
           "uid": "123456",	// 作品唯一id
           "pic_item": [{
           		"uid": "7893432",	// 图片唯一id
           		"works_id": "123456", // 作品id
           		"big_pic_url": "www.baidu.com/img/1.png",	// 大图
           		"thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径，
               	"works_state": 2 // 图片状态
           		...
          	  	},
            	...
            ],
            "number": "fm123456",
            "format": "PNG",
            "user_id": "123567",
			"nick": "喜好",
        	"head_img_url": "www.baidu.com/img/1.png",
        	"works_num": 250,
        	"title": "生活",
        	"desc": "一个人生活",
            "label": ["美好", "幸福"],
            "state": 2,
            "recommend": true,
            "is_follow": true,
            "type": "yj",
            "pic_num": 1,
            "like_num": 666,
            "comment_num": 666,
            "share_num": 666,
            "browse_num": 666,
            "create_time": 1593565215000,
            "update_time": 1593565215000,
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.图文列表页接口

请求URL：

```
/api/v1/article
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取图文列表页选相关数据。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明                                      |
| :--------: | :--: | :------: | :-------------------------------------------- |
|    page    |  是  |   Int    | 页码，从1开始                                 |
|    num     |  是  |   Int    | 每页个数                                      |
|  sort_way  |  否  | Integer  | 排序方式。倒序传-1，正序传1                   |
| sort_field |  否  |  String  | 排序字段。推荐排序默认defualt，time按时间排序 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                  |

返回示例：

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,	// 0代表未浏览，1代表已浏览
        	"head_img_url": "www.baidu.com/img/1.png",
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": "www.baidu.com/img/2.jpg",
            "content": "大家好, 我是祖国的花朵",
        	"state": 2,
        	"is_recommend": true,
        	"type": "tw",
            "is_like": true,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 10.图文热点文章接口

请求URL：

```
/api/v1/article/hot
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取图文热点文章相关数据。
```

请求参数： 无

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |

返回示例

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,	// 0代表未浏览，1代表已浏览
        	"head_img_url": "www.baidu.com/img/1.png",
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": "www.baidu.com/img/2.jpg",
            "content": "大家好, 我是祖国的花朵",
        	"state": 2,
        	"is_recommend": true,
        	"type": "tw",
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 11.图文详情页接口

请求URL：

```
/api/v1/article/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取图文详情页相关数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明    |
| :------: | :--: | :------: | :---------- |
|   uid    |  是  |  String  | 图文作品uid |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|  works_num   |  是  | Integer  | 作品数量   |                                          |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中                       |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|  is_follow   |  是  | Boolean  | 是否关注   | true已关注，false未关注                  |

返回示例

```json
{
	"data":
        {
            "uid": "123456",	// 作品唯一id
            "user_id": "123567",
			"nick": "喜好",
        	"head_img_url": "www.baidu.com/img/1.png",
        	"works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": "www.baidu.com/img/1.jpg",
            "content": "我是祖国的花朵",
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
            "is_follow": true,
        	"type": "tj",
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
    "msg": "Request successful.",
    "code": 0
}
```

##### 12.浏览记录接口

请求URL：

```
/api/v1/browse
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，记录相关浏览数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| works_id |  是  |  Array   | 图文作品id |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 13.热搜词接口

请求URL：

```
/api/v1/hot/keyword
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取前一天热搜词。
```

请求参数：无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回示例：

```json
{
    "data": [
        {
        	"keyword": "美丽"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 14.搜索关键词接口

请求URL：

```
/api/v1/search/keyword
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取联想关键词。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回示例：

```json
{
    "data": [
        {
        	"keyword": "美丽"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 15.搜索作品接口

请求URL：

```
/api/v1/search/works
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取相关作品数据。
```

请求参数：

|   请求参数   | 必须 | 参数类型 | 参数说明 | 备注                             |
| :----------: | :--: | :------: | :------- | -------------------------------- |
|     page     |  是  |   Int    | 页码     | 从1开始                          |
|     num      |  是  |   Int    | 每页个数 |                                  |
|   sort_way   |  是  | Integer  | 排序方式 | 倒序传-1，正序传1                |
| filter_field |  是  |  String  | 筛选字段 | default默认 tj图集 yj影集 tw图文 |
|   keyword    |  是  |  String  | 关键词   |                                  |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   pic_item   |  否  |  Array   | 素材       |                                          |
|  video_url   |  否  |  String  | 视频路径   |                                          |
|  audio_url   |  否  |  String  | 音频路径   |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|  works_num   |  是  | Integer  | 作品数量   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中                       |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |

返回示例：

```json
{
	"data": [
        {
            "uid": "123456",	// 作品唯一id
            "pic_item": [{
            	"uid": "7893432",	// 图片唯一id
                "works_id": "123456", // 作品id
                "big_pic_url": "www.baidu.com/img/1.png",	// 大图
                "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                ...
            	},
            	...
            ],
            "user_id": "123567",
			"nick": "喜好",
            "count": 1,
        	"head_img_url": "www.baidu.com/img/1.png",
        	"video_url": "www.baidu.com/video/1.mp4",
        	"audio_url": "www.baidu.com/audio/1.mp3",
        	"works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": Null,
            "content": Null,
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
        	"type": "tj",
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 16.作品点赞接口

请求URL：

```
/api/v1/works/like
```

请求方式：

```
POST
```

接口说明：

```
作品点赞，用户必须登录才能操作。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| works_id |  是  |  String  | 作品id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 17.评论列表页接口

请求URL：

```
/api/v1/comment/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取评论数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明      |
| :------: | :--: | :------: | :------------ |
|   page   |  是  | Integer  | 页码，从1开始 |
|   num    |  是  | Integer  | 每页个数      |
| works_id |  是  |  String  | 作品id        |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |
| :----------: | :--: | :------: | :------- |
|     uid      |  是  |  String  | 评论uid  |
|   works_id   |  是  |  String  | 作品uid  |
|   user_id    |  是  |  String  | 用户uid  |
| head_img_url |  是  |  String  | 头像     |
|     nick     |  是  |  String  | 昵称     |
|   like_num   |  是  | Integer  | 点赞量   |
|   content    |  是  |  String  | 内容     |
| create_time  |  是  | Integer  | 创建时间 |
|   is_like    |  是  | Boolean  | 是否点赞 |

返回示例：

```json
{
    "data": [{
    	"uid": "123456",
        "works_id": "245687",
        "user_id": "qiandg",
        "head_img_url": "www.baidu.com/img/1.jpg",
        "nick": "我是祖国的花朵",
        "like_num": 666,
        "content": "我是祖国的花朵",
        "create_time": 12545248814,
        "is_like": true
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 18.作品评论接口

请求URL：

```
/api/v1/works/comment
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，记录评论，用户必须登录才能操作。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| works_id |  是  |  String  | 作品id   |
| content  |  是  |  String  | 内容     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 19.评论点赞接口

请求URL：

```
/api/v1/comment/like
```

请求方式：

```
POST
```

接口说明：

```
评论点赞，用户必须登录才能操作。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 |
| :--------: | :--: | :------: | :------- |
|  works_id  |  是  |  String  | 作品id   |
| comment_id |  是  |  String  | 评论uid  |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 20.评论删除接口

请求URL：

```
/api/v1/comment/delete
```

请求方式：

```
PUT
```

接口说明：

```
删除评论， 用户必须登录才能操作。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 |
| :--------: | :--: | :------: | :------- |
| comment_id |  是  |  String  | 评论uid  |

返回字段： 无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 21.评论举报接口

请求URL：

```
/api/v1/comment/report
```

请求方式：

```
POST
```

接口说明：

```
评论举报，用户必须登录才能操作。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 |
| :--------: | :--: | :------: | :------- |
| comment_id |  是  |  String  | 评论uid  |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 22.关注作者接口

请求URL：

```
/api/v1/author/follow
```

请求方式：

```
POST
```

接口说明：

```
关注作者接口，用户必须登录才能操作。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明 |
| :-------: | :--: | :------: | :------- |
| author_id |  是  |  String  | 作者id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 23.供选标签接口

请求URL：

```
/api/v1/custom/label/option
```

请求方式：

```
GET
```

接口说明：

```
自定义标签页面，提供诸多标签供用户选择。
```

请求参数：无

返回字段：无

返回示例：

```json
{
    "data": [
        "美丽",
        "大方",
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 24.自定义标签接口

请求URL：

```
/api/v1/custom/label
```

请求方式：

```
POST
```

接口说明：

```
用户自定义图集、影集标签栏的标签，用户必须登录才能操作。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明           |
| :--------: | :--: | :------: | :----------------- |
|    type    |  是  |  String  | pic图集，video影集 |
| label_list |  是  |  Array   | 标签数组           |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 25.拉黑用户或作品

请求URL：

```
/api/v1/blacklist
```

请求方式：

```
POST
```

接口说明：

```
拉黑用户或作品，用户必须登录才能操作。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明             |
| :------: | :--: | :------: | :------------------- |
|   type   |  是  |  String  | user用户, works作品  |
| black_id |  是  |  String  | 被拉黑用户id或作品id |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 

#### 二、登录注册

##### 1.图片验证码接口

请求URL：

```
/api/v1/captcha
```

请求方式：

```
GET
```

接口说明：

```
获取图片验证码。
```

请求参数：无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明         |
| :------: | :--: | :------: | :--------------- |
|   uid    |  是  |  String  | 图片码uid        |
|   pic    |  是  |  String  | base64格式的图片 |

返回示例：

```json
{
    "data": {
        "uid": "1234456",
        "pic": "data:image/jpg;base64, xxxxxx"
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.发送短信接口

请求URL：

```
/api/v1/sms
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，获取短信验证码。  调试阶段短信验证码固定为111
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明    |
| :------: | :--: | :------: | :---------- |
|   uid    |  是  |  String  | 图片唯一uid |
| pic_code |  是  |  String  | 图片验证码  |
|  mobile  |  是  |  String  | 手机号      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.短信校验接口

请求URL：

```
/api/v1/sms/verify
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，校验短信码的正确性。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
| sms_code |  是  |  String  | 短信验证码 |
|  mobile  |  是  |  String  | 手机号     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.用户注册接口

请求URL：

```
/api/v1/register
```

请求方式：

```
POST
```

接口说明：

```
用户注册。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
|  mobile  |  是  |  String  | 手机号     |
| password |  是  |  String  | 密码       |
|  oauth   |  否  |  Object  | 第三方信息 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.账号登录接口

请求URL：

```
/api/v1/login/account
```

请求方式：

```
POST
```

接口说明：

```
用户账号登录。
```

请求参数：

| 请求参数 | 必须 |   参数类型   | 参数说明 |
| :------: | :--: | :----------: | :------- |
|  mobile  |  是  | String手机号 | 手机号   |
| password |  是  |    String    | 密码     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.手机登录接口

请求URL：

```
/api/v1/login/mobile
```

请求方式：

```
POST
```

接口说明：

```
用户手机登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|  mobile  |  是  |  String  | 手机号   |
| sms_code |  是  |  String  | 验证码   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.第三方绑定接口

请求URL：

```
/api/v1/oauth/bind
```

请求方式：

```
POST
```

接口说明：

```
第三方绑定。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明   |
| :------: | :--: | :------: | :--------- |
|  mobile  |  是  |  String  | 手机号     |
|  oauth   |  是  |  Object  | 第三方信息 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.第三方登录接口

请求URL：

```
/api/v1/oauth/login
```

请求方式：

```
POST
```

接口说明：

```
第三方登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                      |
| :------: | :--: | :------: | :---------------------------- |
|  userid  |  是  |  String  | 第三方用户唯一id              |
| platform |  是  |  String  | 第三方平台。wechat、qq、weibo |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

#### 三、用户个人中心

##### 1.用户基本信息接口

请求URL：

```
/api/v1/user/info
```

请求方式：

```
GET
```

接口说明：

```
第三方登录。 请求头必须携带token
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明                         |
| :-------: | :--: | :------: | :------------------------------- |
| author_id |  否  |  String  | 作者id，查询作者信息时才需要传。 |

返回字段：

|    返回字段    | 必须 | 字段类型 | 字段说明                    |
| :------------: | :--: | :------: | :-------------------------- |
|      uid       |  是  |  String  | 用户唯一id                  |
|      nick      |  是  |  String  | 昵称                        |
|      sex       |  是  |  String  | 性别                        |
|  head_img_url  |  是  |  String  | 头像                        |
|      sign      |  是  |  String  | 签名                        |
|     mobile     |  是  |  String  | 手机                        |
| background_url |  是  |  String  | 背景图                      |
|   works_num    |  是  | Integer  | 作品数                      |
|     label      |  是  |  Array   | 标签                        |
|      day       |  是  | Integer  | 注册天数                    |
|      auth      |  是  | Integer  | 0未提交认证，1审核中，2通过 |
|  order_count   |  是  | Integer  | 订单未完成数                |
| dynamic_count  |  是  | Integer  | 关注用户作品动态数          |

返回示例：

```json
{
    "data": {
        "uid": "123456",
        "nick": "我是祖国的花朵",
        "sex": "保密",
        "head_img_url": "www.baidu.com/img/1.jpg",
        "sign": "我是祖国的花朵",
        "mobile": "18812345678",
        "background_url": "www.baidu.com/img/2.png",
        "works_num": 250,
        "label": ["傲慢", "可爱", "二次元"],
        "day": 150,
        "auth": 2,
        "order_count": 5,
        "dynamic_count": 50
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.修改基本信息接口

请求URL：

```
/api/v1/user/info/alter
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改用户基本信息。 请求头必须携带token
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明           |
| :------: | :--: | :------: | :----------------- |
|   nick   |  否  |  String  | 昵称               |
|   sign   |  否  |  String  | 签名               |
|   sex    |  否  |  String  | 性别               |
|  label   |  否  |  Array   | 兴趣标签  上限20个 |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.我的消息接口

请求URL：

```
/api/v1/user/message
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户消息。
```

请求参数：无

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   |
| :---------: | :--: | :------: | :--------- |
|     uid     |  是  |  String  | uid        |
| push_people |  是  |  String  | 推送人昵称 |
|    desc     |  是  |  String  | 描述       |
| create_time |  是  | Integer  | 毫秒时间戳 |
| update_time |  是  | Integer  | 毫秒时间戳 |

返回示例:

```json
{
    "data": [{
        "uid": "123468",
        "push_people": "二娃",
        "desc": "你被封号了",
        "create_time": 1593565215000,
        "update_time": 1593565215000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.删除我的消息接口

请求URL：

```
/api/v1/user/message/alter
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除我的消息。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| msg_uid  |  是  |  String  | 消息id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.用户关注列表页接口

请求URL：

```
/api/v1/user/follow/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的关注。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明   |
| :-------: | :--: | :------: | :--------- |
|  user_id  |  是  |  String  | 用户id     |
| search_kw |  否  |  String  | 搜索关键词 |
|   page    |  是  | Integer  | 页码       |
|    num    |  是  | Integer  | 页数       |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |
| :----------: | :--: | :------: | :------- |
|   user_id    |  是  |  String  | uid      |
|     nick     |  是  |  String  | 昵称     |
| head_img_url |  是  |  String  | 头像     |
|  works_num   |  是  | Integer  | 作品数   |

返回示例:

```json
{
    "data": [{
        "user_id": "123468",
        "nick": "二娃",
        "head_img_url": "http://www.baidu.com/img/1.png",
        "works_num": 200
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.搜索我的关注接口（舍弃）

请求URL：

```
/api/v1/user/follow/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的关注。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明   |
| :-------: | :--: | :------: | :--------- |
| search_kw |  是  |  String  | 搜索关键词 |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |
| :----------: | :--: | :------: | :------- |
|   user_id    |  是  |  String  | uid      |
|     nick     |  是  |  String  | 昵称     |
| head_img_url |  是  |  String  | 头像     |
|  works_num   |  是  | Integer  | 作品数   |

返回示例：

```json
{
    "data": [{
        "user_id": "123468",
        "nick": "二娃",
        "desc": "你被封号了",
        "works_num": 1593565215000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.取消关注接口

请求URL：

```
/api/v1/user/follow/cancel
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，取消关注。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明 |
| :-------: | :--: | :------: | :------- |
| author_id |  是  |  String  | 作者id   |

返回字段：无

返回数据：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.我的关注作品动态接口

请求URL：

```
/api/v1/user/follow/news
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取关注作者作品动态。
```

请求参数：无

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                     |
| :----------: | :--: | :------: | :--------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                          |
|   pic_item   |  否  |  Array   | 素材       |                                          |
|  video_url   |  否  |  String  | 视频路径   |                                          |
|  audio_url   |  否  |  String  | 音频路径   |                                          |
|   user_id    |  否  |  String  | 用户id     |                                          |
|     nick     |  是  |  String  | 用户昵称   |                                          |
| head_img_url |  是  |  String  | 用户头像   |                                          |
|  works_num   |  是  | Integer  | 作品数量   |                                          |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览                 |
|    title     |  是  |  String  | 标题       |                                          |
|     desc     |  是  |  String  | 描述       |                                          |
|  cover_url   |  否  |  String  | 封面路径   |                                          |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中                       |
|    label     |  否  |  Array   | 标签       | 图文无标签                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1            |
|   like_num   |  是  | Integer  | 点赞量     |                                          |
| comment_num  |  是  | Integer  | 评论量     |                                          |
|  share_num   |  是  | Integer  | 分享量     |                                          |
|  browse_num  |  是  | Integer  | 浏览量     |                                          |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                               |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                  |

返回示例：

```json
{
    "data": {
        "works_list": [{
                "uid": "123456", // 作品唯一id
                "pic_item": [{
                        "uid": "7893432", // 图片唯一id
                        "works_id": "123456", // 作品id
                        "big_pic_url": "www.baidu.com/img/1.png", // 大图
                        "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                        ...
                    },
                    ...
                ],
                "user_id": "123567",
                "nick": "喜好",
                "count": 1,
                "head_img_url": "www.baidu.com/img/1.png",
                "video_url": "www.baidu.com/video/1.mp4",
                "audio_url": "www.baidu.com/audio/1.mp3",
                "works_num": 250,
                "title": "生活",
                "desc": "一个人生活",
                "cover_url": Null,
                "content": Null,
                "label": ["美好", "幸福"],
                "state": 2,
                "is_recommend": true,
                "type": "tj",
                "is_like": true,
                "pic_num": 1,
                "like_num": 666,
                "comment_num": 666,
                "share_num": 666,
                "browse_num": 666,
                "create_time": 1593565215000,
                "update_time": 1593565215000
            },
            ...
        ],
        "count": 50
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.销售记录表接口

请求URL：

```
/api/v1/user/sales/record
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户的销售记录, 用户必须登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   page   |  是  | Integer  | 页码     |
|   num    |  是  | Integer  | 页数     |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 |
| :---------: | :--: | :------: | :------- |
|     uid     |  是  |  String  | 评论id   |
|    title    |  是  |  String  | 标题     |
|   amount    |  是  |  Float   | 金额     |
| create_time |  是  |  String  | 时间戳   |

返回示例：

```json
{
    "data": [{
        "uid": "001",
        "title": "别墅",
        "amount": "250.00",
        "create_time": 1593565215000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 10.用户商品概况接口

请求URL：

```
/api/v1/user/data/statistic
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户商品概况, 用户必须登录。
```

请求参数：无

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 |
| :---------: | :--: | :------: | :------- |
| browse_num  |  是  | Integer  | 评论数   |
|  sale_num   |  是  | Integer  | 销售量   |
| comment_num |  是  | Integer  | 评论数   |
| amount_num  |  是  | Integer  | 销售额   |
|  share_num  |  是  | Integer  | 分享量   |
|  like_num   |  是  | Integer  | 点赞量   |

返回示例：

```json
{
    "data": {
    	"browse_num": 250,
    	"sale_num": 250,
    	"comment_num": 250,
    	"amount_num": 250,
    	"share_num": 250,
    	"like_num": 250
	},
    "msg": "Request successful.",
    "code": 0
}
```

##### 11.账户支付方式接口

请求URL：

```
/api/v1/user/paymethod
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户支付方式, 用户必须登录。
```

请求参数：无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| channel  |  是  |  String  | 支付方式 |
| ico_url  |  是  |  String  | 平台图标 |
|   fees   |  是  |  Float   | 手续费   |

返回示例：

```json
{
    "data": [{
    	"channel": "微信",
    	"ico_url": "http://www.baidu.com/ico/1.ico",
    	"fees": 0.01,
		},
        ...
    ]
    "msg": "Request successful.",
    "code": 0
}
```

##### 12.账户余额、日收益接口

请求URL：

```
/api/v1/user/balance
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户余额、昨日收益, 用户必须登录。
```

请求参数：无

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
| balance  |  是  |  Float   | 账户余额 |
|  amount  |  是  |  Float   | 昨日收益 |
|   fees   |  是  | Integer  | 手续费   |
|   lock   |  是  | Integer  | 锁定数字 |

返回示例：

```json
{
    "data": {
    	"balance": 250.0,
    	"amount": 250.0,
        "fees": 1,
        "lock": 200
    }
    "msg": "Request successful.",
    "code": 0
}
```

##### 13.用户主页接口

请求URL：

```
/api/v1/user/home/page
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户主页信息。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   page   |  否  |  String  | 页码     |
|   num    |  否  |  String  | 页数     |
| user_id  |  否  |  String  | 用户id   |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                       |
| :----------: | :--: | :------: | :--------- | ------------------------------------------ |
|     uid      |  是  |  String  | 作品唯一id |                                            |
|   pic_item   |  否  |  Array   | 素材       |                                            |
|  video_url   |  否  |  String  | 视频路径   |                                            |
|  audio_url   |  否  |  String  | 音频路径   |                                            |
|  works_num   |  是  | Integer  | 作品数量   |                                            |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览。                 |
|    title     |  是  |  String  | 标题       |                                            |
|     desc     |  是  |  String  | 描述       |                                            |
|  cover_url   |  否  |  String  | 封面路径   |                                            |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞。                  |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中。                       |
|    label     |  否  |  Array   | 标签       | 图文无标签。                               |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架。 |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐。                  |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文。            |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1              |
|   like_num   |  是  | Integer  | 点赞量     |                                            |
| comment_num  |  是  | Integer  | 评论量     |                                            |
|  share_num   |  是  | Integer  | 分享量     |                                            |
|  browse_num  |  是  | Integer  | 浏览量     |                                            |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                                 |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                                 |

返回示例:

```json
{
    "data": [{
            "uid": "123456", // 作品唯一id
            "pic_item": [{
                    "uid": "7893432", // 图片唯一id
                    "works_id": "123456", // 作品id
                    "big_pic_url": "www.baidu.com/img/1.png", // 大图
                    "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                    "title": "别墅"
                        ...
                },
                ...
            ],
            "user_id": "123567",
            "count": 1,
            "video_url": "www.baidu.com/video/1.mp4",
            "audio_url": "www.baidu.com/audio/1.mp3",
            "works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": Null,
            "content": Null,
            "label": ["美好", "幸福"],
            "state": 2,
            "is_recommend": true,
            "type": "tj",
            "is_like": true,
            "pic_num": 1,
            "like_num": 666,
            "comment_num": 666,
            "share_num": 666,
            "browse_num": 666,
            "create_time": 1593565215000,
            "update_time": 1593565215000
        },
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 14.用户粉丝列表页接口

请求URL：

```
/api/v1/user/fans/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的关注。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| user_id  |  是  |  String  | 用户id   |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明 |
| :----------: | :--: | :------: | :------- |
|   user_id    |  是  |  String  | uid      |
|     nick     |  是  |  String  | 昵称     |
| head_img_url |  是  |  String  | 头像     |
| create_time  |  是  | Integer  | 创建时间 |

返回示例：

```json
{
    "data": [{
        "user_id": "123468",
        "nick": "二娃",
        "head_img_url": "http://www.baidu.com/img/1.png",
        "create_time": 1593565215000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 15.我的作品接口

请求URL：

```
/api/v1/user/works/manage
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的作品，用户必须登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   page   |  是  | Integer  | 页码     |
|   num    |  是  | Integer  | 页数     |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明   | 备注                                         |
| :----------: | :--: | :------: | :--------- | -------------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id |                                              |
|   pic_item   |  否  |  Array   | 素材       |                                              |
|  video_url   |  否  |  String  | 视频路径   |                                              |
|  audio_url   |  否  |  String  | 音频路径   |                                              |
|  works_num   |  是  | Integer  | 作品数量   |                                              |
|    count     |  是  | Integer  | 计数       | 0代表未浏览，1代表已浏览。【属于works_list】 |
|    title     |  是  |  String  | 标题       |                                              |
|     desc     |  是  |  String  | 描述       |                                              |
|  cover_url   |  否  |  String  | 封面路径   |                                              |
|   is_like    |  是  | Boolean  | 是否点赞   | true已点赞，false未点赞                      |
|   content    |  否  |  String  | 内容       | 图片路径插入文本中。                         |
|    label     |  否  |  Array   | 标签       | 图文无标签。                                 |
|    state     |  是  | Integer  | 状态       | -1删除  0未审核（默认） 1审核中  2已上架。   |
| is_recommend |  是  | Boolean  | 是否推荐   | true推荐  false取消推荐。                    |
|     type     |  是  |  String  | 分类       | tp图片 tj图集  yj影集  tw图文。              |
|   pic_num    |  否  | Integer  | 图片量     | 图文无图片量  图片为1  图集>1                |
|   like_num   |  是  | Integer  | 点赞量     |                                              |
| comment_num  |  是  | Integer  | 评论量     |                                              |
|  share_num   |  是  | Integer  | 分享量     |                                              |
|  browse_num  |  是  | Integer  | 浏览量     |                                              |
| create_time  |  是  | Integer  | 创建时间   | 毫秒时间戳                                   |
| update_time  |  是  | Integer  | 更新时间   | 毫秒时间戳                                   |

返回示例:

```json
{
	"data": [{
            "uid": "123456",	// 作品唯一id
            "pic_item": [{
            	"uid": "7893432",	// 图片唯一id
                "works_id": "123456", // 作品id
                "big_pic_url": "www.baidu.com/img/1.png",	// 大图
                "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
                "title": "别墅"
                ...
            	},
            	...
            ],
            "user_id": "123567",
            "count": 1,
        	"video_url": "www.baidu.com/video/1.mp4",
        	"audio_url": "www.baidu.com/audio/1.mp3",
        	"works_num": 250,
            "title": "生活",
            "desc": "一个人生活",
            "cover_url": Null,
            "content": Null,
            "label": ["美好", "幸福"],
        	"state": 2,
        	"is_recommend": true,
        	"type": "tj",
            "is_like": true,
        	"pic_num": 1,
        	"like_num": 666,
        	"comment_num": 666,
        	"share_num": 666,
        	"browse_num": 666,
        	"create_time": 1593565215000,
        	"update_time": 1593565215000
        },
        ...   
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 16.我的评论历史

请求URL：

```
/api/v1/user/history/comment
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的评论历史，用户必须登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   page   |  是  | Integer  | 页码     |
|   num    |  是  | Integer  | 页数     |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明               |
| :----------: | :--: | :------: | :--------------------- |
|     uid      |  是  |  String  | 唯一id                 |
|   works_id   |  是  |  String  | 作品id                 |
|     nick     |  是  |  String  | 昵称                   |
|   is_like    |  是  | Boolean  | true已点赞,false未点赞 |
|   like_num   |  是  | Integer  | 点赞数                 |
| head_img_url |  是  |  String  | 头像                   |
|    title     |  是  |  String  | 标题                   |

返回示例：

```json
{
    "data": [{
        "uid": "0001",
        "works_id": "0002",
        "title": "大哥大",
        "nick": "中国",
        "is_like": true,
        "head_img_url": "http://www.baidu.com/img/1.png",
        "like_num": 250
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 17.我的点赞历史

请求URL：

```
/api/v1/user/history/like
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的点赞历史，用户必须登录。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|   page   |  是  | Integer  | 页码     |
|   num    |  是  | Integer  | 页数     |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明               |
| :----------: | :--: | :------: | :--------------------- |
|     nick     |  是  |  String  | 昵称                   |
|   is_like    |  是  | Boolean  | true已点赞,false未点赞 |
|   like_num   |  是  | Integer  | 点赞数                 |
| head_img_url |  是  |  String  | 头像                   |
|    title     |  是  |  String  | 标题                   |

返回示例：

```json
{
    "data": [{
        "title": "大哥大",
        "nick": "中国",
        "is_like": true,
        "head_img_url": "http://www.baidu.com/img/1.png",
        "like_num": 250
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 18.我的图片素材库列表接口

请求URL：

```
/api/v1/user/material/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户素材图片。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                        |
| :------: | :--: | :------: | :------------------------------ |
|   page   |  是  | Integer  | 页码                            |
|   num    |  是  | Integer  | 页数                            |
| content  |  是  |  String  | 搜索内容。不搜索时默认传default |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明   |
| :---------: | :--: | :------: | :--------- |
|     uid     |  是  |  String  | 图片id     |
|    title    |  是  |  String  | 标题       |
|    label    |  是  |  Array   | 标签       |
| big_pic_url |  是  |  String  | 大图片路径 |
|  thumb_url  |  是  |  String  | 缩略图路径 |
| create_time |  是  | Integer  | 时间戳     |

返回示例：

```json
{
    "data": [{
        "title": "大哥大",
        "uid": "0122154",
        "label": ["我的", "他的", "哈哈"],
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "thumb_url": "http://www.baidu.com/img/1.png",
        "create_time": 1594848185000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 19.图片素材修改标题接口

请求URL：

```
/api/v1/user/material/title
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改素材标题。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|  pic_id  |  是  |  String  | 图片id   |
|  title   |  是  |  String  | 标题     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 20.图片素材修改标签接口

请求URL：

```
/api/v1/user/material/label
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改素材标签。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
|  pic_id  |  是  |  String  | 图片id   |
|  label   |  是  |  Array   | 标签     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 21.图片素材删除接口

请求URL：

```
/api/v1/user/material/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除素材。
```

请求参数：

|  请求参数   | 必须 | 参数类型 | 参数说明 |
| :---------: | :--: | :------: | :------- |
| pic_id_list |  是  |  Array   | 图片id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 22.图片素材上传接口

请求URL：

```
/api/v1/user/material/upload
```

请求方式：

```
POST
```

接口说明：

```
我的素材库上传接口。
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

##### 23.我的音频素材库列表接口

请求URL：

```
/api/v1/user/audio/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取用户音频素材。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                        |
| :------: | :--: | :------: | :------------------------------ |
|   page   |  是  | Integer  | 页码                            |
|   num    |  是  | Integer  | 页数                            |
| content  |  是  |  String  | 搜索内容。不搜索时默认传default |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明 |
| :---------: | :--: | :------: | :------- |
|     uid     |  是  |  String  | 图片id   |
|    title    |  是  |  String  | 标题     |
|    label    |  是  |  Array   | 标签     |
|  cover_url  |  是  |  String  | 封面路径 |
|  audio_url  |  是  |  String  | 音频路径 |
| create_time |  是  | Integer  | 时间戳   |

返回示例：

```json
{
    "data": [{
        "title": "大哥大",
        "uid": "0122154",
        "label": ["我的", "他的", "哈哈"],
        "cover_url": "http://www.baidu.com/img/1.png",
        "audio_url": "http://www.baidu.com/img/1.png",
        "create_time": 1594848185000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 24.音频素材修改标题接口

请求URL：

```
/api/v1/user/audio/title
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改音频素材标题。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| audio_id |  是  |  String  | 音频id   |
|  title   |  是  |  String  | 标题     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 25.音频素材修改标签 接口

请求URL：

```
/api/v1/user/audio/label
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，修改音频素材标签。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| audio_id |  是  |  String  | 音频id   |
|  label   |  是  |  Array   | 标签     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 26.音频素材删除接口

请求URL：

```
/api/v1/user/audio/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除图片素材。
```

请求参数：

|   请求参数    | 必须 | 参数类型 | 参数说明 |
| :-----------: | :--: | :------: | :------- |
| audio_id_list |  是  |  Array   | 音频id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 27.音频素材上传接口

请求URL：

```
/api/v1/user/audio/upload
```

请求方式：

```
POST
```

接口说明：

```
音频素材上传
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 |
| :--------: | :--: | :------: | :------- |
| cover_url  |  是  |  String  | 封面     |
| audio_url  |  是  |  String  | 音频路径 |
| audio_size |  是  | Integer  | 音频大小 |
|   title    |  是  |  String  | 标题     |
|   label    |  是  |  Array   | 标签     |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 28.图片、图集、影集、图文作品列表

请求URL：

```
/api/v1/user/works/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回我的图片图集作品列表
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                                    |
| :------: | :--: | :------: | :------------------------------------------ |
|   page   |  是  | Integer  | 页码                                        |
|   num    |  是  | Integer  | 页数                                        |
| content  |  是  |  String  | 搜索内容，不搜索时默认传default             |
|  state   |  是  | Integer  | 0未审核，1审核中，2已上架, 3违规下架，4全部 |
|   type   |  是  |  String  | tp图片，tj图集，yj影集, tw图文              |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明                                   |
| :---------: | :--: | :------: | :----------------------------------------- |
|     uid     |  是  |  String  | 作品id                                     |
|    title    |  是  |  String  | 标题                                       |
|    label    |  是  |  Array   | 标签                                       |
|  cover_url  |  是  |  String  | 封面路径                                   |
| big_pic_url |  是  |  String  | 大图路径                                   |
|    desc     |  否  |  String  | 图文描述                                   |
|   pic_id    |  是  |  Array   | 图片id                                     |
|    state    |  是  | Integer  | 状态。0未审核，1审核中，2已上架，3违规下架 |
| create_time |  是  | Integer  | 时间戳                                     |

返回示例：

```json
{
    "data": [{
        "title": "大哥大",
        "uid": "0122154",
        "label": ["我的", "他的", "哈哈"],
        "pic_id": ["111", "222"],
        "cover_url": "http://www.baidu.com/img/1.png",
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "desc": "哈哈哈啊",
        "state": 2,
        "create_time": 1594848185000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 29.删除作品接口

请求URL：

```
/api/v1/user/works/delete
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，删除作品。
```

请求参数：

|   请求参数    | 必须 | 参数类型 | 参数说明 |
| :-----------: | :--: | :------: | :------- |
| works_id_list |  是  |  Array   | 作品id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 30.图片申请上架详情接口

请求URL：

```
/api/v1/user/works/pic/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取作品信息。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| works_id |  是  |  String  | 作品id   |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明                         |
| :---------: | :--: | :------: | :------------------------------- |
|     uid     |  是  |  String  | 图片id                           |
|    title    |  是  |  String  | 标题                             |
|    label    |  是  |  Array   | 标签                             |
| big_pic_url |  是  |  String  | 大图路径                         |
|    state    |  是  | Integer  | 状态。0未审核，1审核中，2已上架  |
|   format    |  是  |  String  | 文件格式                         |
|   number    |  是  |  String  | 文件编号                         |
|     tag     |  是  |  String  | 标签。 商/编                     |
| price_item  |  是  |  Array   | 价格列表                         |
|    code     |  是  | Integer  | 0代表平台定价，1代表自定义定价。 |

返回示例：

```json
{
    "data": {
        "title": "大哥大",
        "uid": "0122154",
        "label": ["我的", "他的", "哈哈"],
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "state": 2,
        "format": PNG,
        "number": mn123456,
        "tag": "商",
        "code": 0,
        "price_item": [{
           "format": "S",
            "price": 55.0
        },
    "msg": "Request successful.",
    "code": 0
}
```

##### 31.肖像权接口

请求URL：

```
/api/v1/user/portrait
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，上传肖像权信息。
```

请求参数：

|  请求参数   | 必须 | 参数类型 | 参数说明       | 备注                             |
| :---------: | :--: | :------: | :------------- | -------------------------------- |
|  works_id   |  是  |  String  | 作品id         |                                  |
|   pic_url   |  是  |  String  | 肖像参考图     |                                  |
| shoot_addre |  是  |  String  | 拍摄地         |                                  |
| shoot_time  |  是  | Integer  | 拍摄时间       |                                  |
|   b_name    |  是  |  String  | 乙方姓名       |                                  |
|  b_id_card  |  是  |  String  | 乙方身份证     |                                  |
|  b_mobile   |  是  |  String  | 乙方手机       |                                  |
| b_home_addr |  是  |  String  | 乙方地址       |                                  |
| authorizer  |  是  |  Array   | 授权人信息     | 以下字段组成对象存入authorizer中 |
|    name     |  是  |  String  | 授权人姓名     |                                  |
|   id_card   |  是  |  String  | 授权人身份证   |                                  |
|     sex     |  是  |  String  | 授权人性别     |                                  |
|   mobile    |  是  |  String  | 授权人手机     |                                  |
| home_addre  |  是  |  String  | 授权人地址     |                                  |
|  is_adult   |  是  | Boolean  | 授权人是否成年 | true成年，false未成年            |
|   g_name    |  是  |  String  | 监护人姓名     | 只有当未成年时才有               |
|  g_id_card  |  是  |  String  | 监护人身份证   | 只有当未成年时才有               |
|  g_mobile   |  是  |  String  | 监护人手机     | 只有当未成年时才有               |

返回字段：无

返回示例：

```json
{
    "data": 1,  // 1已上传，0未上传
    "msg": "Request successful.",
    "code": 0
}
```

##### 32.物产权接口

请求URL：

```
/api/v1/user/property
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，上传物产权信息。
```

请求参数：

|    请求参数     | 必须 | 参数类型 | 参数说明   | 备注 |
| :-------------: | :--: | :------: | :--------- | ---- |
|    works_id     |  是  |  String  | 作品id     |      |
|     a_name      |  是  |  String  | 甲方姓名   |      |
|    a_id_card    |  是  |  String  | 甲方身份证 |      |
|    a_mobile     |  是  |  String  | 甲方手机   |      |
|     a_email     |  是  |  String  | 甲方邮箱   |      |
|   a_home_addr   |  是  |  String  | 甲方地址   |      |
| a_property_desc |  是  |  String  | 财产描述   |      |
| a_property_addr |  是  |  String  | 财产地址   |      |
|     pic_url     |  是  |  String  | 肖像参考图 |      |
|     b_name      |  是  |  String  | 乙方姓名   |      |
|    b_id_card    |  是  |  String  | 乙方身份证 |      |
|    b_mobile     |  是  |  String  | 乙方手机   |      |
|     b_email     |  是  |  String  | 乙方邮箱   |      |
|   b_home_addr   |  是  |  String  | 乙方地址   |      |

返回字段：无

返回示例：

```json
{
    "data": 1,  // 1已上传，0未上传
    "msg": "Request successful.",
    "code": 0
}
```

##### 33.图片作品上架申请

请求URL：

```
/api/v1/user/works/apply
```

请求方式：

```
POST
```

接口说明：

```
根据请求参数，上传申请信息。
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                             |
| :--------: | :--: | :------: | :------- | -------------------------------- |
|    uid     |  是  |  String  | 作品id   |                                  |
|   title    |  是  |  String  | 标题     |                                  |
|   label    |  是  |  Array   | 标签     |                                  |
|    tag     |  是  |  String  | 商/编    |                                  |
| price_item |  否  |  Array   | 价格信息 | [{foramt: , price: },...]        |
|    code    |  是  | Integer  | 状态     | 0代表平台定价，1代表自定义定价。 |

返回字段：无

返回示例：

```json
{
    "data":null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 34.图集上架申请详情

请求URL：

```
/api/v1/user/altas/detail
```

请求方式：

```
GET
```

接口说明：

```
图集上架申请详情。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| :------: | :--: | :------: | :------- | ---- |
| works_id |  是  |  String  | 作品id   |      |

返回字段:

|  返回字段   | 必须 | 字段类型 | 字段说明                                | 备注                           |
| :---------: | :--: | :------: | :-------------------------------------- | ------------------------------ |
|     uid     |  是  |  String  | 图片id                                  |                                |
|    title    |  是  |  String  | 标题                                    |                                |
|    label    |  是  |  Array   | 标签                                    |                                |
|    state    |  是  | Integer  | 状态。0未审核，1审核中，2已上架         |                                |
|  cover_url  |  是  |  String  | 封面                                    |                                |
|  pic_item   |  是  |  Array   | 图集信息                                | 以下字段组成对象存入pic_item中 |
|     uid     |  是  |  String  | uid                                     |                                |
| big_pic_url |  是  |  String  | 大图                                    |                                |
|  thumb_url  |  是  |  String  | 缩略图                                  |                                |
| works_state |  是  |  String  | 状态。0未审核【默认】，1审核中，2已上架 |                                |

返回示例：

```json
{
    "data": {
        "uid": "0124151",
        "title": "我是祖国的花朵",
        "label": ["强大", "繁荣"],
        "state": 2,
        "pic_item": [{
                "uid": "001",
                "big_pic_url": "http://www.baidu.com/img/1.png",
                "thumb_url": "http://www.baidu.com/img/1.png",
                "works_state": 2
            }
            ...
        ]
    }，
    "msg": "Request successful.",
    "code": 0
}
```

##### 35.图集上架申请

请求URL：

```
/api/v1/user/altas/apply
```

请求方式：

```
POST
```

接口说明：

```
图集上架申请。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明 | 备注 |
| :-------: | :--: | :------: | :------- | ---- |
|    uid    |  是  |  String  | 作品id   |      |
|   title   |  是  |  String  | 标题     |      |
|   label   |  是  |  Array   | 标签     |      |
| cover_url |  是  |  String  | 封面     |      |

返回字段：无

返回示例：

```json
{
    "data": null
    "msg": "Request successful.",
    "code": 0
}
```

##### 36.图文作品列表接口

请求URL：

```
/api/v1/user/works/article
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回我的图文作品。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                                    |
| :------: | :--: | :------: | :------------------------------------------ |
|   page   |  是  | Integer  | 页码                                        |
|   num    |  是  | Integer  | 页数                                        |
| content  |  是  |  String  | 搜索内容，不搜索时默认传default             |
|  state   |  是  | Integer  | 0未审核，1审核中，2已上架, 3违规下架，4全部 |

返回字段：

|  返回字段   | 必须 | 字段类型 | 字段说明                        |
| :---------: | :--: | :------: | :------------------------------ |
|     uid     |  是  |  String  | 图片id                          |
|    title    |  是  |  String  | 标题                            |
|   content   |  是  |  String  | 内容                            |
|  cover_url  |  是  |  String  | 封面路径                        |
|    state    |  是  | Integer  | 状态。0未审核，1审核中，2已上架 |
| create_time |  是  | Integer  | 时间戳                          |

返回示例：

```json
{
    "data": [{
        "title": "大哥大",
        "uid": "0122154",
        "content": "我爱你我的祖国......",
        "cover_url": "http://www.baidu.com/img/1.png",
        "state": 2,
        "create_time": 1594848185000
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 37.作品批量上架申请

请求URL：

```
/api/v1/user/works/batch
```

请求方式：

```
POST
```

接口说明：

```
作品批量上架申请
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明                |
| :--------: | :--: | :------: | :---------------------- |
|    uid     |  是  |  Array   | 作品id                  |
| is_article |  是  | Boolean  | 图文上架true，否则false |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 38.地址三联接口

请求URL：

```
/api/v1/area
```

请求方式：

```
GET
```

接口说明：

```
获取地址信息
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明                        |
| :------: | :--: | :------: | :------------------------------ |
| area_id  |  是  |  String  | 一级传defualt, 二三级传对应的id |
|   step   |  是  |  String  | 一级传1，二级传2，三级传3       |

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| :------: | :--: | :------: | :------- |
|   uid    |  是  |  String  | 地址id   |
|   name   |  是  |  String  | 名称     |

返回示例：

```json
{
  "data": [
    {
      "name": "北京市",
      "uid": "110000"
    },
    {
      "name": "天津市",
      "uid": "120000"
    },
    ...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 39.更换用户头像

请求URL：

```
/api/v1/user/head/update
```

请求方式：

```
PUT
```

接口说明：

```
更换用户头像。
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

##### 40.用户更换背景图接口

请求URL：

```
/api/v1/user/background/update
```

请求方式：

```
PUT
```

接口说明：

```
更换背景图接口。
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

##### 41.推荐兴趣标签接口

请求URL：

```
/api/v1/user/interest
```

请求方式：

```
GET
```

接口说明：

```
推荐兴趣标签接口
```

请求参数：无

返回字段：无

返回示例：

```json
{
    "data": [
        "可爱",
        "性感",
        "火辣",
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 42.我的图片库列表接口

请求URL：

```
/api/v1/user/goods/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的商品列表
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| content  | 是   | String   | 搜索内容 |

返回字段：

| 返回字段  | 必须 | 字段类型 | 字段说明                                  |
| --------- | ---- | -------- | ----------------------------------------- |
| works_id  | 是   | String   | 作品id                                    |
| title     | 是   | String   | 标题                                      |
| thumb_url | 是   | String   | 缩略图路径                                |
| spec_list | 是   | Array    | 规格及路径[{"pic_url": , "format": },...] |

返回示例：

```json
{
    "data": {
        "works_id": "001",
        "title": "哈哈哈",
        "thumb_url": "http://www.baidu.com/img/1.png",
        "spec_list": [{
            	"format": "S",
            	"pic_url": "http://www.baidu.com/img/1.png"
        	},
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 43.购买图片详情接口

请求URL：

```
/api/v1/user/goods/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，获取我的商品列表
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| uid      | 是   | String   | 作品id   |

返回字段：

|   返回字段   | 必须 | 字段类型 | 字段说明     | 备注                                     |
| :----------: | :--: | :------: | :----------- | ---------------------------------------- |
|     uid      |  是  |  String  | 作品唯一id   |                                          |
|   pic_item   |  否  |  Array   | 素材         |                                          |
|    number    |  是  |  String  | 文件编号     |                                          |
|    format    |  是  |  String  | 文件格式     |                                          |
|   user_id    |  是  |  String  | 用户id       |                                          |
|     nick     |  是  |  String  | 昵称         |                                          |
| head_img_url |  是  |  String  | 头像         |                                          |
|  works_num   |  是  | Integer  | 作品量       |                                          |
|   price_id   |  是  |  String  | 定价id       |                                          |
|    title     |  是  |  String  | 标题         |                                          |
|     desc     |  是  |  String  | 描述         |                                          |
|    label     |  否  |  Array   | 标签         | 图文无标签                               |
|    state     |  是  | Integer  | 状态         | -1删除  0未审核（默认） 1审核中  2已上架 |
| is_recommend |  是  | Boolean  | 是否推荐     | true推荐  false取消推荐                  |
| is_portrait  |  是  | Boolean  | 是否有肖像权 | true有，false无                          |
| is_products  |  是  | Boolean  | 是否有物产权 | true有，false无                          |
|     type     |  是  |  String  | 分类         | tj图集  yj影集  tw图文 lj链接 pc图片     |
|   pic_num    |  否  | Integer  | 图片量       | 图文无图片量  图片为1                    |
|   like_num   |  是  | Integer  | 点赞量       |                                          |
| comment_num  |  是  | Integer  | 评论量       |                                          |
|  share_num   |  是  | Integer  | 分享量       |                                          |
|  browse_num  |  是  | Integer  | 浏览量       |                                          |
| create_time  |  是  | Integer  | 创建时间     | 毫秒时间戳                               |
| update_time  |  是  | Integer  | 更新时间     | 毫秒时间戳                               |
|  is_follow   |  是  | Boolean  | 是否关注     | true已关注，false未关注                  |

返回示例：

```json
{
	"data": {
       "pic_data": {	// 图片信息
           "uid": "123456",	// 作品唯一id
           "pic_item": [{
              "uid": "7893432",	// 图片唯一id
              "works_id": "123456", // 作品id
              "big_pic_url": "www.baidu.com/img/1.png",	// 大图
           	  "thumb_url": "www.baidu.com/thumb/1.png", // 缩略图路径
               "title": "洱海"
              	...
          		},
            	...
            ],
            "number": "fm123456",
            "format": "PNG",
            "price_id": "2309530",
            "user_id": "123567",
			"nick": "喜好",
        	"head_img_url": "www.baidu.com/img/1.png",
        	"works_num": 250,
        	"title": "生活",
        	"desc": "一个人生活",
        	"content": Null,
            "label": ["美好", "幸福"],
            "state": 2,
            "tag": "商",
            "is_recommend": true,
            "is_portrait": true,
            "is_products": true,
            "is_follow": true,
            "type": "tj",
            "pic_num": 1,
            "like_num": 666,
            "comment_num": 666,
            "share_num": 666,
            "browse_num": 666,
            "create_time": 1593565215000,
            "update_time": 1593565215000,
    	},
    	"price_data": [{  // 价格规格信息
            "format": "S",	// 格式  S、M、L、扩大授权
            "currency": "¥",	// 币种
            "price": "55.00",	// 价格
            "width": 500,	// 宽度
            "height": 800,	// 高度
            "pic_url": "http://www.baidu.com/img/1.png"
        	},
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 44.图片保存

请求URL：

```
/api/v1/user/works/pic/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，编辑图片作品信息
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明 | 备注                             |
| :--------: | :--: | :------: | :------- | -------------------------------- |
|    uid     |  是  |  String  | 作品id   |                                  |
|   title    |  是  |  String  | 标题     |                                  |
|   label    |  是  |  Array   | 标签     |                                  |
|    tag     |  是  |  String  | 商/编    |                                  |
| price_item |  否  |  Array   | 价格信息 | [{foramt: , price: },...]        |
|    code    |  是  | Integer  | 状态     | 0代表平台定价，1代表自定义定价。 |

返回字段：无

返回示例：

```json
{
    "data":null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 45.肖像权详情接口

请求URL：

```
/api/v1/user/portrait/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回肖像权信息。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| works_id | 是   | String   | 作品id   |

返回字段：

|  返回字段   | 字段类型 |  字段说明  |                             备注                             |
| :---------: | :------: | :--------: | :----------------------------------------------------------: |
|  works_id   |  String  |   唯一id   |                           唯一索引                           |
|   user_id   |  String  |   用户id   |                                                              |
|  works_id   |  String  |   作品id   |                                                              |
|   pic_url   |  String  |  照片路径  |                                                              |
| shoot_addr  |  String  |  拍摄地址  |                                                              |
| shoot_time  | Integer  |  拍摄时间  |                                                              |
| authorizer  |  Array   | 授权人信息 | [{name, id_card, sex, mobile, home_addr,is_adult, g_name, g_id_card, g_mobile},...] |
|   b_name    |  String  |  乙方姓名  |                                                              |
|  b_id_card  |  String  | 乙方身份证 |                                                              |
|  b_mobile   |  String  | 乙方手机号 |                                                              |
| b_home_addr |  String  |  乙方地址  |                                                              |

返回示例：

```json
{
    "data": {
        "works_id": "001", // id
        "pic_url": "https://www.baidu.com/images/1.png", // 参考图
        "shoot_time": 1595743329000, // 拍摄时间
        "shoot_addr": "重庆市", // 拍摄地址
        "authorizer": [{ // 授权人信息
                "name": "李四", // 授权人姓名
                "id_card": "5020xxxxxxxxx", // 授权人身份证
                "sex": "男", // 授权人性别
                "mobile": "17725021251", // 授权人手机
                "home_addr": "重庆市xxxxx", // 授权人地址
                "is_adult": true, // 是否成年
            	"g_name": "哈哈",
            	"g_id_card": "500228xxxx",
            	"g_mobile": "1772502xxxx"
            },
            ....
        ],
        "b_name": "王五", // 乙方姓名
        "b_id_card": "5002281994xxxxxxxxx", // 乙方身份证
        "b_mobile": "17725021251", // 乙方手机
        "b_home_addr": "重庆市xxxxx", // 乙方地址
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 46.物产权详情接口

请求URL：

```
/api/v1/user/property/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回物产权信息。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| works_id | 是   | String   | 作品id   |

返回字段：

|    返回字段     | 字段类型 |   字段说明   |         备注         |
| :-------------: | :------: | :----------: | :------------------: |
|     user_id     |  String  |    用户id    |                      |
|    works_id     |  String  |    作品id    |                      |
|     a_name      |  String  |   甲方姓名   |   姓名或者公司名称   |
|    a_id_card    |  String  |  甲方证件号  | 身份证号或企业注册号 |
|    a_mobile     |  String  |  甲方手机号  |                      |
|     a_email     |  String  |   甲方邮箱   |                      |
|   a_home_addr   |  String  | 甲方家庭住址 |                      |
|     pic_url     |  String  |   照片路径   |                      |
| a_property_addr |  String  | 甲方财产地址 |                      |
| a_property_desc |  String  | 甲方财产描述 |                      |
|     b_name      |  String  |   乙方姓名   |                      |
|    b_id_card    |  String  |  乙方证件号  |                      |
|    b_mobile     |  String  |  乙方手机号  |                      |
|     b_email     |  String  |   乙方邮箱   |                      |
|   b_home_addr   |  String  | 乙方家庭住址 |                      |

返回示例：

```json
{
    "data": {
        "works_id": "001", // id
        "a_name": "张三", // 甲方姓名
        "a_id_card": "5002281994xxxxxxxxx", // 甲方身份证
        "a_mobile": "17725021250", // 甲方手机
        "a_home_addr": "重庆市梁平县xxxxxx", // 甲方地址
        "a_email": "825076878@qq.com", // 甲方邮箱
        "pic_url": "https://www.baidu.com/images/1.png", // 参考图
        "a_property_addr": "重庆市xxx", // 甲方财产地址
        "a_property_desc": "很好很好", // 甲方财产描述
        "b_name": "王五", // 乙方姓名
        "b_id_card": "5002281994xxxxxxxxx", // 乙方身份证
        "b_mobile": "17725021251", // 乙方手机
        "b_home_addr": "重庆市xxxxx", // 乙方地址
        "b_email": "825076878@qq.com" // 乙方邮箱
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 47.肖像权编辑接口

请求URL：

```
/api/v1/user/portrait/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，编辑肖像权信息。
```

请求参数：

|  请求参数   | 必须 | 参数类型 | 参数说明       | 备注                             |
| :---------: | :--: | :------: | :------------- | -------------------------------- |
|  works_id   |  是  |  String  | 作品id         |                                  |
|   pic_url   |  是  |  String  | 肖像参考图     |                                  |
| shoot_addre |  是  |  String  | 拍摄地         |                                  |
| shoot_time  |  是  | Integer  | 拍摄时间       |                                  |
|   b_name    |  是  |  String  | 乙方姓名       |                                  |
|  b_id_card  |  是  |  String  | 乙方身份证     |                                  |
|  b_mobile   |  是  |  String  | 乙方手机       |                                  |
| b_home_addr |  是  |  String  | 乙方地址       |                                  |
| authorizer  |  是  |  Array   | 授权人信息     | 以下字段组成对象存入authorizer中 |
|    name     |  是  |  String  | 授权人姓名     |                                  |
|   id_card   |  是  |  String  | 授权人身份证   |                                  |
|     sex     |  是  |  String  | 授权人性别     |                                  |
|   mobile    |  是  |  String  | 授权人手机     |                                  |
| home_addre  |  是  |  String  | 授权人地址     |                                  |
|  is_adult   |  是  | Boolean  | 授权人是否成年 |                                  |

返回字段：无

返回示例：

```json
{
    "data": 1,  // 1已上传，0未上传
    "msg": "Request successful.",
    "code": 0
}
```

##### 48.物产权编辑接口

请求URL：

```
/api/v1/user/property/editor
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，编辑物产权信息。
```

请求参数：

|    请求参数     | 必须 | 参数类型 | 参数说明   | 备注 |
| :-------------: | :--: | :------: | :--------- | ---- |
|    works_id     |  是  |  String  | 作品id     |      |
|     a_name      |  是  |  String  | 甲方姓名   |      |
|    a_id_card    |  是  |  String  | 甲方身份证 |      |
|    a_mobile     |  是  |  String  | 甲方手机   |      |
|     a_email     |  是  |  String  | 甲方邮箱   |      |
|   a_home_addr   |  是  |  String  | 甲方地址   |      |
| a_property_desc |  是  |  String  | 财产描述   |      |
| a_property_addr |  是  |  String  | 财产地址   |      |
|     pic_url     |  是  |  String  | 肖像参考图 |      |
|     b_name      |  是  |  String  | 乙方姓名   |      |
|    b_id_card    |  是  |  String  | 乙方身份证 |      |
|    b_mobile     |  是  |  String  | 乙方手机   |      |
|     b_email     |  是  |  String  | 乙方邮箱   |      |
|   b_home_addr   |  是  |  String  | 乙方地址   |      |

返回字段：无

返回示例：

```json
{
    "data": 1,  // 1已上传，0未上传
    "msg": "Request successful.",
    "code": 0
}
```

##### 49.图集申请上架编辑接口

请求URL：

```
/api/v1/user/altas/editor
```

请求方式：

```
PUT
```

接口说明：

```
图集上架申请。
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明 | 备注 |
| :-------: | :--: | :------: | :------- | ---- |
|    uid    |  是  |  String  | 作品id   |      |
|   title   |  是  |  String  | 标题     |      |
|   label   |  是  |  Array   | 标签     |      |
| cover_url |  是  |  String  | 封面     |      |

返回字段：无

返回示例：

```json
{
    "data": null
    "msg": "Request successful.",
    "code": 0
}
```

##### 50.摄影师认证接口

请求URL：

```
/api/v1/cameraman/auth
```

请求方式：

```
POST
```

接口说明：

```
摄影师认证
```

请求参数：

|   请求参数    | 必须 | 参数类型 | 参数说明   | 备注 |
| :-----------: | :--: | :------: | :--------- | ---- |
|     name      |  是  |  String  | 姓名       |      |
|    id_card    |  是  |  String  | 身份证号   |      |
|     addr      |  是  |  String  | 地址       |      |
| id_card_a_url |  是  |  String  | 身份证正面 |      |
| id_card_b_url |  是  |  String  | 身份证反面 |      |
|  repre_works  |  是  |  Array   | 代表作品   |      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 51.用户提现接口

请求URL：

```
/api/v1/user/withdrawal
```

请求方式：

```
POST
```

接口说明：

```
提现申请
```

请求参数：

|  请求参数  | 必须 | 参数类型 | 参数说明     |
| :--------: | :--: | :------: | :----------- |
|  channel   |  是  |  String  | 提现渠道     |
| trade_name |  是  |  String  | 提现账号姓名 |
|  trade_id  |  是  |  String  | 提现账号     |
|   amount   |  是  |  Float   | 提现金额     |

返回字段：无

返回示例：

```json
{
    "data": "将在7-14个工作日到账，届时注意查收",
    "msg": "Request successful.",
    "code": 0
}
```

##### 52.作品分享接口

请求URL：

```
/api/v1/works/share
```

请求方式：

```
POST
```

接口说明：

```
作品分享
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| works_id |  是  |  String  | 作品id   |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

#### 四、作品制作

##### 1.素材上传通用接口

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

##### 2.本地相册上传接口

请求URL：

```
/api/v1/user/local/upload
```

请求方式：

```
POST
```

接口说明：

```
用户本地图片上传。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| pic_list | 是   | Array    | 文件字段 |

返回字段：

| 返回字段    | 必须 | 字段类型 | 字段说明   |
| ----------- | ---- | -------- | ---------- |
| uid         | 是   | String   | 图片id     |
| thumb_url   | 是   | String   | 缩略图路径 |
| format      | 是   | String   | 图片格式   |
| big_pic_url | 是   | String   | 大图路径   |

返回字段：

```json
{
    "data": [{
        "thumb_url": "http://www.baidu.com/img/1.png",
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "uid": "001",
        "format": "PNG"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.素材库图片列表接口

请求URL：

```
/api/v1/user/pic/material/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数,返回图片素材库数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明       |
| :------: | :--: | :------: | :------------- |
|   page   |  是  |   Int    | 页码， 从1开始 |
|   num    |  是  |   Int    | 页数， 从1开始 |

返回字段：

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| -------- | ---- | -------- | -------- |
| uid      | 是   | String   | 图片id   |
| pic_url  | 是   | String   | 图片路径 |
| label    | 否   | Array    | 标签     |
| title    | 否   | String   | 标题     |
| format   | 是   | String   | 格式     |

返回示例：

```json
{
    "data": [{
        "pic_url": "http://www.baidu.com/img/1.png",
        "uid": "001",
        "label": ["5G", "科技"],
        "title": "华为5g",
        "format": "png"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.历史标签接口

请求URL：

```
/api/v1/user/histroy/label
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数,返回用户历史标签。
```

请求参数：无

返回字段：无

返回示例：

```json
{
  "data": [
    "科技",
    "华为",
    "中国",
	...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 5.图集搜索标签接口

请求URL：

```
/api/v1/user/label/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数,返回模糊匹配标签。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回字段：无

返回示例：

```json
{
  "data": [
    "科技",
    "华为",
    "中国",
	...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 6.创作图片接口

请求URL：

```
/api/v1/user/creation/pic
```

请求方式：

```
POST
```

接口说明：

```
制作图片作品
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                           |
| :------: | :--: | :------: | :------- | ------------------------------ |
| pic_list |  是  |  Array   | 外层结构 | 以下字段组成对象放入pic_list中 |
|  title   |  是  |  String  | 标题     |                                |
|  label   |  是  |  Array   | 标签     |                                |
|   uid    |  是  |  String  | 图片id   |                                |
|  format  |  是  |  String  | 图片格式 |                                |

返回字段: 

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| -------- | ---- | -------- | -------- |
| pic_id   | 是   | String   | 图片id   |
| works_id | 是   | String   | 作品id   |

返回示例：

```json
{
  "data": {
      "pic_id": "001",
      "works_id": "002"
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 7.创作图集接口

请求URL：

```
/api/v1/user/creation/atlas
```

请求方式：

```
POST
```

接口说明：

```
制作图集作品
```

请求参数：

|  请求参数   | 必须 | 参数类型 | 参数说明 | 备注 |
| :---------: | :--: | :------: | :------- | ---- |
|  cover_url  |  是  |  String  | 封面     |      |
|    title    |  是  |  String  | 标题     |      |
|    label    |  是  |  Array   | 标签     |      |
| pic_id_list |  是  |  Array   | 图片id   |      |

返回字段: 

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| -------- | ---- | -------- | -------- |
| pic_id   | 是   | String   | 图片id   |
| works_id | 是   | String   | 作品id   |

返回示例：

```json
{
  "data": {
      "pic_id": "001",
      "works_id": "002"
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 8.音频素材上传接口

请求URL：

```
/api/v1/user/audio/common
```

请求方式：

```
POST
```

接口说明：

```
音频、视频通用接口。
```

请求参数：

| 请求参数   | 必须 | 参数类型 | 参数说明 |
| ---------- | ---- | -------- | -------- |
| audio_list | 是   | Array    | 文件字段 |

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
        "file_path": "http://www.baidu.com/mp3/1.mp3",
        "size": 250,
        "file_extension": "mp3",
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.影集图片上传接口

请求URL：

```
/api/v1/video/pic/upload
```

请求方式：

```
POST
```

接口说明：

```
影集图片上传。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| -------- | ---- | -------- | -------- |
| pic_list | 是   | Array    | 文件字段 |

返回字段：

| 返回字段    | 必须 | 字段类型 | 字段说明   |
| ----------- | ---- | -------- | ---------- |
| uid         | 是   | String   | 图片id     |
| thumb_url   | 是   | String   | 缩略图路径 |
| format      | 是   | String   | 图片格式   |
| big_pic_url | 是   | String   | 大图路径   |

返回字段：

```json
{
    "data": [{
        "thumb_url": "http://www.baidu.com/img/1.png",
        "big_pic_url": "http://www.baidu.com/img/1.png",
        "uid": "001",
        "format": "PNG"
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 10.影集标签搜索接口

请求URL：

```
/api/v1/video/label/search
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数,返回模糊匹配标签。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 |
| :------: | :--: | :------: | :------- |
| keyword  |  是  |  String  | 关键词   |

返回字段：无

返回示例：

```json
{
  "data": [
    "科技",
    "华为",
    "中国",
	...
  ],
  "code": 0,
  "msg": "Request successful."
}
```

##### 11.创作影集接口

请求URL：

```
/api/v1/user/video/create
```

请求方式：

```
POST
```

接口说明：

```
制作影集作品
```

请求参数：

|  请求参数   | 必须 | 参数类型 | 参数说明 | 备注 |
| :---------: | :--: | :------: | :------- | ---- |
|  cover_url  |  是  |  String  | 封面     |      |
|    title    |  是  |  String  | 标题     |      |
|    label    |  是  |  Array   | 标签     |      |
| pic_id_list |  是  |  Array   | 图片id   |      |
| me_works_id |  是  |  String  | me作品id |      |

返回字段: 

| 返回字段 | 必须 | 字段类型 | 字段说明 |
| -------- | ---- | -------- | -------- |
| pic_id   | 是   | String   | 图片id   |
| works_id | 是   | String   | 作品id   |

返回示例：

```json
{
  "data": {
      "pic_id": "001",
      "works_id": "002"
  },
  "code": 0,
  "msg": "Request successful."
}
```

##### 12.创作图文接口

请求URL：

```
/api/v1/user/creation/article
```

请求方式：

```
POST
```

接口说明：

```
制作图文作品
```

请求参数：

| 请求参数  | 必须 | 参数类型 | 参数说明 | 备注 |
| :-------: | :--: | :------: | :------- | ---- |
|    uid    |  否  |  String  | 作品id   |      |
| cover_url |  是  |  String  | 封面     |      |
|   title   |  是  |  String  | 标题     |      |
|  content  |  是  |  String  | 内容     |      |

返回字段: 无

返回示例：

```json
{
  "data": "001", // 制作时为图文id,编辑时为null
  "code": 0,
  "msg": "Request successful."
}
```

##### 

#### 五、订单管理

##### 1.加入购物车接口

请求URL：

```
/api/v1/car/add
```

请求方式：

```
POST
```

接口说明：

```
加入购物车
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注                     |
| -------- | ---- | -------- | -------- | ------------------------ |
| works_id | 是   | String   | 作品id   |                          |
| price    | 是   | Float    | 价格     |                          |
| is_buy   | 是   | Boolean  | 是否购买 | true购买 false加入购物车 |

返回字段：无

返回示例：

```json
{
    "data": "1245145121412115421", // 当is_busy返回true才有订单号返回
    "msg": "Request successful.",
    "code": 0
}
```

##### 2.购物车列表接口

请求URL：

```
/api/v1/car/list
```

请求方式：

```
GET
```

接口说明：

```
获取购物车列表
```

请求参数：无

返回字段：

| 返回字段  | 必须 | 字段类型 | 字段说明 |
| --------- | ---- | -------- | -------- |
| uid       | 是   | String   | id       |
| title     | 是   | String   | 标题     |
| spec      | 是   | String   | 规格     |
| currency  | 是   | String   | 币种     |
| price     | 是   | Float    | 价格     |
| thumb_url | 是   | String   | 缩略图   |

返回示例：

```json
{
    "data": [{
        	"uid": "001",
        	"title": "哈哈",
        	"spec": "S",
        	"currency": "￥",
        	"thumb_url": "http://www.baidu.com/img/1.png",
        	"price": 55.0
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 3.购物车合并订单接口

请求URL：

```
/api/v1/car/merge
```

请求方式：

```
PUT
```

接口说明：

```
合并购物车订单
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明     | 备注 |
| -------- | ---- | -------- | ------------ | ---- |
| uid_list | 是   | Array    | 购物车商品id |      |

返回字段：

| 返回字段     | 必须 | 字段类型 | 字段说明                   |
| ------------ | ---- | -------- | -------------------------- |
| order        | 是   | String   | 订单                       |
| balance      | 是   | Float    | 余额                       |
| create_time  | 是   | Integer  | 订单创建时间               |
| total_amount | 是   | Float    | 总金额                     |
| works_item   | 是   | Array    | 图片信息                   |
| uid          | 是   | String   | 唯一标识【属于works_item】 |
| title        | 是   | String   | 标题【属于works_item】     |
| spec         | 是   | String   | 规格【属于works_item】     |
| currency     | 是   | String   | 币种【属于works_item】     |
| price        | 是   | Float    | 价格【属于works_item】     |
| thumb_url    | 是   | String   | 缩略图【属于works_item】   |

返回示例：

```json
{
    "data": {
        "order": "0001",
        "create_time": 1596088929000,
        "total_amount": 550.0,
        "works_item": [{
            	"uid": "001",
            	"title": "哈哈",
            	"spec": "M",
            	"currency": "￥",
            	"price": 55.0,
            	"thumb_url": "http://www.baidu.com/img/1.png"
        	},
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 4.订单列表接口

请求URL：

```
/api/v1/order/list
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户订单数据。
```

请求参数：

| 请求参数    | 必须 | 参数类型 | 参数说明 | 备注                 |
| ----------- | ---- | -------- | -------- | -------------------- |
| num         | 是   | Integer  | 页数     |                      |
| page        | 是   | Integer  | 页码     |                      |
| is_complete | 是   | Boolean  | 是否完成 | true完成 false待付款 |

返回字段：

| 返回字段     | 必须 | 字段类型 | 字段说明                                 |
| ------------ | ---- | -------- | ---------------------------------------- |
| order        | 是   | String   | 订单                                     |
| balance      | 是   | Float    | 余额                                     |
| create_time  | 是   | Integer  | 订单创建时间                             |
| delta_time   | 是   | Integer  | 订单剩余时间/秒                          |
| total_amount | 是   | Float    | 总金额                                   |
| works_item   | 是   | Array    | 图片信息                                 |
| state        | 是   | Integer  | -1取消，0正常，1未付款，2已付款，3已退款 |
| uid          | 是   | String   | 唯一标识【属于works_item】               |
| title        | 是   | String   | 标题【属于works_item】                   |
| spec         | 是   | String   | 规格【属于works_item】                   |
| currency     | 是   | String   | 币种【属于works_item】                   |
| price        | 是   | Float    | 价格【属于works_item】                   |
| thumb_url    | 是   | String   | 缩略图【属于works_item】                 |

返回示例：

```json
{
    "data": [{
        	"order": "001",
        	"total_amount": 250.0,
        	"create_time": 1596088929000,
        	"delta_time": 1800,
        	"state": 1,
        	"works_item": [{
                	"uid": "0001",
                	"title": "哈哈哈",
                	"spec": "S",
                	"currency": "￥",
                	"price": 25.0,
                	"thumb_url": "http://wwww.baidu.com/img/1.png"
            	},
                ...
            ]
    	},
        ...
    ],
    "msg": "Request successful.",
    "code": 0
}
```

##### 5.取消订单接口

请求URL：

```
/api/v1/order/state
```

请求方式：

```
PUT
```

接口说明：

```
根据请求参数，取消订单。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| -------- | ---- | -------- | -------- | ---- |
| order_id | 是   | String   | 订单id   |      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

##### 6.订单详情

请求URL：

```
/api/v1/order/detail
```

请求方式：

```
GET
```

接口说明：

```
根据请求参数，返回用户订单数据。
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| -------- | ---- | -------- | -------- | ---- |
| order    | 是   | String   | 订单号   |      |

返回字段：

| 返回字段     | 必须 | 字段类型 | 字段说明                                 |
| ------------ | ---- | -------- | ---------------------------------------- |
| order        | 是   | String   | 订单                                     |
| balance      | 是   | Float    | 余额                                     |
| create_time  | 是   | Integer  | 订单创建时间                             |
| delta_time   | 是   | Integer  | 订单剩余时间/ 秒                         |
| total_amount | 是   | Float    | 总金额                                   |
| works_item   | 是   | Array    | 图片信息                                 |
| state        | 是   | Integer  | -1取消，0正常，1未付款，2已付款，3已退款 |
| uid          | 是   | String   | 唯一标识【属于works_item】               |
| title        | 是   | String   | 标题【属于works_item】                   |
| spec         | 是   | String   | 规格【属于works_item】                   |
| currency     | 是   | String   | 币种【属于works_item】                   |
| price        | 是   | Float    | 价格【属于works_item】                   |
| thumb_url    | 是   | String   | 缩略图【属于works_item】                 |

返回示例：

```json
{
    "data": {
        "order": "001",
        "total_amount": 250.0,
        "create_time": 1596088929000,
        "delta_time": 1800,
        "state": 1,
        "works_item": [{
                "uid": "0001",
                "title": "哈哈哈",
                "spec": "S",
                "currency": "￥",
                "price": 25.0,
                "thumb_url": "http://wwww.baidu.com/img/1.png"
            },
            ...
        ]
    },
    "msg": "Request successful.",
    "code": 0
}
```

##### 7.删除购物车接口

请求URL：

```
/api/v1/car/delete
```

请求方式：

```
DELETE
```

接口说明：

```
删除购物车
```

请求参数：

| 请求参数 | 必须 | 参数类型 | 参数说明 | 备注 |
| -------- | ---- | -------- | -------- | ---- |
| uid_list | 是   | Array    | 订单id   |      |

返回字段：无

返回示例：

```json
{
    "data": null, // 当is_busy返回true才有订单号返回
    "msg": "Request successful.",
    "code": 0
}
```

##### 8.订单支付

请求URL：

```
/api/v1/order/payment
```

请求方式：

```
POST
```

接口说明：

```
订单支付
```

请求参数：

| 请求参数     | 必须 | 参数类型 | 参数说明 | 备注             |
| ------------ | ---- | -------- | -------- | ---------------- |
| order        | 是   | String   | 订单id   |                  |
| channel      | 是   | String   | 渠道     | 余额 支付宝 微信 |
| total_amount | 是   | Float    | 订单总额 |                  |

返回字段：

返回示例：

```json
{
    "data": 'app_id=2015052600090779&biz_content={"timeout_express":"30m","product_code":"QUICK_MSECURITY_PAY","total_amount":"0.01","subject":"1","body":"我是测试数据","out_trade_no":"IQJZSRC1YMQB5HU"}&charset=utf-8&format=json&method=alipay.trade.app.pay&notify_url=http://domain.merchant.com/payment_notify&sign_type=RSA2&timestamp=2016-08-25 20:26:31&version=1.0&sign=cYmuUnKi5QdBsoZEAbMXVMmRWjsuUj+y48A2DvWAVVBuYkiBj13CFDHu2vZQvmOfkjE0YqCUQE04kqm9Xg3tIX8tPeIGIFtsIyp/M45w1ZsDOiduBbduGfRo1XRsvAyVAv2hCrBLLrDI5Vi7uZZ77Lo5J0PpUUWwyQGt0M4cj8g=', // 支付宝 微信为响应的xml字符串
    "msg": "Request successful.",
    "code": 0
}
```

##### 9.支付成功后app回调

请求URL：

```
/api/v1/app/callback
```

请求方式：

```
POST
```

接口说明：

```
支付成功后回调
```

请求参数：

| 请求参数     | 必须 | 参数类型 | 参数说明 | 备注 |
| ------------ | ---- | -------- | -------- | ---- |
| order        | 是   | String   | 订单id   |      |
| total_amount | 是   | Float    | 订单总额 |      |

返回字段：无

返回示例：

```json
{
    "data": null,
    "msg": "Request successful.",
    "code": 0
}
```

