# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import os
import sys
from  PIL import Image
import urllib.request
from Utils import *


# 2 ----------------常量定义
sys_path = sys.path[0]
dir_temp_path = sys.path[0] + '/Temp_images/'
dir_path = sys.path[0] + '/Item_images/'
image_format_left = u'._SL'
image_format_right= u'_'
change_imagesize_reg = re.compile("\._.*_")


# 3 ----------------生成tbi格式图片
def genLocalImage(imageLink, image_format):
    return_name_temp = dir_temp_path + imageLink.replace('https://', '').replace('/', '_')
    return_name = dir_path + imageLink.replace('https://', '').replace('/', '_')
    formated_image_format = image_format_left + str(image_format) + image_format_right
    formated_imageLink = change_imagesize_reg.sub(formated_image_format, imageLink)

    # 处理多个图片链接连在一起的情况
    if '"' in return_name_temp:
        return_name_temp = return_name_temp.replace('"', '')

    if '"' in return_name:
        return_name = return_name.replace('"', '')

    if '"' in formated_imageLink:
        formated_imageLink = formated_imageLink[0, formated_imageLink.find('"')] + "'"

    if not os.path.exists(return_name):
        try:
            urllib.request.urlretrieve(formated_imageLink, return_name_temp)
        except:
            urllib.request.urlretrieve(imageLink, return_name_temp)

        try:
            imageopened = Image.open(return_name_temp)
            x,y = imageopened.size
            x_s = image_format
            y_s = int((y / x) * image_format)
            imagesaved = imageopened.resize((x_s, y_s))
            imagesaved.save(return_name)
        except:
            println(u'图片处理模块文件错误')

    return return_name

# 3.1 ----------------方法测试
# genLocalImage(None, None)