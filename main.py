import multiprocess
import database
from log_setter import *

import string

from spider.spider_mainpage import SpiderMainPage
from spider import spider_detail

def main():
    mongo = database.Mongo_db()
    redis = database.Redis_db()
    MainPage = SpiderMainPage()

    # 把MongoDB保存的 proxy IP 转到 redis 中准备调用
    redis.insert_proxies(mongo.get_proxies())
    print('Database Setting Complete.')

    alphabet = string.ascii_uppercase
    for i in alphabet:
        # 主页爬取
        url ='http://www.urbandictionary.com/popular.php?character='+ i
        logging.info('crawling %s' %url)
        href_list = MainPage.crawl(url)

        # 详细内容, 多线程, 多IP爬取
        multiprocess.thread(spider_detail.craw_detail, href_list)

    # redis 数据库处理. 剩余部分 to-do
    logging.info('Redis database processing: href_diff ')
    redis.hrefs_diff()

    # 爬取剩余部分, 用 asyncio 异步处理
    logging.info('Crawling Remain Datas')
    spider_detail.async_crawl()


# 运行数据, 并测试运行时间
def exeTime(func, *args, **kwargs):
    t0 = datetime.now()
    func(*args, **kwargs)
    t1 = datetime.now()
    return t1 - t0

if __name__ == '__main__':
    _time = exeTime(main)
    logging.info('Total Time 2: %s' %_time)