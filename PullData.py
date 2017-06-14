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
title_append = u''
# 描述头
description_start = 'xxx'
# 描述尾
description_end = 'yyy'
# 模拟浏览器登录
values = {'email': 'amazonjpysht9@sina.com', 'password': '1qaz2wsx@99', 'submit': 'Login'}
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
def ems_fee1(weight):
        if weight <= 500:
            ems_price = 1400
        elif weight < 1000:
            ems_price = 1400 + int((weight - 500) / 100) * 140
        elif weight == 1000:
            ems_price = 2100
        elif weight < 2000:
            ems_price = 2100 + int((weight - 1000) / 250) * 300
        elif weight == 2000:
            ems_price = 3300
        elif weight < 6000:
            ems_price = 3300 + int((weight - 2000) / 500) * 500
        elif weight == 6000:
            ems_price = 7300
        elif weight < 30000:
            ems_price = 7300 + int((weight - 6000) / 1000) * 800
        elif weight == 30000:
            ems_price = 26500
        else:
            ems_price = 2650000
        return ems_price

def pullData(html_url):
    global ems

    # 提取网页内容
    try:
        request = urllib.request.Request(html_url, postdata, headers)
        html_file = opener.open(request)
    except:
        print('open html failed ')
    else:
        # 正常处理模块
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
            title = title_node.get_text().strip().replace('\'', '')
            title = title_append + title

        try:
            c_title = translate1(title)
        except:
            product_info_list.append(title)
            println(u'title--宝贝名称: %s' % title)
        else:
            product_info_list.append(c_title)
            println(u'title--宝贝名称: %s' % c_title)

        # 3.2 宝贝类目
        cid = 50018961
        product_info_list.append(cid)
        # println(u'cid--宝贝类目: %s' % cid)

        # 3.3 店铺类目
        seller_cids = 50018961
        product_info_list.append(seller_cids)
        # println(u'seller_cids--店铺类目: %s' % seller_cids)

        # 3.4 淘宝新旧程度
        stuff_status = 1
        product_info_list.append(stuff_status)
        # println(u'stuff_status--新旧程度: %s' % stuff_status)

        # 3.5 省
        location_state = u'海外'
        product_info_list.append(location_state)
        # println(u'location_state--省: %s' % location_state)

        # 3.6 城市
        location_city = u'日本'
        product_info_list.append(location_city)
        # println(u'location_city--城市: %s' % location_city)

        # 3.7 出售方式
        item_type = 1
        product_info_list.append(item_type)
        # println(u'item_type--出售方式: %s' % item_type)

        # 3.8 宝贝价格
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
        elif detail_bullets_node and len(detail_bullets_node) > 0:
            for item in detail_bullets_node.find_all('li'):
                item_text = item.get_text().strip().replace('\n', '')
                if re.search(r".*重量.*", item_text) != None:
                    weight_temp = re.sub(r".*:", "", item_text).strip()
                if re.search(r".*型番.*", item_text) != None:
                    type_temp = re.sub(r".*型番.", "", item_text).strip()
                if re.search(r".*ASIN.*", item_text) != None:
                    asin_temp = re.sub(r".*:", "", item_text).strip()
                if re.search(r".*開始日.*", item_text) != None:
                    startday_temp = re.sub(r".*:", "", item_text).strip()

        print("提取属性成功")

        # 获取价格
        if re.search(r".*Kg.*", weight_temp) != None:
            weight_factor = 1000
            try:
                packet_total_weight = int(float(weight_temp.replace(u'Kg', '').strip()) *weight_factor) + packet_weight
            except:
                packet_total_weight = 10000
        elif re.search(r".*kg.*", weight_temp) != None:
            weight_factor = 1000
            try:
                packet_total_weight = int(float(weight_temp.replace(u'kg', '').strip()) *weight_factor) + packet_weight
            except:
                packet_total_weight = 10000
        elif re.search(r".*キロ.*", weight_temp) != None:
            weight_factor = 1000
            try:
                packet_total_weight = int(float(weight_temp.replace(u'キロ', '').strip()) *weight_factor) + packet_weight
            except:
                packet_total_weight = 10000
        elif re.search(r".*g.*", weight_temp) != None:
            weight_factor = 1
            try:
                packet_total_weight = int(float(weight_temp.replace(u'g', '').strip()) *weight_factor) + packet_weight
            except:
                packet_total_weight = 10000
        elif re.search(r".*グラム.*", weight_temp) != None:
            weight_factor = 1
            try:
                packet_total_weight = int(float(weight_temp.replace(u'グラム', '').strip()) *weight_factor) + packet_weight
            except:
                packet_total_weight = 10000
        else:
            packet_total_weight = 10000
        ems = ems_fee1(packet_total_weight)
        price = round(((src_price + ship_price + ems) / exchange_rate) * (1 + profit_rate))

        # 4
        product_info_list.append(price)
        println(u'price--宝贝价格: %s' % price)

        # 3.9 加价幅度
        auction_increment = 0
        product_info_list.append(auction_increment)
        # println(u'auction_increment--加价幅度: %s' % auction_increment)

        # 3.10 宝贝数量
        num = 0
        num_node = bs_obj.find('', {'id': 'availability'})
        if num_node and len(num_node) > 0:
            num_text = num_node.get_text().replace('\n', '').strip()
            if (re.search(r".*在庫あり.*", num_text) != None):
                num = 20
            elif (re.search(r".*日以内に発送.*", num_text) != None):
                num = 5
            elif (re.search(r".*週間以内に発送.*", num_text) != None):
                num = 0
            elif (re.search(r".*か月以内に発送.*", num_text) != None):
                num = 0
            else:
                num = 0
        product_info_list.append(num)
        println(u'num--宝贝数量: %s' % num)

        # 3.11 有效期
        valid_thru = 7
        product_info_list.append(valid_thru)
        # println(u'valid_thru--有效期: %s' % valid_thru)

        # 3.12 运费承担
        freight_payer = 2
        product_info_list.append(freight_payer)
        # println(u'freight_payer--运费承担: %s' % freight_payer)

        # 3.13 平邮
        post_fee = 0
        product_info_list.append(post_fee)
        # println(u'post_fee--平邮: %s' % post_fee)

        # 3.14 EMS
        ems_fee = 2
        product_info_list.append(ems_fee)
        # println(u'ems_fee--EMS: %s' % ems_fee)

        # 3.15 快递
        express_fee = 0
        product_info_list.append(express_fee)
        # println(u'express_fee--快递: %s' % express_fee)

        # 3.16 发票
        has_invoice = 1
        product_info_list.append(has_invoice)
        # println(u'has_invoice--发票: %s' % has_invoice)

        # 3.17 保修
        has_warranty = 1
        product_info_list.append(has_warranty)
        # println(u'has_warranty--保修: %s' % has_warranty)

        # 3.18 放入仓库
        approve_status = 1
        product_info_list.append(approve_status)
        # println(u'approve_status--放入仓库: %s' % approve_status)

        # 3.19 橱窗推荐
        has_showcase = 0
        product_info_list.append(has_showcase)
        # println(u'has_showcase--橱窗推荐: %s' % has_showcase)

        # 3.20 开始时间
        list_time = u''
        product_info_list.append(list_time)
        # println(u'list_time--开始时间: %s' % list_time)

        # 3.21 商品描述
        # 品牌
        brand = ''
        brand_node = bs_obj.find('', {'id': 'brand'})
        if brand_node and len(brand_node) > 0:
            brand = brand_node.get_text().strip().replace('\'', '')
        println(u'brand--品牌: %s' % brand)

        # 产品特点
        feature_list = []
        feature_node = bs_obj.find('', {'id': 'feature-bullets'})
        if feature_node and len(feature_node) > 0:
            for feature_text in feature_node.find_all('span', {'class': 'a-list-item'}):
                if feature_text != '\n':
                    feature = reg_replace.sub('', feature_text.get_text().strip())
                    feature_list.append(feature)
        print(u'feature_list--产品特点: ')
        println(feature_list)

        # 图片地址
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

        # aplus_list描述
        aplus_list = []
        aplus_node = bs_obj.find('div', id=re.compile(".*aplus_feature_div.*"))
        if aplus_node and len(aplus_node) > 0:
            image_head_deleted_content = delete_img_head_reg.sub('', aplus_node.prettify())
            html_head_deleted_content = delete_html_head_reg.sub('', image_head_deleted_content).replace(' ', '').strip('\n')
            aplus_list_temp = delete_n_reg.split(html_head_deleted_content)
            for aplus_item in aplus_list_temp:
                if re.search('http', aplus_item) == None:
                    aplus_temp = reg_replace.sub('', aplus_item)
                else:
                    aplus_temp = re.search(r"http.*(jpg|png)", aplus_item).group(0)
                aplus_list.append(aplus_temp)
        print(u'aplus_list--描述: ')
        println(aplus_list)

        # 商品问答环
        question_list = []
        question_node = bs_obj.find('', id=re.compile(".*ask-btf_feature_div.*"))
        if question_node and len(question_node) > 0:
            html_head_deleted_content_question = delete_html_head_reg.sub('', question_node.prettify()).replace(' ','').strip('\n')
            question_list_temp = delete_n_reg.split(html_head_deleted_content_question)
            for question_item in question_list_temp:
                if re.search('http', question_item) == None:
                    question_temp = reg_replace.sub('', question_item)
                else:
                    question_temp = re.search(r"http.*(jpg|png)", question_item).group(0)
                question_list.append(question_temp)
        print(u'question_dict--商品问答环节: ')
        println(question_list)

        # 客户评论
        comment_list = []
        comment_node = bs_obj.find('', id=re.compile(".*customer-reviews_feature_div.*"))
        if comment_node and len(comment_node) > 0:
            image_head_deleted_content_comment = delete_img_head_reg.sub('', comment_node.prettify())
            html_head_deleted_content_comment = delete_html_head_reg.sub('', image_head_deleted_content_comment).replace(' ', '').strip('\n')
            comment_list_temp = delete_n_reg.split(html_head_deleted_content_comment)
            for comment_item in comment_list_temp:
               if re.search('http', comment_item):
                    comment_temp = re.search(r"http.*(jpg|png)", comment_item).group(0)
                    comment_list.append(comment_temp)
        print(u'comment_image_list--客户图片评论: ')
        println(comment_list)

        # 添加描述信息*************************************
        description = genDescription(feature_list, image_list, pd_list, aplus_list, comment_list)
        product_info_list.append(description)
        print(u'description--描述模块: ')
        println(description)

        # 新图片下载与路径写入csv*************************************
        asin_number = asin_temp
        thread = threading.Thread(target=genImage, name=str(asin_number), args=(image_list, str(asin_number)))
        thread.setDaemon(True)
        thread.start()
        # time.sleep(20)
        thread.join()

        # 3.22 宝贝属性
        cateProps = u''
        product_info_list.append(cateProps)
        # println(u'cateProps--宝贝属性: %s' % cateProps)

        # 3.23 邮费模版ID
        postage_id = u'5352276030'
        product_info_list.append(postage_id)
        # println(u'postage_id--邮费模版ID: %s' % postage_id)

        # 3.24 会员打折
        has_discount = 0
        product_info_list.append(has_discount)
        # println(u'has_discount--会员打折: %s' % has_discount)

        # 3.25 修改时间
        modified = list_time
        product_info_list.append(modified)
        # println(u'modified--修改时间: %s' % modified)

        # 3.26 上传状态
        upload_fail_msg = u''
        product_info_list.append(upload_fail_msg)
        # println(u'upload_fail_msg--上传状态: %s' % upload_fail_msg)

        # 3.27 图片状态
        picture_status = u'1;1;1;1;1;'
        product_info_list.append(picture_status)
        # println(u'picture_status--图片状态: %s' % picture_status)

        # 3.28 返点比例
        auction_point = u'0'
        product_info_list.append(auction_point)
        # println(u'auction_point--返点比例: %s' % auction_point)

        # 3.29 新图片
        picture = u''
        new_picture_temp = '805567564a7cbdc' + str(asin_number) + 'i1' + ':1:i2:|;'
        for i in list(range(len(image_list))):
            if i < 10:
                i1 = '0' + str(i)
            else:
                i1 = str(i)
            i2 = str(i)
            picture += new_picture_temp.replace('i1', i1).replace('i2', i2)
        product_info_list.append(picture)
        print(u'picture--新图片: ')
        println(picture)

        # 3.30 视频
        video = u''
        product_info_list.append(video)
        # println(u'video--视频: %s' % video)

        # 3.31 销售属性组合
        skuProps = 1
        product_info_list.append(skuProps)
        # println(u'skuProps--销售属性组合: %s' % skuProps)

        # 3.32 用户输入ID串
        inputPids = u''
        product_info_list.append(inputPids)
        # println(u'inputPids--用户输入ID串: %s' % inputPids)

        # 3.33 用户输入名-值对
        inputValues = u''
        product_info_list.append(inputValues)
        # println(u'inputValues--用户输入名-值对: %s' % inputValues)

        # 3.34 商家编码
        outer_id = asin_temp
        product_info_list.append(outer_id)
        println(u'outer_id--商家编码: %s' % outer_id)

        # 3.35 销售属性别名
        propAlias = u''
        product_info_list.append(propAlias)
        # println(u'propAlias--销售属性别名: %s' % propAlias)

        # 3.36 代充类型
        auto_fill = u''
        product_info_list.append(auto_fill)
        # println(u'auto_fill--代充类型: %s' % auto_fill)

        # 3.37 数字ID
        num_id = u'543000000000'
        product_info_list.append(num_id)
        # println(u'num_id--数字ID: %s' % num_id)

        # 3.38 本地ID
        local_cid = 1
        product_info_list.append(local_cid)
        # println(u'local_cid--本地ID: %s' % local_cid)

        # 3.39 宝贝分类
        navigation_type = 2
        product_info_list.append(navigation_type)
        # println(u'navigation_type--宝贝分类: %s' % navigation_type)

        # 3.40 用户名称
        user_name = u'scjmanbuman'
        product_info_list.append(user_name)
        # println(u'user_name--用户名称: %s' % user_name)

        # 3.41 宝贝状态
        syncStatus = 1
        product_info_list.append(syncStatus)
        # println(u'syncStatus--宝贝状态: %s' % syncStatus)

        # 3.42 闪电发货
        is_lighting_consigment = 252
        product_info_list.append(is_lighting_consigment)
        # println(u'is_lighting_consigment--闪电发货: %s' % is_lighting_consigment)

        # 3.43 新品
        is_xinpin = 248
        product_info_list.append(is_xinpin)
        # println(u'is_xinpin--新品: %s' % is_xinpin)

        # 3.44 食品专项
        foodparame = u''
        product_info_list.append(foodparame)
        # println(u'foodparame--食品专项: %s' % foodparame)

        # 3.45 尺码库
        features = ''
        product_info_list.append(features)
        # println(u'features--尺码库: %s' % features)

        # 3.46 采购地
        buyareatype = 1
        product_info_list.append(buyareatype)
        # println(u'buyareatype--采购地: %s' % buyareatype)

        # 3.47 库存类型
        global_stock_type = 1
        product_info_list.append(global_stock_type)
        # println(u'global_stock_type--库存类型: %s' % global_stock_type)

        # 3.48 国家地区
        global_stock_country = u'日本'
        product_info_list.append(global_stock_country)
        # println(u'global_stock_country--国家地区: %s' % global_stock_country)

        # 3.49 库存计数
        sub_stock_type = 1
        product_info_list.append(sub_stock_type)
        # println(u'sub_stock_type--库存计数: %s' % sub_stock_type)

        # 3.50 物流体积
        item_size = 1
        product_info_list.append(item_size)
        # println(u'item_size--物流体积: %s' % item_size)

        # 3.51 物流重量
        item_weight = str(round(((packet_total_weight) / 1000), 1))
        product_info_list.append(item_weight)
        println(u'item_weight--物流重量: %s' % item_weight)

        # 3.52 退换货承诺
        sell_promise = 0
        product_info_list.append(sell_promise)
        # println(u'sell_promise--退换货承诺: %s' % sell_promise)

        # 3.53 定制工具
        custom_design_flag = u''
        product_info_list.append(custom_design_flag)
        # println(u'custom_design_flag--定制工具: %s' % custom_design_flag)

        # 3.54 无线详情
        wireless_desc = genWirelessDesc(title, feature_list, image_list, pd_list, aplus_list, comment_list)
        product_info_list.append(wireless_desc)
        print(u'wireless_desc--无线详情: ')
        println(wireless_desc)

        # 3.55 商品条形码
        barcode = u''
        product_info_list.append(barcode)
        # println(u'barcode--商品条形码: %s' % barcode)

        # 3.56 条形码
        sku_barcode = u''
        product_info_list.append(sku_barcode)
        # println(u'sku_barcode--条形码: %s' % sku_barcode)

        # 3.57 7天退货
        newprepay = 0
        product_info_list.append(newprepay)
        # println(u'newprepay--7天退货: %s' % newprepay)

        #3.58 宝贝卖点
        subtitle_temp = str()
        for text in feature_list:
            subtitle_temp += text
        subtitle = subtitle_temp[0:139]
        product_info_list.append(subtitle)
        println(u'subtitle--宝贝卖点: %s' % subtitle)

        # 3.59 属性值备注
        cpv_memo = 0
        product_info_list.append(cpv_memo)
        # println(u'cpv_memo--属性值备注: %s' % cpv_memo)

        # 3.60 自定义属性值
        input_custom_cpv = 0
        product_info_list.append(input_custom_cpv)
        # println(u'input_custom_cpv--自定义属性值: %s' % input_custom_cpv)

        # 3.61 商品资质
        qualification = 0
        product_info_list.append(qualification)
        # println(u'qualification--商品资质: %s' % qualification)

        # 3.62 增加商品资质
        add_qualification = 0
        product_info_list.append(add_qualification)
        # println(u'add_qualification--增加商品资质: %s' % add_qualification)

        # 3.63 关联线下服务
        o2o_bind_service = 0
        product_info_list.append(o2o_bind_service)
        # println(u'o2o_bind_service--关联线下服务: %s' % o2o_bind_service)

        print(u'商品信息列表形式: ')
        println(product_info_list)

        # 返回获取的数据结果
        return product_info_list





