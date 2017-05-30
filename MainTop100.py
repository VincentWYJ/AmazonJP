# -*- coding: utf-8 -*-


# 模块导入
import time
import threading
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
reg_id = re.compile('zg_critical|zg_nonCritical')


# 类别网址获取
def getHtmlUrlList(html_url):
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        response = opener.open(request)
    except:
        print(html_url + ' open failed.')
    else:
        cookie.save(ignore_discard=True, ignore_expires=True)

        bs_obj = BeautifulSoup(response.read(), 'html.parser')

        # 排除script脚本
        for script in bs_obj(['script', 'style']):
            script.extract()

        node = bs_obj.find('', {'id': 'zg_browseRoot'})
        if node and len(node) > 0:
            name_list = []
            link_list = []
            for item in node.find_all('a'):
                if item != '\n':
                    name = translate(item.get_text().strip().replace('\n', ''))
                    name_list.append(name)
                    link = item.get('href').strip().replace('\n', '')
                    link = link[:link.rfind("/")]
                    link_list.append(link)
            print("name_list len: " + str(len(name_list)))
            print(name_list)
            print("link_list len: " + str(len(link_list)))
            print(link_list)

            return link_list


# 每个类别开启新线程获取Top100
def startMutilThread(link_list):
    thread_list = []
    for html_url in link_list:
        thread_list.append(threading.Thread(target=getTop100Items, args=(html_url,)))
    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()
        thread.join()


# 获取某类别下Top 100 items
def getTop100Items(html_url):
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
    except:
        print(html_url + ' open failed.')
    else:
        cookie.save(ignore_discard=True, ignore_expires=True)

        bs_obj = BeautifulSoup(html_file.read(), 'html.parser')

        # 排除script脚本
        for script in bs_obj(['script', 'style']):
            script.extract()

        print(html_url + ":")
        node = bs_obj.find('', {'id': 'zg_paginationWrapper'})
        if node and len(node) > 0:
            html_url_list = []
            link_list = []
            for item in node.find_all('a'):
                if item != '\n':
                    link = item.get('href').strip().replace('\n', '')
                    html_url_list.append(link)
            for temp_html_url in html_url_list:
                getSub20Items(temp_html_url, link_list)
            print(link_list)


# 分5次获取Top 100 items, 每次20条
def getSub20Items(html_url, link_list):
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
    except:
        print(html_url + ' open failed.')
    else:
        cookie.save(ignore_discard=True, ignore_expires=True)

        bs_obj = BeautifulSoup(html_file.read(), 'html.parser')

        # 排除script脚本
        for script in bs_obj(['script', 'style']):
            script.extract()

        print(html_url + ":")
        node = bs_obj.find('', {'id': 'zg_critical'})
        if node and len(node) > 0:
            for item in node.find_all('a'):
                if item != '\n':
                    link = item.get('href').strip().replace('\n', '')
                    if "/product-reviews" in link:
                        link = "https://www.amazon.co.jp/dp/" + link[len("/product-reviews/") : link.rfind("/")]
                        if link not in link_list:
                            print(link)
                            link_list.append(link)

        node = bs_obj.find('', {'id': 'zg_nonCritical'})
        if node and len(node) > 0:
            for item in node.find_all('a'):
                if item != '\n':
                    link = item.get('href').strip().replace('\n', '')
                    if "/product-reviews" in link:
                        link = "https://www.amazon.co.jp/dp/" + link[len("/product-reviews/") : link.rfind("/")]
                        if link not in link_list:
                            print(link)
                            link_list.append(link)


# 主方法
if __name__ == '__main__':
    html_url = 'https://www.amazon.co.jp/gp/bestsellers/'

    link_list = getHtmlUrlList(html_url)

    startMutilThread(link_list)