# -*- coding: utf-8 -*-
import scrapy

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait


# scrapy 信号相关库
from scrapy.utils.project import get_project_settings
from scrapy import signals
# scrapy最新采用的方案
from pydispatch import dispatcher

import os
import hashlib
import configparser

class WeiboseleniumloginSpider(scrapy.Spider):
    name = 'weiboseleniumlogin'
    allowed_domains = ['www.weibo.com', 'login.sina.com.cn', 'passport.weibo.com', 'weibo.com']
    start_urls = ['https://weibo.com/']

    cookie_filename = 'weibo_cookies.txt'
    start_url = 'https://weibo.com/'

    # 配置文件中读取
    home_url = ''
    unifo = {'username': '', 'password': ''}

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": { 
            #'Host':'weibo.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
        "DOWNLOADER_MIDDLEWARES": {
            'ipchi.middlewares.SeleniumFirfoxMiddleware': 543,
            # 将scrapy默认的user-agent中间件关闭
            #'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": False,
    }

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("E:\pythonweb\config\weibo.ini")
        self.unifo['username'] = cf.get('weibo-user', 'username')
        self.unifo['password'] = cf.get('weibo-user', 'password')
        self.home_url = cf.get('weibo-user', 'home_url')
        self.driver_executable_path = cf.get('weibo-user', 'driver_executable_path')
        self.myfans_url = cf.get('weibo-user', 'myfans_url')

        # 设置信号量，当收到spider_closed信号时，调用mySpiderCloseHandle方法，关闭chrome
        dispatcher.connect(receiver=self.mySpiderCloseHandle, 
                            signal=signals.spider_closed
                            )

    # 爬虫运行的起始位置
    def start_requests(self):

        # 生成request时，将是否使用selenium下载的标记，放入到meta中
        yield scrapy.Request(
            url = self.start_url,
            meta={'usedSelenium': True, 'pageType': 'login'},
            callback=self.parseLoginRes,
            errback=self.errorHandle,
            #dont_filter=True,  # 防止页面因为重复爬取，被过滤了
            )


    def parseLoginRes(self, response):
        #print(response.request.headers.getlist('Cookie'))
        yield scrapy.Request(
            url=self.myfans_url, 
            callback=self.home,
            meta={'usedSelenium': False, 'dont_redirect': False},
            )

    def errorHandle(self, failure):
        print(f"request error: {failure.value.response}")


    def home(self, response):
        print('home page')
        self.writepage(response)

    # 信号量处理函数：关闭chrome浏览器
    def mySpiderCloseHandle(self, spider):
        self.logger.info('mySpiderCloseHandle: enter')

    # 网页写入文件查看
    def writepage(self, response):
        filename = hashlib.md5(response.url.encode(encoding='UTF-8')).hexdigest()

        with open('%s%s%s' % (os.getcwd(), os.sep, filename+'.html'), 'wb') as f:
            f.write(response.body)
