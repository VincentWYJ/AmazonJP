# -*- coding: utf-8 -*-


# 1----------------模块导入
import re
import urllib.parse, urllib.request
from HandleJs import Py4Js
import hashlib
import urllib
import random
import json

appid = '20170525000049178'
secretKey = 'CJ3amNC3iyx4pR3AnmZs'


js = Py4Js()


def open_url(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url = url,headers=headers)
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

# 3.1 方法测试
# println('Hello')


# /usr/bin/env python
# coding=utf8






