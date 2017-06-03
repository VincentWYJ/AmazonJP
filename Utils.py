# -*- coding: utf-8 -*-


# 1----------------模块导入
import re
import urllib.parse, urllib.request
from HandleJs import Py4Js
import hashlib
import urllib
import random
import json
from PIL import Image
import Levenshtein
import os

appid = '20170525000049178'
secretKey = 'CJ3amNC3iyx4pR3AnmZs'


js = Py4Js()


def open_url(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url = url, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return data


# 2----------------翻译方法
def translate1(content, f='ja', t='zh-cn'):
    if len(content) > 4891:
        print('Content is too long.')
        return

    tk = js.getTk(content)

    content = urllib.parse.quote(content)

    url = 'http://translate.google.cn/translate_a/single?client=t&sl=%s&tl=%s&hl=%s&dt=at&dt=bd&dt=ex&dt=ld&dt=md&' \
          'dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&' \
          'q=%s' % (f, t, t, tk, content)

    result = open_url(url)

    end = result.find('",')
    if end > 4:
        return result[4:end]
    else:
        return ''

def translate(q):
    # http://api.fanyi.baidu.com/api/trans/product/index
    appid = '20170525000049178' # 百度API的 APPid
    secretKey = 'CJ3amNC3iyx4pR3AnmZs'# 百度API的 secretKey
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    fromLang = 'jp'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        # response是HTTPResponse对象
        resultPage = urllib.request.urlopen(myurl)
        resultJason = resultPage.read().decode('utf-8')  # 取得翻译的结果，翻译的结果是json格式
        jsdata = json.loads(resultJason)  # 将json格式的结果转换成Python的字典结构
        tranlate_result = str(jsdata["trans_result"][0]["dst"])  # 取得翻译后的文本结果
    except Exception as e:
        print
        e
    return tranlate_result

# 2.1 方法测试
# content = input('输入待翻译内容：')
# print(translate(content))


# 2----------------翻译方法
# def translate(text, f='ja', t='zh-cn'):
#     url = 'http://translate.google.cn'
#     values = {'hl': 'zh-CN', 'ie': 'UTF-8', 'text': text, 'langpair': '%s|%s' % (f, t)}
#     data = urllib.parse.urlencode(values)
#     req = urllib.request.Request(url + '?' + data)
#     user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
#                  r'Chrome/44.0.2403.157 Safari/537.36'
#     req.add_header('User-Agent', user_agent)
#     response = urllib.request.urlopen(req)
#     html = response.read()
#     p = re.compile(r'(?<=TRANSLATED_TEXT=).*?;')
#     m = p.search(html.decode())
#     text = m.group(0).strip(';').strip('\'')
#
#     return text

# 2.1 方法测试
# print(translate('Hello'))


# 3----------------添加换行打印方法
def println(text):
    print(str(text) + '\n')


def ems_fee(weight):
    if weight <= 500:
        ems_price = 1400
    elif weight < 1000:
        ems_price = 1400 + int((weight - 500)/100) *140
    elif weight == 1000:
        ems_price = 2100
    elif weight < 2000:
        ems_price = 2100 + int((weight - 1000) / 250) * 300
    elif weight == 2000:
        ems_price = 3300
    elif weight < 6000:
        ems_price = 3300 + int((weight - 2000) / 500) * 500
    elif weight == 6000:
        ems_price = 7300
    elif weight < 30000:
        ems_price = 7300 + int((weight - 6000) / 1000) * 800
    elif weight == 30000:
        ems_price = 26500
    else:
        ems_price = 2650000
    return ems_price

#This module can classify the image by histogram.
#This method is easy for someone who is a beginner in Image classification.
#Size' is parameter what the image will resize to it.It's 256 * 256 when it default.
#This function return the similarity rate betweene 'image1' and 'image2'
def compare_image(image_path1,image_path2,size = (256,256)):
    image1 = Image.open(image_path1)
    image1 = image1.resize(size).convert("RGB")
    g = image1.histogram()
    image2 = Image.open(image_path2)
    image2 = image2.resize(size).convert("RGB")
    s = image2.histogram()
    assert len(g) == len(s), "error"

    data = []

    for index in range(0, len(g)):
        if g[index] != s[index]:
            data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
        else:
            data.append(1)

    ratio = sum(data) / len(g)
    return ratio

def compare_str(str1, str2):
    similar_index = Levenshtein.jaro(str1, str2)
    return similar_index

# 3.1 方法测试
# println('Hello')


# /usr/bin/env python
# coding=utf8






