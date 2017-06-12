# -*- coding: utf-8 -*-
# 1 ----------------模块导入
import os
import sys
from  PIL import Image
import urllib.request
import urllib.error
from Utils import *
import socket
socket.setdefaulttimeout(10)

# 2 ----------------常量定义
sys_path = sys.path[0]
dir_temp_path = sys.path[0] + '/Temp_images/'
dir_path = sys.path[0] + '/Items/'
image_format_left = u'._SL'
image_format_right= u'_'
change_imagesize_reg = re.compile("\._.*_")

def auto_down(url,filename):
    try:
        urllib.request.urlretrieve(url,filename)
    except urllib.error.ContentTooShortError:
        print("Network conditions is not good.Reloading.")
        auto_down(url,filename)
    except Exception as e :
        print("other errors")
        print(e)


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

    auto_down(formated_imageLink, return_name_temp)

    im = Image.open(return_name_temp)
    ori_w, ori_h = im.size
    if (ori_w and ori_w < image_format):
        source_box = (0, 0, int(ori_w), int(ori_h))
        source_region = im.crop(source_box)
        x_shift = int(image_format / 2) - int(ori_w / 2)
        y_shift = 0
        taget_box = (x_shift, y_shift, (ori_w + x_shift), (ori_h + y_shift))
        new_image = Image.new('RGB', (image_format, ori_h), (255, 255, 255))
        new_image.paste(source_region, taget_box)
        new_image.save(return_name, "JPEG", quality=95)

    return return_name

# 3.1 ----------------方法测试
# genLocalImage(None, None)