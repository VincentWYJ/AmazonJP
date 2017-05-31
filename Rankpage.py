# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import threading
import http.cookiejar
import urllib.request, urllib.parse, urllib.error
from Utils import *
import datetime
import os
import sys

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
    i = 0
    taobao_output_data =[]
    driver = webdriver.Firefox()
    try:
        driver.get('https://www.taobao.com/')
    except Exception as e:
        print(e)

    try:
        driver.find_element_by_id("J_IMGSeachUploadBtn").clear() # 非常奇怪，没有这句话无法工作
        time.sleep(10)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(amazon_picture_name)
        driver.find_element_by_id("J_IMGSeachUploadBtn").send_keys(Keys.ENTER)
    except Exception as e:
        print(e)
    time.sleep(20)
    get_html = driver.page_source
    driver.quit()
    bs_obj = BeautifulSoup(get_html,'html.parser')
    target_div_node = bs_obj.find('div', {'class': 'items g-clearfix'})
    if target_div_node and len(target_div_node) > 0:
        for items_div in target_div_node.find_all('div', {'class': r'row row-2 title'}): #获取名称
            item_name = items_div.get_text().strip()
            taobao_output_data.append(item_name)
            print (item_name)
        for items_div in target_div_node.find_all('div', {'class': 'price g_price g_price-highlight'}): #获取价格
            item_price = items_div.get_text().strip()
            taobao_output_data.append(item_price)
            print(item_price)
        for items_div in target_div_node.find_all('div', {'class': 'deal-cnt'}): #获取销量
            item_account = items_div.get_text().strip()
            taobao_output_data.append(item_account)
            print(item_account)
        print(taobao_output_data)
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
    else:
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
            title = translate(title_node.get_text().strip().replace('\'', ''))

        # 0
        product_info_list.append(title)
        println(u'title--宝贝名称: %s' % title)

        star_number = ''
        star_number_node = bs_obj.find('span', {'id': 'acrPopover'})
        if star_number_node and len(star_number_node) > 0:
            star_number = translate(star_number_node.title.get_text().strip().replace('\'', ''))

        # 1
        product_info_list.append(star_number)
        println(u'总得分: %s' % star_number)


        reviewer_number = ''
        reviewer_number_node = bs_obj.find('span', {'id': 'acrCustomerReviewText'})
        if reviewer_number_node and len(reviewer_number_node) > 0:
            reviewer_number = translate(reviewer_number_node.get_text().strip().replace('\'', ''))

        # 2
        product_info_list.append(reviewer_number)
        println(u'评论数: %s' % reviewer_number)

        answer_number = ''
        answer_number_node = bs_obj.find('a', {'id': 'askATFLink'})
        if answer_number_node and len(answer_number_node) > 0:
            answer_number = translate(answer_number_node.get_text().strip().replace('\'', ''))

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
                    label = translate(label_text.get_text().strip().replace('\n', ''))
                    detail_label_list.append(label)
            for value_text in detail_node.find_all('td', {'class': 'value'}):
                if value_text != '\n':
                    value = translate(value_text.get_text().strip().replace('\n', ''))
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
        now_days = datetime.datetime.now("%Y-%m-%d")
        for i in range(len(detail_label_list)):
            if re.search(r".*Amazon.*", detail_label_list[i]) != None:
                release_day = datetime.datetime.strptime(detail_value_list[i], "%Y-%m-%d").date()
                sale_days = (now_days - release_day).days
                break

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
            brand = translate(brand_node.get_text().strip().replace('\'', ''))

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
            html_head_deleted_content_product = delete_html_head_reg.sub('', image_head_deleted_content_product).\
                replace(' ', '').strip('\n')
            pd_list_temp = delete_n_reg.split(html_head_deleted_content_product)
            for pd_item in pd_list_temp:
                if re.search('http', pd_item) == None:
                    pd_temp = reg_replace.sub('', translate(pd_item))
                else:
                    pd_temp = re.search(r"http.*(jpg|png)", pd_item).group(0)
                pd_list.append(pd_temp)
        print(u'pd_list--描述: ')
        println(pd_list)

        # aplus_list描述
        aplus_list = []
        aplus_node = bs_obj.find('div', id=re.compile(".*aplus_feature_div.*"))
        if aplus_node and len(aplus_node) > 0:
            image_head_deleted_content = delete_img_head_reg.sub('', aplus_node.prettify())
            html_head_deleted_content = delete_html_head_reg.sub('', image_head_deleted_content).replace(' ', '').\
                strip('\n')
            aplus_list_temp = delete_n_reg.split(html_head_deleted_content)
            for aplus_item in aplus_list_temp:
                if re.search('http', aplus_item) == None:
                    aplus_temp = reg_replace.sub('', translate(aplus_item))
                else:
                    aplus_temp = re.search(r"http.*(jpg|png)", aplus_item).group(0)
                aplus_list.append(aplus_temp)
        print(u'aplus_list--描述: ')
        println(aplus_list)

        # 客户评论
        comment_list = []
        comment_node = bs_obj.find('', id=re.compile(".*customer-reviews_feature_div.*"))
        if comment_node and len(comment_node) > 0:
            image_head_deleted_content_comment = delete_img_head_reg.sub('', comment_node.prettify())
            html_head_deleted_content_comment = delete_html_head_reg.sub('', image_head_deleted_content_comment).\
                replace(' ', '').strip('\n')
            comment_list_temp = delete_n_reg.split(html_head_deleted_content_comment)
            for comment_item in comment_list_temp:
                if re.search('http', comment_item) == None:
                    comment_temp = reg_replace.sub('', translate(comment_item))
                else:
                    comment_temp = re.search(r"http.*(jpg|png)", comment_item).group(0)
                comment_list.append(comment_temp)
        print(u'comment_image_list--客户图片评论: ')
        println(comment_list)

        # 获取图片个数
        picture_number = len(image_list) + len(pd_list) +len(aplus_list) + len(comment_list)

        # 8
        product_info_list.append(picture_number)
        println(u'图片个数: %d' % picture_number)

        # 保存第一张图片
        try:
            if not os.path.exists(picure_temp_path):
                urllib.request.urlretrieve(image[1],picure_temp_path)
        except Exception as e:
            print(e)

        # 8
        product_info_list.append(picure_temp_path)
        println(u'图片个数: %s' % picure_temp_path)

        # 3.51 物流重量
        item_weight = str(round(((weight + packet_weight) / 1000), 1))

        # 9
        product_info_list.append(item_weight)
        println(u'item_weight--物流重量: %s' % item_weight)

        # 返回获取的数据结果
        return product_info_list

def ranking(asin):
    rank_value = 0
    asin_info = []
    tb_info = []
    asin_info = pull_amazon_Data(asin)
    time.sleep(3)
    tb_info = get_taobao_data(asin_info[8])

    if len(tb_info)%3 == 0 :
        i = len(tb_info)/3
        tb_info





if __name__ == '__main__':
    get_taobao_data(picture_name)
