# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import threading
import http.cookiejar
import urllib.request, urllib.parse, urllib.error
import datetime
import os
import sys
import numpy
import Levenshtein
import re
from Utils import *
import operator
import math


# 2 ----------------常量定义
# 汇率(API)
exchange_rate = 16.24
# 利润率(可调)
profit_rate = 0
# 包装重量(克)
packet_weight = 150

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

# 获取亚马逊商品信息
def pull_amazon_Data(asin,amazon_image_path):
    html_url = r'https://www.amazon.co.jp/dp/' + asin
    product_info_list = []
    # 提取网页内容
    print("提取网页内容")
    time_mark()

    try:
        cookie.save(ignore_discard=True, ignore_expires=True)
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
        bs_obj = BeautifulSoup(html_file.read(), 'html.parser')
        for script in bs_obj(['script', 'style']):
            script.extract()
    except:
        print('open html failed **************************')

    print("提取网页内容成功")
    time_mark()

    # 3.1 宝贝名称
    title = ''
    title_node = bs_obj.find('', {'id': 'productTitle'})
    if title_node and len(title_node) > 0:
        title = translate1(title_node.get_text().strip().replace('\'', ''))

    # 0
    product_info_list.append(title)
    println(u'title--宝贝名称: %s' % title)

    time_mark()

    star_number = ''
    star_number_node = bs_obj.find('span', {'id': 'acrPopover'})
    if star_number_node and len(star_number_node) > 0:
        star_number = star_number_node.attrs['title'].strip().replace('\'', '')

        # 1
    product_info_list.append(star_number)
    println(u'总得分: %s' % star_number)
    time_mark()

    reviewer_number = ''
    reviewer_number_node = bs_obj.find('span', {'id': 'acrCustomerReviewText'})
    if reviewer_number_node and len(reviewer_number_node) > 0:
        reviewer_number = reviewer_number_node.get_text().strip().replace('\'', '')

    # 2
    product_info_list.append(reviewer_number)
    println(u'评论数: %s' % reviewer_number)
    time_mark()

    answer_number = ''
    answer_number_node = bs_obj.find('a', {'id': 'askATFLink'})
    if answer_number_node and len(answer_number_node) > 0:
        answer_number = answer_number_node.get_text().strip().replace('\'', '')

        # 3
    product_info_list.append(answer_number)
    println(u'回答问题数: %s' % answer_number)
    time_mark()

        # 原价
    src_price = 0
    src_price_node = bs_obj.find('', {'id': 'priceblock_ourprice'})
    if src_price_node and len(src_price_node) > 0:
        src_price = int(src_price_node.get_text().replace('￥', '').replace(',', '').strip())
    println(u'src_price--原价: %s' % src_price)

        # 配送费
    ship_price = 500
    ship_price_node = bs_obj.find('', {'id': 'price-shipping-message'})
    if ship_price_node and len(ship_price_node) > 0:
        ship_price_text = ship_price_node.get_text().replace('\n', '').strip()
        if u'配送無料' in ship_price_text and '¥' not in ship_price_text:
            ship_price = 0
    println(u'ship_price--配送费: %s' % ship_price)

    time_mark()

    # 商品详细
    detail_label_list = []
    detail_value_list = []
    weight_temp = ''
    type_temp = ''
    asin_temp = ''
    startday_temp = ''

    detail_node = bs_obj.find('', {'id': 'prodDetails'})
    detail_bullets_node = bs_obj.find('', {'id': 'detail_bullets_id'})
    if detail_node and len(detail_node) > 0:
        for label_text in detail_node.find_all('td', {'class': 'label'}):
            if label_text != '\n':
                label = label_text.get_text().strip().replace('\n', '')
                detail_label_list.append(label)
        for value_text in detail_node.find_all('td', {'class': 'value'}):
            if value_text != '\n':
                value = value_text.get_text().strip().replace('\n', '')
                detail_value_list.append(value)
        # 获取重要信息
        # 重量信息
        for i in range(len(detail_label_list)):
            if re.search(r".*重量.*", detail_label_list[i]) != None:
                weight_temp = detail_value_list[i]
            if re.search(r".*型番.*", detail_label_list[i]) != None:
                type_temp = detail_value_list[i]
            if re.search(r".*ASIN.*", detail_label_list[i]) != None:
                asin_temp = detail_value_list[i]
            if re.search(r".*開始日.*", detail_label_list[i]) != None:
                startday_temp = detail_value_list[i]
    elif detail_bullets_node and len(detail_bullets_node) >0:
        for item in detail_bullets_node.find_all('li'):
            item_text = item.get_text().strip().replace('\n', '')
            if re.search(r".*重量.*", item_text) != None:
                weight_temp = re.sub(r".*:","",item_text).strip()
            if re.search(r".*型番.*", item_text) != None:
                type_temp = re.sub(r".*型番.","",item_text).strip()
            if re.search(r".*ASIN.*", item_text) != None:
                asin_temp = re.sub(r".*:", "", item_text).strip()
            if re.search(r".*開始日.*", item_text) != None:
                startday_temp = re.sub(r".*:", "", item_text).strip()

    print("提取属性成功")
    time_mark()


# 获取价格
    if re.search(r".*Kg.*", weight_temp) != None:
        weight_factor =1000
    else:
        weight_factor = 1

    packet_total_weight = int(float(weight_temp.replace(u'K','').replace(u'g','').strip()) * weight_factor)+ packet_weight
    ems = ems_fee(packet_total_weight)
    price = round(((src_price + ship_price + ems) / exchange_rate) * (1 + profit_rate))

        # 4
    product_info_list.append(price)
    println(u'price--宝贝价格: %s' % price)
    time_mark()


        # 发布时间
    now_days = datetime.datetime.now()
    sale_days = 0
    for i in range(len(detail_label_list)):
        if startday_temp != None:
            temptime = startday_temp.replace("/", "-")
            release_day = datetime.datetime.strptime(temptime, "%Y-%m-%d")
            sale_days = (now_days - release_day).days

    # 5
    product_info_list.append(sale_days)
    println(u'发布时间: %s' % sale_days)
    time_mark()

     # 可用性
    availability = 5
    availability_node = bs_obj.find('', {'id': 'availability'})
    if availability_node and len(availability_node) > 0:
        availability_text = availability_node.get_text().replace('\n', '').strip()
        if (re.search(r".*在庫あり.*",availability_text) != None):
            availability = 1
        elif (re.search(r".*日以内に発送.*",availability_text) != None):
            availability = 2
        elif (re.search(r".*週間以内に発送.*",availability_text) != None):
            availability = 3
        elif (re.search(r".*か月以内に発送.*",availability_text) != None):
            availability = 4
        else: availability = 5

        # 6
    product_info_list.append(availability)
    println(u'可用性: %d' % availability)
    time_mark()

        # 品牌
    brand = ''
    brand_node = bs_obj.find('', {'id': 'brand'})
    if brand_node and len(brand_node) > 0:
        brand = translate1(brand_node.get_text().strip().replace('\'', ''))

        # 7
    product_info_list.append(brand + type_temp)
    println(u'brand--品牌: %s' % brand)
    time_mark()

        # 图片地址

    image_list = []
    image_node = bs_obj.find('', {'id': 'altImages'})
    if image_node and len(image_node) > 0:
        for image_text in image_node.find_all('img'):
            if image_text != '\n':
                image = image_text.get('src').replace('SS40', 'SL600')
                image_list.append(image)
    print(u'image_list--图片地址: ')
    time_mark()

    # pd_list描述
    pd_list = []
    pd_node = bs_obj.find('div', id=re.compile(".*descriptionAndDetails.*"))
    if pd_node and len(pd_node) > 0:
        for image_text in pd_node.find_all('img'):
            if image_text != '\n':
                image = image_text.get('src')
                pd_list.append(image)
    print(u'pd_list--描述: ')
    time_mark()

    # pd_list描述
    aplus_list = []
    aplus_node = bs_obj.find('div', id=re.compile(".*aplus_feature_div.*"))
    if aplus_node and len(aplus_node) > 0:
        for image_text in aplus_node.find_all('img'):
            if image_text != '\n':
                image = image_text.get('src')
                aplus_list.append(image)
    print(u'pd_list--描述: ')
    time_mark()

    picture_number = len(image_list) + len(pd_list) + len(aplus_list)

        # 8
    product_info_list.append(picture_number)
    println(u'图片个数: %d' % picture_number)
    time_mark()

     # 3.51 物流重量
    # 9
    product_info_list.append(packet_total_weight)
    println(u'item_weight--物流重量: %s' % packet_total_weight)
    time_mark()
    # 保存第一张图片
    try:
        if not os.path.exists(amazon_image_path):
            urllib.request.urlretrieve(image_list[0],amazon_image_path)
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            print(now)
    except Exception as e:
            print(e)
    print("保存图片成功")
    time_mark()

    # 返回获取的数据结果
    return product_info_list
# 通过图片获取淘宝竞争品的信息
def pull_taobao_data(amazon_picture_name):
    print("获取淘宝开始")
    time_mark()

    driver = webdriver.Firefox()
    try:
        driver.get('https://www.taobao.com/')
    except Exception as e:
        print(e)
    print("获取淘宝页面成功")
    time_mark()
    try:
        driver.find_element_by_id("J_IMGSeachUploadBtn").clear() # 非常奇怪，没有这句话无法工作
        time.sleep(5)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(amazon_picture_name)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(Keys.ENTER)
    except Exception as e:
        print(e)

    print("设置图片搜索成功")
    time_mark()

    time.sleep(5)
    get_html = driver.page_source
    driver.quit()

    print("获取淘宝结果成功")
    time_mark()

    bs_obj = BeautifulSoup(get_html,'html.parser')
    target_div_node = bs_obj.find('div', {'class': 'items g-clearfix'})

    print("获取OBJ")
    time_mark()

    taobao_output_data = [[0 for col in range(4)]for row in range(len(target_div_node))]
    if target_div_node and len(target_div_node) > 0:
        number = 0
        for items_div in target_div_node.find_all('div', {'class': r'row row-2 title'}): #获取名称
            item_name = items_div.get_text().strip()
            taobao_output_data[number][0] = item_name
            number += 1
            print (item_name)

        number = 0
        for items_div in target_div_node.find_all('div', {'class': 'price g_price g_price-highlight'}): #获取价格
            item_price = int(int(re.sub("\D", "", items_div.get_text().strip()))/100)
            taobao_output_data[number][1] = item_price
            number += 1
            print(item_price)

        number = 0
        for items_div in target_div_node.find_all('div', {'class': 'deal-cnt'}): #获取销量
            item_account = int(re.sub("\D", "", items_div.get_text().strip()))
            taobao_output_data[number][2] = item_account
            number += 1
            print(item_account)

        number = 0
        for items_div in target_div_node.find_all('img', {'class': 'J_ItemPic img'}): #获取销量
            item_image = items_div.get('src').strip()
            taobao_output_data[number][3] = item_image
            number += 1
            print(item_image)

    print("获取taobao_data")
    time_mark()

    return taobao_output_data
# 进行评比对比
def ranking(asin,ranknumber,category):
    amazon_image_path = sys.path[0] + '/Temp_images/' + asin + '.jpg'
    amazon_image_path_temp = sys.path[0] + '/Temp_images/' + asin + '_temp' + '.jpg'
    rank_value = 0
    asin_info = []
    tb_info = [[]]

    print("开始获取亚马逊信息")
    time_mark()

    asin_info = pull_amazon_Data(asin,amazon_image_path)



    time.sleep(3)

    print("开始获取淘宝信息")
    time_mark()


    tb_info = pull_taobao_data(amazon_image_path.replace("/",os.sep))
    time.sleep(5)




# 把字符串等数据处理成为数值
    print("把字符串等数据处理成为数值")
    time_mark()

    amazon_title = str(asin_info[0])
    amazon_title_2nd = "日本直邮"+ str(asin_info[7]) + category
    amazon_star_number = int(re.sub("\D", "", asin_info[1]))
    amazon_revi_number = int(re.sub("\D", "", asin_info[2]))
    amazon_price = int(asin_info[4])
    amazon_days = int(asin_info[5])
    amazon_availability = int(asin_info[6])
    amazon_picture_number = int(asin_info[8])
    amazon_item_weight = int(asin_info[9])
    amazon_ranknum = ranknumber
    amazon_catagory = category

# 删除空行
    zero_row = [0,0,0,0]
    for item in tb_info:
        while tb_info.count(zero_row)>=1:
            tb_info.remove(zero_row)

# 对数据进行变换，将决对的数据转化为指数

            #  进行筛选， 第一，筛选图片相似度， 第二筛选名称相似度， 第三，筛选价格
    title_corelation_critial = 0.85
    title_aux_critial = 0.5
    image_corelation_critial = 0.85
    image_aux_critial = 0.5
    title_image_mix = 1.1
    price_corelation_critial_min = -0.3
    price_corelation_critial_max = 3
    price_impact_factor = 10
    volume_impact_factor = 0.1

    print("获取淘宝推荐")
    time_mark()

    tb_index = [[0 for col in range(4)] for row in range(len(tb_info))]
    for item in tb_info:
        a1 = (compare_str(item[0],amazon_title))
        a2 = (compare_str(item[0],amazon_title_2nd))
        #提升翻译准确度很重要
        if a1 >= a2:
            a =a1
        else:
            a =a2
        b = (item[1]- amazon_price)/amazon_price
        c = item[2]
        # 获取图片对结果
        tb_image_path = sys.path[0] + '/Temp_images/' + 'tb'+ '.jpg'
        try:
            if not os.path.exists(tb_image_path):
                tb_image_url = 'https:'+ item[3]
                urllib.request.urlretrieve(tb_image_url, tb_image_path)
        except Exception as e:
            print(e)

        resizeImg(amazon_image_path,amazon_image_path_temp,220,220,95)
        d = compare_image(amazon_image_path,tb_image_path,size=(220,220))
        try:
            os.remove(tb_image_path)
        except Exception as e:
            print(e)

        if a >= title_corelation_critial and d>=image_aux_critial and b>= price_corelation_critial_min and b < price_corelation_critial_max:
            tb_index.append([a, b, c, d])
        elif d >= image_corelation_critial and a>=title_aux_critial and b>= price_corelation_critial_min and b < price_corelation_critial_max:
            tb_index.append([a, b, c, d])
        elif a + d >= title_image_mix and b>= price_corelation_critial_min and b < price_corelation_critial_max:
            tb_index.append([a, b, c, d])

    for item in tb_index:
        while tb_index.count(zero_row)>=1:
            tb_index.remove(zero_row)

    if tb_index != None and len(tb_index) !=0:
        tb_index.sort(key=operator.itemgetter(2))
        tb_price_gap = tb_index[0][1]*100
        tb_volume = math.log(tb_index[0][2]+2)*10
        tb_rank = tb_price_gap * tb_volume
    else:
        tb_rank = 100

    print("计算推荐程度")
    time_mark()
# 计算推荐程度
    if amazon_availability == 2:
        rank_availability = 0
    elif amazon_availability == 3:
        rank_availability = -50
    elif amazon_availability == 4:
        rank_availability = -1000
    elif amazon_availability == 5:
        rank_availability = -1000
    else:
        rank_availability = 0


    if amazon_item_weight >= 30000:
        rank_weight = -1000
    elif amazon_item_weight >= 10000:
        rank_weight = -100
    elif amazon_item_weight >= 5000:
        rank_weight = -50
    elif amazon_item_weight >= 1000:
        rank_weight = -10
    else:
        rank_weight = 0


    if amazon_price >= 3000:
        rank_price = -300
    elif amazon_price >= 2000:
        rank_price = -10
    elif amazon_price <= 100:
        rank_price = -20
    elif amazon_price <= 150:
        rank_price = -10
    else:
        rank_price = 0


    #coefficient of star

    rank_review = math.log(amazon_revi_number+2)

    output_rank = tb_rank + rank_availability + rank_weight + rank_price + (amazon_star_number-550)*rank_review + math.log(amazon_days+2)*10 - math.log(amazon_ranknum+2)*10 + amazon_picture_number

    print("删除文件")
    time_mark()

    #   删除文件
    try:
        os.remove(amazon_image_path.replace("/", os.sep))
        os.remove(amazon_image_path_temp.replace("/", os.sep))
    except Exception as e:
            print(e)

    print("删除完成")
    time_mark()

    print("rank value")
    print(output_rank)
    time_mark()
    return output_rank

if __name__ == '__main__':
    ranking('B00HWMS21I',1, '男士电动剃须刀')