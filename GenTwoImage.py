# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import os
import urllib.request


# 2 ----------------常量定义
image_list = ['https://img.alicdn.com/imgextra/i1/32546558/TB25W7YbX5N.eBjSZFmXXboSXXa_!!32546558.jpg',\
              'https://img.alicdn.com/imgextra/i3/32546558/TB26DH4aW9I.eBjy0FeXXXqwFXa_!!32546558.jpg']
name = ['Static_images/image_start.jpg', 'Static_images/image_end.jpg']


# 3 ----------------生成tbi格式图片
def genTwoImage():
    for i in list(range(len(image_list))):
        if not os.path.exists(name[i]):
            urllib.request.urlretrieve(image_list[i], name[i])

# 3.1 ----------------方法测试
# genTwoImage()