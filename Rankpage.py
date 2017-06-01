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

# 2 ----------------常量定义
# 汇率(API)
exchange_rate = 15
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

# 通过图片获取淘宝竞争品的信息
def get_taobao_data(amazon_picture_name):
    driver = webdriver.Firefox()
    try:
        driver.get('https://www.taobao.com/')
    except Exception as e:
        print(e)

    try:
        driver.find_element_by_id("J_IMGSeachUploadBtn").clear() # 非常奇怪，没有这句话无法工作
        time.sleep(5)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(amazon_picture_name)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(Keys.ENTER)
    except Exception as e:
        print(e)
    time.sleep(5)
    get_html = driver.page_source
    driver.quit()
    bs_obj = BeautifulSoup(get_html,'html.parser')
    target_div_node = bs_obj.find('div', {'class': 'items g-clearfix'})


    taobao_output_data = [[0 for col in range(3)]for row in range(len(target_div_node))]
    for i in range(len(target_div_node)):
       for j in range(3):
            print(taobao_output_data[i][j])


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

    return taobao_output_data


# 获取亚马逊商品信息
def pull_amazon_Data(asin):
    html_url = r'https://www.amazon.co.jp/dp/' + asin
    # 提取网页内容
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
    except:
        print('open html failed **************************')

    print(u'打印获取数据: ')

        # 商品总信息列表
    product_info_list = []

    cookie.save(ignore_discard=True, ignore_expires=True)
    bs_obj = BeautifulSoup(html_file.read(), 'html.parser')

        # 排除script脚本*************************************
    for script in bs_obj(['script', 'style']):
        script.extract()

    # 3.1 宝贝名称
    title = ''
    title_node = bs_obj.find('', {'id': 'productTitle'})
    if title_node and len(title_node) > 0:
        title = translate1(title_node.get_text().strip().replace('\'', ''))

    # 0
    product_info_list.append(title)
    println(u'title--宝贝名称: %s' % title)

    star_number = ''
    star_number_node = bs_obj.find('span', {'id': 'acrPopover'})
    if star_number_node and len(star_number_node) > 0:
        star_number = star_number_node.attrs['title'].strip().replace('\'', '')

        # 1
    product_info_list.append(star_number)
    println(u'总得分: %s' % star_number)


    reviewer_number = ''
    reviewer_number_node = bs_obj.find('span', {'id': 'acrCustomerReviewText'})
    if reviewer_number_node and len(reviewer_number_node) > 0:
        reviewer_number = reviewer_number_node.get_text().strip().replace('\'', '')

    # 2
    product_info_list.append(reviewer_number)
    println(u'评论数: %s' % reviewer_number)

    answer_number = ''
    answer_number_node = bs_obj.find('a', {'id': 'askATFLink'})
    if answer_number_node and len(answer_number_node) > 0:
        answer_number = answer_number_node.get_text().strip().replace('\'', '')

        # 3
    product_info_list.append(answer_number)
    println(u'回答问题数: %s' % answer_number)


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

        # 商品详细
    detail_label_list = []
    detail_value_list = []
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
    elif detail_bullets_node and len(detail_bullets_node) >0:
        print(u'没有table的页面')

        # 价格
    weight_temp = str('1000000克')
    for i in range(len(detail_label_list)):
        if re.search(r".*重量.*", detail_label_list[i]) != None:
            weight_temp = detail_value_list[i]
            break
        if re.search(r".*公斤.*", weight_temp) != None:
            weight = int(1000*float((weight_temp.replace(u'公斤', '').strip())))
        elif re.search(r".*克.*", weight_temp) != None:
            weight = int(weight_temp.replace(u'克', '').strip())
        else:
            weight = 1000000
        if (weight + packet_weight) < 500:
            ems = 100
        else:
            ems = 100 + ((weight + packet_weight - 500) / 100) * 10
        price = round(((src_price + ship_price) / exchange_rate + (ems)) * (1 + profit_rate))

        # 4
    product_info_list.append(price)
    println(u'price--宝贝价格: %s' % price)


        # 发布时间
    release_time = ''
    now_days = datetime.datetime.now()
    sale_days = 0
    for i in range(len(detail_label_list)):
        if re.search(r".*開始日.*", detail_label_list[i]) != None:
            temptime = detail_value_list[i].replace("/", "-")
            release_day = datetime.datetime.strptime(temptime, "%Y-%m-%d")
            sale_days = (now_days - release_day).days

    # 5
    product_info_list.append(sale_days)
    println(u'发布时间: %s' % sale_days)

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

        # 品牌
    brand = ''
    brand_node = bs_obj.find('', {'id': 'brand'})
    if brand_node and len(brand_node) > 0:
        brand = translate1(brand_node.get_text().strip().replace('\'', ''))

        # 7
    product_info_list.append(brand)
    println(u'brand--品牌: %s' % brand)


        # 图片地址
    picure_temp_path = sys.path[0] + '/Temp_images/'+ asin + '.jpg'
    image_list = []
    image_node = bs_obj.find('', {'id': 'altImages'})
    if image_node and len(image_node) > 0:
        for image_text in image_node.find_all('img'):
            if image_text != '\n':
                image = image_text.get('src').replace('SS40', 'SL600')
                image_list.append(image)
    print(u'image_list--图片地址: ')
    println(image_list)

    # pd_list描述
    pd_list = []
    pd_node = bs_obj.find('div', id=re.compile(".*descriptionAndDetails.*"))
    if pd_node and len(pd_node) > 0:
        image_head_deleted_content_product = delete_img_head_reg.sub('', pd_node.prettify())
        html_head_deleted_content_product = delete_html_head_reg.sub('', image_head_deleted_content_product).replace(' ', '').strip('\n')
        pd_list_temp = delete_n_reg.split(html_head_deleted_content_product)
        for pd_item in pd_list_temp:
            if re.search('http', pd_item) == None:
                pd_temp = reg_replace.sub('', pd_item)
            else:
                pd_temp = re.search(r"http.*(jpg|png)", pd_item).group(0)
            pd_list.append(pd_temp)
    print(u'pd_list--描述: ')
    println(pd_list)


    picture_number = len(image_list) + len(pd_list)

        # 8
    product_info_list.append(picture_number)
    println(u'图片个数: %d' % picture_number)

    # 保存第一张图片
    try:
        if not os.path.exists(picure_temp_path):
            urllib.request.urlretrieve(image_list[0],picure_temp_path)
    except Exception as e:
            print(e)

        # 9
    product_info_list.append(picure_temp_path)
    println(u'图片个数: %s' % picure_temp_path)

        # 3.51 物流重量
    item_weight = int(round(((weight + packet_weight) / 1000), 1))

        # 10
    product_info_list.append(item_weight)
    println(u'item_weight--物流重量: %s' % item_weight)

    # 返回获取的数据结果
    return product_info_list

def similar_ratio(str1, str2):
    similar_index = Levenshtein.jaro(str1, str2)
    return similar_index


def ranking(asin,ranknumber,category):
    rank_value = 0
    asin_info = []
    tb_info = [[]]

    asin_info = pull_amazon_Data(asin)
    time.sleep(3)
    tb_info = get_taobao_data(asin_info[9].replace("/",os.sep))

#   删除文件
    if tb_info and len(tb_info) > 0:
        try:
            os.remove(asin_info[9].replace("/",os.sep))
        except Exception as e:
            print(e)

# 把字符串等数据处理成为数值

    amazon_title = str(asin_info[0]) + str(asin_info[7])
    amazon_star_number = int(re.sub("\D", "", asin_info[1]))
    amazon_revi_number = int(re.sub("\D", "", asin_info[2]))
    amazon_price = int(asin_info[4])
    amazon_days = int(asin_info[5])
    amazon_availability = int(asin_info[6])
    amazon_picture_number = int(asin_info[8])
    amazon_item_weight = int(asin_info[10])
    amazon_ranknum = ranknumber
    amazon_catagory = category

# 删除空行
    zero_row = [0,0,0]
    for item in tb_info:
        while tb_info.count(zero_row)>=1:
            tb_info.remove(zero_row)


#---------初步筛选数据----------------
    # 剪除名称不相关的数据
    dellist = []
    for i in range(len(tb_info)):
        similar_index = similar_ratio(amazon_title,tb_info[i][0])
        if similar_index < 0.3 :
            dellist.append(tb_info[i][0])

    for item in dellist:
        for i in tb_info:
            while tb_info.count(item) >= 1:
                tb_info.remove(item)

    # 剪除价格明显问题的数据

    dellist = []
    for i in range(len(tb_info)):
        if tb_info[i][1] < amazon_price*0.8 :
            dellist.append(tb_info[i][1])

    for item in dellist:
        for i in tb_info:
            while tb_info[:][1].count(item) >= 1:
                tb_info.remove(item)

# ---------根据统计学筛选数据----------------
    price_sum1 = 0.0
    price_sum2 = 0.0
    volume_sum1 = 0.0
    volume_sum2 = 0.0
    for i in range(len(tb_info)):
        price_sum1 += tb_info[i][2]
        volume_sum1 += tb_info[i][1]
        price_sum2 += tb_info[i][2] ** 2
        volume_sum2 += tb_info[i][1] ** 2
    price_mean = price_sum2 /len(tb_info)
    price_var = price_sum2 / len(tb_info) - price_mean ** 2
    volume_mean = volume_sum1 /len(tb_info)
    volume_var = volume_sum2 / len(tb_info) - volume_mean ** 2

    # 按照销量从高到低排序
    tb_info_sorted = sorted(tb_info,key=lambda x:x[1],reverse=True)

    # 计算取前几名
    j = 8
    for i in range(len(tb_info_sorted)):
        if volume_var/i < 2:
            j -= 1

# 销量方差越大，取平均的数量就越少，销量方差大于5，取平均前3名？
# 销量前三名的平均价格作为该产品价格

    # 根据偏离平均值的程度和方差，进一步剪除价格有问题的数据，
    sum_price = 0
    for i in range(j):
        sum_price += tb_info_sorted[i][2]
    mean_price = int(sum_price/j)



# 计算推荐程度
    rank_result = 1000
    if amazon_availability == 2:
        rank_result -= 200
    elif amazon_availability == 3:
        rank_result -= 600
    elif amazon_availability == 4:
        rank_result -= 800
    elif amazon_availability == 5:
        rank_result -=  900
    else:
        rank_result = 0


    if amazon_item_weight >= 25000:
        rank_result -= 900
    elif amazon_item_weight >= 10000:
        rank_result -= 100
    elif amazon_item_weight >= 5000:
        rank_result -= 50
    elif amazon_item_weight >= 1000:
        rank_result -= 10


    if amazon_price >= 3000:
        rank_result -= 300
    elif amazon_price >= 2000:
        rank_result -= 10
    elif amazon_price <= 100:
        rank_result -= 20
    elif amazon_price <= 150:
        rank_result -= 10

    #coefficient of star
    if amazon_revi_number <= 10:
        coefficient = 15
    elif amazon_revi_number > 10 and amazon_price <= 50:
        coefficient = 10
    elif amazon_revi_number > 50 and amazon_price <= 100:
        coefficient = 5
    elif amazon_revi_number > 100 and amazon_price <= 300:
        coefficient = 2
    elif amazon_revi_number > 300 and amazon_price <= 1000:
        coefficient = 1
    else:
        coefficient = 0.5


    output_rank = rank_result - (550-amazon_star_number)*coefficient - amazon_days*0.01 - amazon_ranknum*0.1 + ((mean_price-amazon_price)/amazon_price)*400


    return output_rank





if __name__ == '__main__':
    ranking('B0013NHU6K',4, 'category')
