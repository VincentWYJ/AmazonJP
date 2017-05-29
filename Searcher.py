# -*- coding: utf-8 -*-

#0： 每天小时更新一次
#1:  获取https://www.amazon.co.jp/gp/bestsellers/
#2： 获取所有类目
#3： 获取子类目
#4： 获取最小分类
#5： 获取销售排行榜前100名的商品
#6： 获取新品排行榜前100名的商品
#7： 获取心愿排行榜前100名的商品
#8： 获取礼品排行榜前100名的商品
#7： 存入数据库（远程数据库，在阿里云？？）
#8： 分析数据变化



# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import threading
import http.cookiejar
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
from Utils import *
from GenImage import *
from GenDescription import *
from GenWirelessDesc import *


# 2 ----------------常量定义
# 汇率(API)
exchange_rate = 15
# 利润率(可调)
profit_rate = 0.3
# 包装重量(克)
packet_weight = 150
# 产地后缀
title_append = u'日本制造'
# 描述头
description_start = 'xxx'
# 描述尾
description_end = 'yyy'
# 模拟浏览器登录
values = {'email': 'wyjxjm@126.com', 'password': '324712', 'submit': 'Login'}
postdata = urllib.parse.urlencode(values).encode()
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 ' \
             r'Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
cookie_filename = 'cookie.txt'
cookie = http.cookiejar.MozillaCookieJar(cookie_filename)
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
# 正则表达式
delete_img_head_reg = re.compile('<img')
delete_html_head_reg = re.compile('<[^>]*>')
delete_n_reg = re.compile('\n*')
reg_replace = re.compile('\n|\'|[|]|【|】')



# 3 ----------------数据获取
def searcher(html_url):

    # 提取网页内容
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
    except:
        print('open html failed **************************')
    else:
        print(u'获取TOP100列表: ')
        cookie.save(ignore_discard=True, ignore_expires=True)
        bs_obj = BeautifulSoup(html_file.read(), 'html.parser')

        # 排除script脚本*************************************
        for script in bs_obj(['script', 'style']):
            script.extract()
        # 获取子类目名称和链接
        category_name_root = []
        category_link_root = []
        category_node = bs_obj.find('', {'id': 'zg_browseRoot'})
        if category_node and len(category_node) > 0:
            for zg_selected in category_node.find_all('span', {'class': 'zg_selected'}): #find the current selected item
                if zg_selected.parent.next_sibling.find('ul'): # if selected item 's parent have ul sibling, its have children
                    for category_item in zg_selected.parent.next_sibling.children:
                        if category_item != '\n':
                            category_name = translate(category_item.get_text().strip().replace('\n', ''))
                            print(category_name)
                            category_link = category_item.get('href').strip().replace('\n', '')
                            print(category_link)



                else: # else without children


        else:




        category_node = bs_obj.find('', {'id': 'zg_browseRoot'})
        if category_node and len(category_node) > 0:
            for category_item in category_node.find_all('a'):
                if category_item != '\n':
                    category_name = translate(category_item.get_text().strip().replace('\n', ''))
                    print(category_name)
                    category_link = category_item.get('href').strip().replace('\n', '')
                    print(category_link)






if __name__ == '__main__':
    html_url = 'https://www.amazon.co.jp/gp/bestsellers/'
    searcher(html_url)