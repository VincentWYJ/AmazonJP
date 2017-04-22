# -*- coding: utf-8 -*-


# 1----------------模块导入
import re
import urllib.parse, urllib.request


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

# 3.1 方法测试
# println('Hello')