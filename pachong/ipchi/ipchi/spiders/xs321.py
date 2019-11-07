# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ipchi.items import Xs321Item

class Xs321Spider(scrapy.Spider):
    name = 'xs321'
    allowed_domains = ['m.xs321.com']

    start_urls = ['https://m.xs321.com/160_160011/all.html']
    base_url = 'https://m.xs321.com'

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": { 
            'Host':'m.xs321.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'http://m.xs321.com/'
        },
        "DOWNLOADER_MIDDLEWARES": {
            'ipchi.middlewares.RandomUserAgentMiddleware': 543,
            #'ipchi.middlewares.RandomProxyMiddleware': 544,
        },
        "ITEM_PIPELINES": {
            'ipchi.pipelines.JsonPipeline': 301,
        }
    }


    # 取开始页码
    def parse(self, response):
        hrefs = response.css('#chapterlist p a::attr(href)').extract()
        for href in hrefs:
            url = self.base_url + href
            yield Request(url, callback=self.parse_detail)


    # 取详情页
    def parse_detail(self, response):
        item = Xs321Item()
        item['title'] =  response.css('title::text').extract_first()
        item['url'] = response.url
        # 内容
        content_arr =  response.css('#chaptercontent::text').extract()
        content = ''.join(content_arr)
        item['content'] = content

        yield item

        # 主动关闭爬虫
        #self.crawler.engine.close_spider(self, 'response msg error %s, job done!'.format('ok'))