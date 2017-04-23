# -*- coding: utf-8 -*-


# 1 ----------------导入模块
import os
import csv
import time
import shutil
import threading
from Utils import *
from PullHtmlCmp import pullHtmlCmp
from PullData import pullData
from PushDataCmp import pushDataCmp


# 2 ----------------数据获取与写入
def pullAndPushData(html_url):
    product_info_list = pullData(html_url)
    pushDataCmp(product_info_list)


# 3 ----------------多线程处理
def startMutilThread():
    html_list = pullHtmlCmp()
    print(u'打印网页名称: ')
    println(html_list)
    thread_list = []
    for html_url in html_list:
        thread_list.append(threading.Thread(target=pullAndPushData, args=(html_url,)))
    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()
        time.sleep(20)
    thread.join()


# 4 ----------------初始化方法
if __name__ == '__main__':
    # 重置下载图片目录
    dir_path = 'Item_images'
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)

    dir_path = 'Temp_images'
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)

    # 迭代AllItems.csv文件
    dir_path = 'Htmls/AllItems.csv'
    if os.path.exists(dir_path):
        os.remove(dir_path)
    shutil.copy('AllItems.csv', dir_path)

    # 先写入文件头部4行信息
    item_file1 = open('Htmls/AllItems.csv', 'r')
    item_reader = csv.reader(item_file1)
    dir_path = 'AllItems.csv'
    if os.path.exists(dir_path):
        os.remove(dir_path)
    item_file2 = open('AllItems.csv', 'w', newline='')
    item_writer = csv.writer(item_file2, dialect='excel')
    i = 0
    for row in item_reader:
        item_writer.writerow(row)
        i = i + 1
        if i == 4:
            break
    item_file1.close()
    item_file2.close()

    # 开启多线程获取网页信息
    startMutilThread()