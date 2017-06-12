# -*- coding: utf-8 -*-


# 模块导入
import csv
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
url_g = 'https://www.amazon.co.jp/gp/bestsellers/beauty'
asin_filter_g = '/dp/'
timeout_open_g = 10


# 正则表达式
nav_tag_g = '_nav_'
delete_tag_g = re.compile('/ref=zg_.*')


# 获取美妆类别下的子链接
def getSubUrlList(url_arg):
    url_list = []
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
            for script in bs_obj(['script', 'style']):
                script.extract()

            node = bs_obj.find('', {'id': 'zg_browseRoot'})
            if node and len(node) > 0:
                for item in node.find_all('a'):
                    url = item.get('href').strip()
                    if nav_tag_g not in url:
                        continue
                    url = delete_tag_g.sub('', url)
                    print(url)
                    url_list.append(url)

    return url_list


# 获取所有子类别对应的top 100 items对应的5个urls
def getTop100UrlList(url_arg):
    top100_url_list = []
    for url in url_arg:
        top100_urls = getTop100Urls(url)
        top100_url_list.append(top100_urls)

    return top100_url_list


# 获取某子类别下的top 100 items对应的5个urls
def getTop100Urls(url_arg):
    url_list = []
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
            for script in bs_obj(['script', 'style']):
                script.extract()

            node = bs_obj.find('', {'id': 'zg_paginationWrapper'})
            if node and len(node) > 0:
                for item in node.find_all('a'):
                    url = item.get('href').strip()
                    print(url)
                    url_list.append(url)

    return url_list


# 获取所有子类别对应的top 1000 item asins
def getTop1000AsinList(url_arg):
    top1000_asin_list = []
    for url_list in url_arg:
        for url in url_list:
            top20_asins = get20ItemAsins(url)
            top1000_asin_list.append(top20_asins)

    return top1000_asin_list


# 获取url_arg指定的20条
def get20ItemAsins(url_arg):
    asin_list = []
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
                    asin_row = []
                    asin_row.append(asin)
                    print(asin)
                    writeAsin(asin_row)
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
                    asin_row = []
                    asin_row.append(asin)
                    print(asin)
                    writeAsin(asin_row)
                    asin_list.append(asin)

    return asin_list


item_file = open('Asins.csv', 'a+', newline='')
item_writer = csv.writer(item_file, dialect='excel')
# 将top 1000 asins写入csv文件
def writeAsin(asin_arg):
    item_writer.writerow(asin_arg)


# 文件执行入口
if __name__ == '__main__':
    sub_url_list = getSubUrlList(url_g)
    print(len(sub_url_list))
    top100_url_list = getTop100UrlList(sub_url_list)
    print(len(top100_url_list))
    top1000_asin_list = getTop1000AsinList(top100_url_list)
    print(len(top1000_asin_list))
    item_file.close()