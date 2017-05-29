# -*- coding: UTF-8 -*-

import pymysql
try:
    #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
    conn=pymysql.connect(host='amazondata.mysql.rds.aliyuncs.com',user='root',passwd='1qaz2wsx@12',db='amazondata',port=3306,charset='utf8')
    cur=conn.cursor()#获取一个游标
    cur.execute('select * from top100')
    data=cur.fetchall()
    for d in data :
        #注意int类型需要使用str函数转义
        print(d[2])
    cur.close()#关闭游标
    conn.close()#释放数据库资源
except Exception as e:
    print(e)