# -*- coding: utf-8 -*-


# 1 ----------------模块导入
import urllib.request


# 2 ----------------常量定义
dir_path = 'Item_images'
start_name = dir_path+'/805567564a7cbdc'
format = '.tbi'


# 3 ----------------生成tbi格式图片
def genImage(imageLink_list, asin_number):
    # 下载图片
    i = 0
    for link in imageLink_list:
        if i < 10:
            name = start_name + asin_number + '0' + str(i) + format
        else:
            name = start_name + asin_number + str(i) + format
        urllib.request.urlretrieve(link, name)
        i += 1

# 2.3 ----------------方法测试
# genImage(None, None)