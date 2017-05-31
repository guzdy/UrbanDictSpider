from lxml import etree
import requests
from database import Redis_db


class SpiderMainPage(object):

    headers = {
        "Host": "www.urbandictionary.com",
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,ko;q=0.6,en;q=0.4,zh-TW;q=0.2",
        "Accept-Encoding": "gzip, deflate, sdch"
    }

    def __init__(self):
        self.redis = Redis_db()
        self.cookies = None

    def crawl(self, url, headers= headers):
        content = self.urldownload(url, headers=headers)
        return self.parse_main(content)

    def urldownload(self, url, headers):
        resp = requests.get(url, headers = headers, cookies = self.cookies)
        self.cookies = resp.cookies
        return resp.text

    def parse_main(self, content):
        html = etree.HTML(content)

        words = html.xpath('//li[@class = "word"]')
        href_list = []
        for word in words:
            href = word.xpath('./a/@href')[0]
            href_list.append(href)
        print('main href_list %s' %href_list)
        self.redis.insert_hrefs_main(href_list)
        print('主页中, 抓取以下信息, %s' %href_list)
        return href_list