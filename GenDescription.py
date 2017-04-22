# -*- coding: utf-8 -*-


# 1 ----------------导入模块
from GenLocalImage import *


# 2 ----------------常量定义
image_begin = sys.path[0] + '/Static_images/image_start.jpg'
image_end = sys.path[0]+ '/Static_images/image_end.jpg'
div_begin = '<div class="a-section a-spacing-medium a-spacing-top-small">'
div_end = '</div>'
img_rep = 'image_link'
img = '<img src="image_link">'
ul_begin = '<ul class="a-vertical a-spacing-none">'
ul_end = '</ul>'
li_begin = '<li><span class="a-list-item">'
li_end = '</span></li>'
br = '<br/>'


# 3 ----------------添加换行符
def addEnter(text):
    return text + '\n'


# 4 ----------------添加换行符
def genDescription(feature_list, image_list, pd_list, aplus_list, comment_list):
    description = addEnter(div_begin)

    # 商家开始图片
    description += addEnter(img.replace(img_rep, image_begin))

    # 商品特点
    if feature_list and len(feature_list) > 0:
        description += addEnter(br)
        description += addEnter(br)
        description += addEnter(br)
        description += addEnter('商品特点：')
        description += addEnter(ul_begin)
        for feature in feature_list:
            if u'请输入型号验证' not in feature:
                description += li_begin
                description += feature
                description += addEnter(li_end)
        description += addEnter(ul_end)

    # 商品图片
    if image_list and len(image_list) > 0:
        description += addEnter(br)
        description += addEnter('商品图片：')
        for image in image_list:
            description += addEnter(br)
            local_image = genLocalImage(image, 750)
            description += addEnter(img.replace(img_rep, local_image))

    # 商品图片描述1
    if pd_list and len(pd_list) > 0:
        description += addEnter(br)
        description += addEnter('商家图片1：')
        for image in pd_list:
            if 'http' in image:
                description += addEnter(br)
                local_image = genLocalImage(image, 750)
                description += addEnter(img.replace(img_rep, local_image))

    # 商品图片描述2
    if aplus_list and len(aplus_list) > 0:
        description += addEnter(br)
        description += addEnter('商家图片2：')
        for image in aplus_list:
            if 'http' in image:
                description += addEnter(br)
                local_image = genLocalImage(image, 750)
                description += addEnter(img.replace(img_rep, local_image))

    # 评论
    if comment_list and len(comment_list) > 0:
        description += addEnter(br)
        description += addEnter('评论图片：')
        for image in comment_list:
            if 'http' in image:
                description += addEnter(br)
                local_image = genLocalImage(image, 750)
                description += addEnter(img.replace(img_rep, local_image))

    # 商家末尾图片
    description += addEnter(br)
    description += addEnter(img.replace(img_rep, image_end))

    description += div_end

    return description

# 4.1 方法测试
# genDescription(None, None, None, None, None)