# -*- coding: UTF-8 -*-


import pymysql


def queryCategoryInfo():
    try:
        #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
        conn = pymysql.connect(host='amazondata.mysql.rds.aliyuncs.com', user='root', passwd='1qaz2wsx@12',
                             db='amazondata', port=3306, charset='utf8')
        cur = conn.cursor()

        cur.execute('select * from category')
        conn.commit()

        data = cur.fetchall()
        for d in data :
            print(d)

        cur.close()
        conn.close()
    except Exception as e:
        print(e)

queryCategoryInfo()


# 创建数据表
# cur.execute("create table student(id int ,name varchar(20),class varchar(30),age varchar(10))")
# 插入一条数据
# cur.execute("insert into student values('2','Tom','3 year 2 class','9')")
# sqli = "insert into category values(%s, %s, %s)"
# cur.execute(sqli, ('Huhu', '2 year 1 class', '7'))
# 修改查询条件的数据
# cur.execute("update student set class='3 year 1 class' where name = 'Tom'")
# 删除查询条件的数据
# cur.execute("delete from student where age='9'")