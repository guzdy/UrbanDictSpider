# UrbanDictionarySpider

这是 [UrbanDictionary](http://www.urbandictionary.com/) 爬取软件。
通过对之前保存到数据库的ProxyPool的合理利用，避免爬取数据过程中的IP被封等影响效率的部分。
使用Redis进行 Proxy Queue ; 使用多线程及 Asyncio 来保证爬取速度。

计划的数据爬取完成（8万多个Document, 1个半小时），但代码细节还待优化。