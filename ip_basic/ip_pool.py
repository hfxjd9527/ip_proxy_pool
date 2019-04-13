# -*- coding: utf-8 -*-
# @AuThor  : frank_lee
import requests
from scrapy.selector import Selector
import MySQLdb.cursors
import random
conn = MySQLdb.connect(
    host="127.0.0.1",
    user="root",
    passwd="",
    charset="utf8")
cursor = conn.cursor()


def handle_mysql():
    # 创建数据库，如果不存在则创建该数据库
    cursor.execute("create database if Not Exists ip_pool character set utf8;")
    # 进入该数据库
    cursor.execute("use ip_pool;")
    # 创建数据表
    # 创建一个表
    sql = """create table  If Not Exists iptable (
              ip_addr varchar(50) not null ,
              ip_port varchar(20) not null
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
    except BaseException:
        # 如果发生错误则回滚
        conn.rollback()
    # mysql部分结束


def crawl_ips():
    # user_agent列表
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36']
    headers = {'User-Agent': random.choice(user_agent_list)}
    j = 1
    ip_list = []
    while j < 20:
        url = "http://www.66ip.cn/{0}.html".format(j)
        data = requests.get(url=url, headers=headers)
        response = Selector(text=data.text)
        tr = response.css("#main > div > div:nth-child(1) > table > tr")

        for line in tr[1:]:
            ipinfo_list = line.css("td::text")
            ip_addr = ipinfo_list[0].extract()
            ip_port = ipinfo_list[1].extract()
            ip_list.append((ip_addr, ip_port))
        print("我刚刚爬了第{}页".format(j))
        j += 1
    return ip_list


if __name__ == '__main__':
    handle_mysql()
    ip_list = crawl_ips()
    for ip_info in ip_list:
        cursor.execute(
            # 如果已存在相应记录则忽略该条数据
            "insert ignore into iptable(ip_addr, ip_port) values('{0}', '{1}')".format(ip_info[0],
                                                                                       ip_info[1])
        )
        conn.commit()
