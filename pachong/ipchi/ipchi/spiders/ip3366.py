# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ipchi.items import IpItem


class Ip3366Spider(scrapy.Spider):
    name = 'ip3366'
    allowed_domains = ['www.ip3366.net']
    start_urls = ['http://www.ip3366.net/']
    base_url = 'http://www.ip3366.net/'
    page = 1

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": { 
            'Host':'www.ip3366.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'http://www.ip3366.net/'
        },
        "DOWNLOADER_MIDDLEWARES": {
            'ipchi.middlewares.RandomUserAgentMiddleware': 543,
            'ipchi.middlewares.RandomProxyMiddleware': 544,
        }
    }

    def parse(self, response):
        if self.page >= 10:
            self.crawler.engine.close_spider(self, 'response msg error %s, job done!'.format('ok'))

        self.page += 1

        table = response.xpath('//div[@id="list"]//tr')
        for tr in table:

            item = IpItem()
            item['ip'] = tr.xpath('td[1]//text()').extract_first()
            item['port'] = tr.xpath('td[2]//text()').extract_first()
            item['address'] = tr.xpath('td[6]//text()').extract_first()
            item['is_niming'] = tr.xpath('td[3]//text()').extract_first()
            item['leixing'] = tr.xpath('td[4]//text()').extract_first()
            item['is_active'] = 0

            yield item

        next_page = response.xpath('//div[@id="listnav"]//a[text()="下一页"]//@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield Request(url=next_page, callback=self.parse)
