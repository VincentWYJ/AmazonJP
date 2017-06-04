# -*- coding: utf-8 -*-


# 模块导入
import pymysql
import http.cookiejar
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
from Utils import *


# 浏览器登录模拟
values = {'email': 'wyjxjm@126.com', 'password': '324712', 'submit': 'Login'}
postdata = urllib.parse.urlencode(values).encode()
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 ' \
             r'Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
cookie_filename = 'cookie.txt'
cookie = http.cookiejar.MozillaCookieJar(cookie_filename)
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)


# 全局变量
asin_filter_g = '/dp/'
id_g = 1
timeout_open_g = 10


# 获取某类别下Top 100 items
def getTop100Items(info_arg):
    try:
        request = urllib.request.Request(info_arg[2], postdata, headers)
        response = opener.open(request, timeout=timeout_open_g)
    except Exception as e:
        print(info_arg[2] + ' open failed.')
        print(e)
    else:
        cookie.save(ignore_discard=True, ignore_expires=True)

        try:
            bs_obj = BeautifulSoup(response.read(), 'html.parser')
        except Exception as e:
            print(info_arg[2] + ' read failed.')
            print(e)
        else:
            # 排除script脚本
            for script in bs_obj(['script', 'style']):
                script.extract()

            node = bs_obj.find('', {'id': 'zg_paginationWrapper'})
            if node and len(node) > 0:
                url_list = []
                for item in node.find_all('a'):
                    url = item.get('href').strip()
                    url_list.append(url)

                if len(url_list) > 0:
                    getSub20Items(url_list, info_arg[0])


# 分5次获取Top 100 items, 每次20条
def getSub20Items(url_list_arg, base_id_arg):
    global id_g
    rank_value = 1
    for url in url_list_arg:
        if rank_value == 101:
            rank_value = 1
        asin_list = []
        try:
            request = urllib.request.Request(url, postdata, headers)
            response = opener.open(request, timeout=timeout_open_g)
        except Exception as e:
            print(url + ' open failed.')
            print(e)
        else:
            cookie.save(ignore_discard=True, ignore_expires=True)

            try:
                bs_obj = BeautifulSoup(response.read(), 'html.parser')
            except Exception as e:
                print(url + ' read failed.')
                print(e)
            else:
                # 排除script脚本
                for script in bs_obj(['script', 'style']):
                    script.extract()

                node = bs_obj.find('', {'id': 'zg_critical'})
                if node and len(node) > 0:
                    for item in node.find_all('a'):
                        url = item.get('href').strip()
                        if asin_filter_g not in url:
                            continue
                        asin = url[url.find(asin_filter_g) + 4:url.rfind('/')]
                        if asin in asin_list:
                            continue
                        info = []
                        # name = translate1(item.get_text().strip())
                        name = item.get_text().strip()
                        info.append(id_g)
                        info.append(base_id_arg)
                        info.append(rank_value)
                        info.append(asin)
                        info.append(rank_value)
                        insertItemInfo(info)
                        print(info)
                        id_g += 1
                        rank_value += 1
                        asin_list.append(asin)

                node = bs_obj.find('', {'id': 'zg_nonCritical'})
                if node and len(node) > 0:
                    for item in node.find_all('a'):
                        url = item.get('href').strip()
                        if asin_filter_g not in url:
                            continue
                        asin = url[url.find(asin_filter_g) + 4:url.rfind('/')]
                        if asin in asin_list:
                            continue
                        info = []
                        # name = translate1(item.get_text().strip())
                        # name = item.get_text().strip()
                        info.append(id_g)
                        info.append(base_id_arg)
                        info.append(rank_value)
                        info.append(asin)
                        info.append(rank_value)
                        insertItemInfo(info)
                        print(info)
                        id_g += 1
                        rank_value += 1
                        asin_list.append(asin)


# 添加分类信息到数据库
def insertItemInfo(info):
    insert_code = 'insert into top100 values(%s, %s, %s, %s, %s)'
    cur.execute(insert_code, (info[0], info[1], info[2], info[3], info[4]))
    conn.commit()


# 连接数据库
conn = pymysql.connect(host='amazondata.mysql.rds.aliyuncs.com', user='root', passwd='1qaz2wsx@12',
                       db='amazondata', port=3306, charset='utf8')
cur = conn.cursor()


cur.execute('delete from top100')
conn.commit()


cur.execute('select * from category')
conn.commit()


category_info_list = cur.fetchall()
for category_info in category_info_list[5:]:
    getTop100Items(category_info)


# 断开数据库
cur.close()
conn.close()