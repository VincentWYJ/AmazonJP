# -*- coding: utf-8 -*-


# 1----------------模块导入
import re
import urllib.parse, urllib.request
from urllib import error
from urllib import parse
import json


# 2----------------翻译方法
def translate(text, f='ja', t='zh-cn'):
    url = 'http://translate.google.cn'
    values = {'hl': 'zh-CN', 'ie': 'UTF-8', 'text': text, 'langpair': '%s|%s' % (f, t)}
    data = urllib.parse.urlencode(values)
    req = urllib.request.Request(url + '?' + data)
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 r'Chrome/44.0.2403.157 Safari/537.36'
    req.add_header('User-Agent', user_agent)
    response = urllib.request.urlopen(req)
    html = response.read()
    p = re.compile(r'(?<=TRANSLATED_TEXT=).*?;')
    m = p.search(html.decode())
    text = m.group(0).strip(';').strip('\'')

    return text


# 2.1 方法测试
# print(translate('Hello'))




# 3----------------添加换行打印方法
def println(text):
    print(str(text) + '\n')

# 4----------------添加urlretrieve 函数的回调函数
def cbk(a, b, c):
    '''回调函数
    @a: 已经下载的数据块
    @b: 数据块的大小
    @c: 远程文件的大小
    '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    println(u'%.2f%%' % per)

# 5---------------添加获取网路目标的函数
def Get_net_object(url_in,filename_out):
    try:
        urllib.request.urlretrieve(url_in, filename_out, cbk)
    except error.HTTPError as e:
        flag = False
        print("HTTPError")
        print(e.code)
    except error.URLError as e:
        flag = False
        print("URLError")
        print(e.reason)
    else:
        flag = True

    return flag

# 6---------------添加有道词典的翻译程序，备份用
def youdao_tanslate(translate_input):
    Request_URL = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=https://www.baidu.com/link'
    # 创建Form_Data字典，存储上图的Form Data
    Form_Data = {}
    Form_Data['type'] = 'AUTO'
    Form_Data['i'] = translate_input
    Form_Data['doctype'] = 'json'
    Form_Data['xmlVersion'] = '1.8'
    Form_Data['keyfrom'] = 'fanyi.web'
    Form_Data['ue'] = 'ue:UTF-8'
    Form_Data['action'] = 'FY_BY_CLICKBUTTON'
    #使用urlencode方法转换标准格式
    data = parse.urlencode(Form_Data).encode('utf-8')
        # 传递Request对象和转换完格式的数据
    response = urllib.request.urlopen(Request_URL, data)
        # 读取信息并解码
    html = response.read().decode('utf-8')
        # 使用JSON
    translate_results = json.loads(html)
        # 找到翻译结果
    translate_results = translate_results['translateResult'][0][0]['tgt']

    return(translate_results)


