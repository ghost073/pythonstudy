# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ipchi.items import IpItem

class XiciSpider(scrapy.Spider):
    name = 'xici'
    allowed_domains = ['www.xicidaili.com']
    start_urls = ['https://www.xicidaili.com/nn/']
    base_url = 'https://www.xicidaili.com/nn/'
    page = 1

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": { 
            'Host':'www.xicidaili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xicidaili.com/'
        }
    }

    def parse(self, response):
        if self.page >= 3:
            # 主动关闭爬虫
            self.crawler.engine.close_spider(self, 'response msg error %s, job done!'.format('ok'))

        self.page += 1

        table = response.xpath('//table[@id="ip_list"]//tr')
        for tr in table:

            item = IpItem()
            item['ip'] = tr.xpath('td[2]//text()').extract_first()
            item['port'] = tr.xpath('td[3]//text()').extract_first()
            item['address'] = tr.xpath('td[4]/a//text()').extract_first()
            item['is_niming'] = tr.xpath('td[5]//text()').extract_first()
            item['leixing'] = tr.xpath('td[6]//text()').extract_first()
            item['is_active'] = 0

            yield item

        next_page = response.xpath('//div[@class="pagination"]/a[@class="next_page"]//@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(url=next_page, callback=self.parse)


    #css选择器检测
    def parsecss(self, response):
        table = response.css('#ip_list tr')
        for tr in table:
            item = XixiItem()
            item['ip'] = tr.css('td:nth-child(2)::text').extract_first()
            item['port'] = tr.css('td:nth-child(3)::text').extract_first()
            item['address'] = tr.css('td:nth-child(4) a::text').extract_first()
            item['is_niming'] = tr.css('td:nth-child(5)::text').extract_first()
            item['type'] = tr.css('td:nth-child(6)::text').extract_first()
            item['lifetime'] = tr.css('td:nth-child(9)::text').extract_first()
            item['checktime'] = tr.css('td:nth-child(10)::text').extract_first()
            yield item

