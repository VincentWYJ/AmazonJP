# -*- coding: utf-8 -*-


# 1 ----------------导入模块
from GenLocalImage import *

# 2 ----------------常量定义
image_begin = sys.path[0] + '/Static_images/image_start_w.jpg'
image_end = sys.path[0]+ '/Static_images/image_end_w.jpg'
wap_begin = '<wapDesc>'
wap_end = '</wapDesc>'
short = '<shortDesc>short_content</shortDesc>'
short_reg = 'short_content'
txt = '<txt>text_content</txt>'
txt_reg = 'text_content'
img = '<img>img_content</img>'
img_reg = 'img_content'


# 3 ----------------添加换行符
def addEnter(text):
    return text + '\n'


# 4 ----------------添加换行符
def genWirelessDesc(title, feature_list, image_list, pd_list, aplus_list, comment_list):

    description = addEnter(wap_begin)

    # 商品简述
    description += addEnter(short.replace(short_reg, title))

    # 商家开始图片
    description += addEnter(img.replace(img_reg, image_begin))

    # 商品特点
    if feature_list and len(feature_list) > 0:
        for feature in feature_list:
            if u'モデル番号を入力してくださいこれが適合するか確認：' not in feature:
                try:
                    c_feature =translate1(feature)
                except:
                    description += addEnter(txt.replace(txt_reg, feature))
                else:
                    description += addEnter(txt.replace(txt_reg, c_feature))


    # 商品图片
    if image_list and len(image_list) > 0:
        for image in image_list:
            local_image = genLocalImage(image, 600)
            description += addEnter(img.replace(img_reg, local_image))

    # 商品描述1
    if pd_list and len(pd_list) > 0:
        for content in pd_list:
            if re.search(r'.*http.*', content) != None:
                local_image = genLocalImage(content, 600)
                description += addEnter(img.replace(img_reg, local_image))
            else:
                try:
                    c_content = translate1(content)
                except:
                    description += addEnter(txt.replace(txt_reg, content))
                else:
                    description += addEnter(txt.replace(txt_reg, c_content))

    # 商品描述2
    if aplus_list and len(aplus_list) > 0:
        for content in aplus_list:
            if 'http' in content:
                local_image = genLocalImage(content, 600)
                description += addEnter(img.replace(img_reg, local_image))
            else:
                try:
                    c_content = translate1(content)
                except:
                    description += addEnter(txt.replace(txt_reg, content))
                else:
                    description += addEnter(txt.replace(txt_reg, c_content))

    # 评论
    if comment_list and len(comment_list) > 0:
        for content in comment_list:
            if 'http' in content:
                local_image = genLocalImage(content, 600)
                description += addEnter(img.replace(img_reg, local_image))
            else:
                try:
                    c_content = translate1(content)
                except:
                    description += addEnter(txt.replace(txt_reg, content))
                else:
                    description += addEnter(txt.replace(txt_reg, c_content))

    # 商家末尾图片
    description += addEnter(img.replace(img_reg, image_end))

    description += wap_end

    return description

# 4.1 方法测试
# genWirelessDesc("", None, None, None, None, None)