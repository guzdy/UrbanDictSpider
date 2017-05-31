from pymongo import MongoClient
import redis
import datetime

# MongoDB 处理模块
class Mongo_db(object):

    def __init__(self):
        client = MongoClient()
        db_Dict = client.urbanDict
        db_Proxy = client.proxyIP
        self.coll_Dict = db_Dict.maindict
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.coll_Proxy = db_Proxy[today]

    # Dict数据插入
    def insert_many_words(self,data_list):
        self.coll_Dict.insert_many(data_list)

    def get_proxies(self):
        datas = self.coll_Proxy.find()
        return ['http://'+data['_id']+':'+data['port'] for data in datas]

# redis 处理模块
class Redis_db(object):

    def __init__(self):
        self.db = redis.StrictRedis(decode_responses=True)

    # proxy 处理部分, 用 list 循环队列使用
    def insert_proxies(self, data_list, list_name='proxy'):
        self.db.rpush(list_name, *data_list)

    # 左出又进
    def get_proxy(self, list_name='proxy'):
        data = self.db.lpop(list_name)
        self.db.rpush(list_name, data)
        return data


    # url 处理部分, 用 set 帅选重复
    # 收集urls
    def insert_hrefs_main(self, data_list, set_name='url_main'):
        self.db.sadd(set_name,*data_list)

    def insert_hrefs_others(self, data_list, set_name='url_others'):
        self.db.sadd(set_name,*data_list)

    # 获得 set 的差异值, 在未来进行 crawling
    def hrefs_diff(self,set_dest='url_others', set_comp='url_main'):
        self.db.sdiffstore('url_todo',set_dest,set_comp )

    def hrefs_len(self, set_name = 'url_todo'):
        return self.db.scard(set_name)

    def pop_href(self,set_name = 'url_todo'):
        return self.db.spop(set_name)

    def flush_all(self):
        self.db.flushall()


