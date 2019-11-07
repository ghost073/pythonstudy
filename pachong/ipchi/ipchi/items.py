# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IpItem(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()
    address = scrapy.Field()
    is_niming = scrapy.Field()
    leixing = scrapy.Field()
    is_active = scrapy.Field()


class Xs321Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()