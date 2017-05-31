from lxml import etree
import requests
from database import Redis_db, Mongo_db
import pickle
import random
import asyncio
from functools import partial

with open(r'D:\DATA\useragent.pkl', 'rb') as f:
    ua = pickle.load(f)

redis = Redis_db()
mongo = Mongo_db()

# 把函数调入作为参数
async def _async_crawl():
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, craw_detail, redis.pop_href) for i in range(redis.hrefs_len())]
    return await asyncio.gather(*tasks)


def async_crawl():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_crawl())


# 控制函数, headers 和 其他参数
def craw_detail(href, num = 1, headers = None, cookies = None, more_page = True):

    # 如果是函数, 获取返回值
    if callable(href):
        href = href()
        more_page = False

    proxy = redis.get_proxy()
    url = 'http://www.urbandictionary.com' + href
    if headers:
        headers = {
            "Host": "www.urbandictionary.com",
            "User-Agent": random.choice(ua),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,ko;q=0.6,en;q=0.4,zh-TW;q=0.2",
            "Accept-Encoding": "gzip, deflate, sdch"
        }
    try:
        content,cookies = urldownload(url,proxy, headers, cookies)
    except:
        print('下载失败, 重试. %s' %url)
        return craw_detail(href)
    else:
        print('下载成功, 准备抓取. %s' % url)
        return parse_detail(content, num, headers , cookies, more_page)

# 下载函数
def urldownload(url, proxy, headers, cookies):
    proxies = {'html': proxy}
    resp = requests.get(url, proxies=proxies, headers = headers, cookies = cookies)
    if resp.status_code != 200:
        raise "requests Error %s" % resp.status_code
    cookies = resp.cookies
    return resp.text, cookies


def parse_detail(content, num, headers, cookies, more_page):
    html = etree.HTML(content)

    panels = html.xpath('//div[@class = "def-panel"]')
    data_list = []
    print('Ready to parse.')
    for panel in panels:
        word = panel.xpath('string(./div[@class = "def-header"]/a[@class = "word"])')
        meaning = panel.xpath('string(./div[@class = "meaning"])')
        example = panel.xpath('string(./div[@class = "example"])')
        contributor = panel.xpath('string(./div[@class = "contributor"]/a)')
        date = panel.xpath('./div[@class = "contributor"]/text()')[1].strip()
        thumbs_up = panel.xpath('number(.//div[@class = "thumbs"]/a[@class = "up"]/span)')
        thumbs_down = panel.xpath('number(.//div[@class = "thumbs"]/a[@class = "down"]/span)')
        up_proportion = (thumbs_up / thumbs_up + thumbs_down) if (thumbs_up + thumbs_down) else 'N/A'
        data = {'word': word, 'meaning': meaning, 'example': example,
                'contributor': contributor, 'date': date, 'up_proportion': up_proportion,
                'thumbs_up': thumbs_up, 'thumbs_down': thumbs_down,'num':num }

        try:
            gif = panel.xpath('./div[@class = "gif"]/img/@src')[0]
        except:
            pass
        else:
            data['gif'] = gif
        print('Parse data:',data)

        data_list.append(data)
        num += num

    print('Mongo数据库里插入数据 %s' %data_list)
    mongo.insert_many_words(data_list)
    counts = len(data_list)

    if more_page:
        a_content_raw = html.xpath('//a/@href')
        a_content = [i.lower() for i in a_content_raw if i.startswith('/define.php?term=') and '&page=' not in i]
        redis.insert_hrefs_others(a_content)
        print('Detail href_list %s' % a_content)
        page_content = {i.lower() for i in a_content_raw if i.startswith('/define.php?term=') and '&page=' in i}

        print('Check more page content:', page_content)

        # 如果有额外的页数, 增加内容, 限制 5 页, 不再爬取更多页内容

        if page_content:
            for href in page_content:
                counts += craw_detail(href, num,headers, cookies, more_page= False)

    return counts