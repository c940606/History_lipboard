
# encoding:utf-8

import requests
import base64

'''
通用文字识别
'''

request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
# 二进制方式打开图片文件
f = open(r'img.png', 'rb')
img = base64.b64encode(f.read())

params = {"image":img}
access_token = '24.6873eeb6b482f61bc9106bde275aaa17.2592000.1663667607.282335-23993393'
request_url = request_url + "?access_token=" + access_token
headers = {'content-type': 'application/x-www-form-urlencoded'}
response = requests.post(request_url, data=params, headers=headers)
if response:
    print (response.json())