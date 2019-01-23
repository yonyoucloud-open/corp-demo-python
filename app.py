from flask import Flask
from flask import request
from crypto import sign, crypto
import time
import requests
import json

app = Flask(__name__)

# 自建应用的 app key
app_key = '< your app key >'
# 自建应用的 app secret
app_secret = '< your app secret >'

app_sign = sign.Sign(app_key, app_secret)
app_crypto = crypto.Crypto(app_key, app_secret)


@app.route('/')
def hello_world():
    return 'Hello World! </br> app_key: %s, app_secret: %s' % (app_key, app_secret)


@app.route('/getAccessToken')
def get_access_token():
    """
    获取 access_token
    :return: 开放平台返回的包含 access_token 的原始消息体
    """
    timestamp = int(time.time() * 1000)
    param_dict = {'appKey': app_key, 'timestamp': timestamp}
    signature = app_sign.sign(param_dict)
    param_dict['signature'] = signature
    res = requests.get('https://open.yonyoucloud.com/open-auth/selfAppAuth/getAccessToken', param_dict)
    return res.content


@app.route('/eventPush', methods=['POST'])
def push_event():
    """
    接收开放平台推送的数据变动事件，开放平台会直接调用该接口，推送数据变动的 id，超时时间 5s，复杂耗时业务推荐异步处理
    :return: 处理成功返回 'success'，否则开放平台判定处理失败，会重试推送，直到 24 小时
    """
    request_json = request.get_json()

    # 解密验签
    decoded = app_crypto.decode_dict_with_validate(request_json)
    print(decoded)
    event = json.loads(decoded)
    event_type = event['type']

    # 根据事件类型进行业务处理，开放平台投递超时时间 5s，复杂业务推荐异步处理，超时视为投递失败，会进行重试
    if 'CHECK_URL' == event_type:
        print('事件类型: %s, 说明: 检查事件推送回调地址' % event_type)
    elif 'STAFF_ADD' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下员工增加, 员工变更 id: %s' % (event_type, event['tenantId'], event['staffId']))
    elif 'STAFF_UPDATE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下员工更改, 员工变更 id: %s' % (event_type, event['tenantId'], event['staffId']))
    elif 'STAFF_ENABLE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下员工启用, 员工变更 id: %s' % (event_type, event['tenantId'], event['staffId']))
    elif 'STAFF_DISABLE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下员工停用, 员工变更 id: %s' % (event_type, event['tenantId'], event['staffId']))
    elif 'STAFF_DELETE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下员工删除, 员工变更 id: %s' % (event_type, event['tenantId'], event['staffId']))
    elif 'DEPT_ADD' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下部门创建, 部门变更 id: %s' % (event_type, event['tenantId'], event['deptId']))
    elif 'DEPT_UPDATE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下部门修改, 部门变更 id: %s' % (event_type, event['tenantId'], event['deptId']))
    elif 'DEPT_ENABLE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下部门启用, 部门变更 id: %s' % (event_type, event['tenantId'], event['deptId']))
    elif 'DEPT_DISABLE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下部门停用, 部门变更 id: %s' % (event_type, event['tenantId'], event['deptId']))
    elif 'DEPT_DELETE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下部门删除, 部门变更 id: %s' % (event_type, event['tenantId'], event['deptId']))
    elif 'USER_ADD' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下用户增加, 用户 id: %s' % (event_type, event['tenantId'], event['userId']))
    elif 'USER_DELETE' == event_type:
        print('事件类型: %s, 说明: 租户 %s 下用户移除, 用户 id: %s' % (event_type, event['tenantId'], event['userId']))

    # 处理成功返回 'success'，否则开放平台认为投递失败，会重试投递直到 24 小时
    return 'success'


if __name__ == '__main__':
    app.run()
