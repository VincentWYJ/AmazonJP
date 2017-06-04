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


# 正则表达式
nav_tag_g = '_nav_'
delete_tag_g = re.compile('/ref=zg_.*')


# 全局变量
id_g = 1
url_g = 'https://www.amazon.co.jp/gp/bestsellers/'
timeout_open_g = 10


# 获取5个类型信息：畅销，新品，人气，心愿，礼物
# 数据库中存储内容：id，name，url，base_id
def getFiveTypeInfo(url_arg):
    global id_g
    try:
        request = urllib.request.Request(url_arg, postdata, headers)
        response = opener.open(request, timeout=timeout_open_g)
    except Exception as e:
        print(url_arg + ' open failed.')
        print(e)
    else:
        cookie.save(ignore_discard=True, ignore_expires=True)

        try:
            bs_obj = BeautifulSoup(response.read(), 'html.parser')
        except Exception as e:
            print(url_arg + ' read failed.')
            print(e)
        else:
            # 排除script脚本
            for script in bs_obj(['script', 'style']):
                script.extract()

            node = bs_obj.find('', {'id': 'zg_tabs'})
            if node and len(node) > 0:
                base_id = 0
                info_list = []
                url_list = []
                for item in node.find_all('a'):
                    info = []
                    # name = translate1(item.get_text().strip())
                    name = item.get_text().strip()
                    url = item.get('href').strip()
                    url = delete_tag_g.sub('', url)
                    info.append(id_g)
                    info.append(name)
                    info.append(url)
                    info.append(base_id)
                    print(info)
                    insertCategoryInfo(info)
                    id_g += 1
                    info_list.append(info)
                    url_list.append(url)

                if len(info_list) > 0:
                    getCategoryInfo(info_list, url_list)


# 获取某个类型下的分类信息
# 数据库中存储内容：id，name，url，base_id
def getCategoryInfo(info_list_arg, url_list_arg):
    global id_g
    info_list = []
    url_list = []
    for info in info_list_arg:
        try:
            request = urllib.request.Request(info[2], postdata, headers)
            response = opener.open(request, timeout=timeout_open_g)
        except Exception as e:
            print(info[2] + ' open failed.')
            print(e)
        else:
            cookie.save(ignore_discard=True, ignore_expires=True)

            try:
                bs_obj = BeautifulSoup(response.read(), 'html.parser')
            except Exception as e:
                print(info[2] + ' read failed.')
                print(e)
            else:
                # 排除script脚本
                for script in bs_obj(['script', 'style']):
                    script.extract()

                node = bs_obj.find('', {'id': 'zg_browseRoot'})
                if node and len(node) > 0:
                    base_id = info[0]
                    for item in node.find_all('a'):
                        url = item.get('href').strip()
                        if nav_tag_g not in url:
                            continue
                        url = delete_tag_g.sub('', url)
                        if url in url_list_arg:
                            continue
                        info = []
                        # name = translate1(item.get_text().strip())
                        name = item.get_text().strip()
                        info.append(id_g)
                        info.append(name)
                        info.append(url)
                        info.append(base_id)
                        print(info)
                        insertCategoryInfo(info)
                        id_g += 1
                        info_list.append(info)
                        url_list.append(url)

    if len(info_list) > 0:
        getCategoryInfo(info_list, url_list)


# 添加分类信息到数据库
def insertCategoryInfo(info):
    insert_code = 'insert into category values(%s, %s, %s, %s)'
    cur.execute(insert_code, (info[0], info[1], info[2], info[3]))
    conn.commit()


# 连接数据库
conn = pymysql.connect(host='amazondata.mysql.rds.aliyuncs.com', user='root', passwd='1qaz2wsx@12',
                       db='amazondata', port=3306, charset='utf8')
cur = conn.cursor()


cur.execute("delete from category")
conn.commit()


# getFiveTypeInfo方法测试
getFiveTypeInfo(url_g)
# getCategoryInfo([[0, '', 'https://www.amazon.co.jp/gp/bestsellers/mobile-apps/2386858051', 3]], [])


# 断开数据库
cur.close()
conn.close()