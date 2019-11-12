# -*- coding: utf-8 -*-
# 
# 参考： https://www.jianshu.com/p/36a39ea71bfd
# https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTIzNDU2&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1573466530670
# 
import scrapy
from scrapy import Request
from scrapy.http.cookies import CookieJar    # 该模块继承自内置的http.cookiejar,操作类似
import urllib
import base64
import json
import rsa
import binascii
import re
import os
import configparser

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['www.weibo.com', 'login.sina.com.cn', 'passport.weibo.com', 'weibo.com']
    start_urls = ['https://www.weibo.com/']

    cookie_filename = 'weibo_cookies.txt'
    # 发文博
    add_url = 'https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=1573546930405'
    home_url = ''

    # 配置文件中读取
    cookies = None

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
            #'ipchi.middlewares.RandomUserAgentMiddleware': 543
        },
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": False
    }


    # 开始请求, 先获得请求参数，cookie
    def start_requests(self):

        if self.cookies is None:
            self.cookies = self.readCookie()

        yield Request(url=self.home_url, callback=self.homeback, cookies=self.cookies)


    def home(self):

        yield Request(url=self.home_url, callback=self.homeback, cookies=self.cookies)

    def homeback(self, response):
        print(response.text)


    def addweibo(self):
        '''self.cookies = {
            'SUHB':'0xnTM12yRtDExr',
            'UOR':'login.sina.com.cn,weibo.com,news.ifeng.com',
            'SINAGLOBAL':'7442872261193.7705.1450746188741',
            'ULV':'1573521285000:471:3:2:4604301501980.854.1573521284992:1573464967746',
            'SCF':'AqMS3QHzSN0NOn1I_EMVfmwOOJveDPvuEZxFmzrhIcPpDtugAwJtQxYhjPE0rVr1emSUILC9RS1bFRxL05ijNAg.',
            'SUBP':'0033WrSXqPxfM725Ws9jqgMF55529P9D9WW0AGsAmXm_5zJuw9rf7DUL5JpX5K2hUgL.FozE1K.7e0-RSoz2dJLoIEXLxKqL1KMLBoqLxK-LBo5L1-2LxKqLB.BLB--LxKqLBo-L1h2LxK-LBK5L1hzt',
            'SUB': '_2A25wzk-XDeRhGeRM4lsR8yvEzT6IHXVTuiZfrDV8PUNbmtANLWvZkW9NU6qNihkY2cMMHWRYL_VNgB6UHYdbBKe5',
            'login_sid_t':'be89003deb9167898be6ec2335423305',
            'cross_origin_proto':'SSL',
            'Ugrow-G0':'d52660735d1ea4ed313e0beb68c05fc5',
            'YF-V5-G0':'e8fcb05084037bcfa915f5897007cb4d',
            '_s_tentry':'-',
            'Apache':'4604301501980.854.1573521284992',
            'TC-V5-G0':'595b7637c272b28fccec3e9d529f251a',
            'wb_view_log':'1920*12001',
            'un':'yaojingbukuwww@sina.com',
            'wvr':'6',
            'YF-Page-G0':'bd9e74eeae022c6566619f45b931d426|1573548387|1573548311',
            'wb_view_log_2299035862':'1920*12001',
            'webim_unReadCount':'{"time":1573548398593,"dm_pub_total":29,"chat_group_client":0,"allcountNum":32,"msgbox":0}',
            'ALF':'1605071601',
            'SSOLoginState':'1573535687',
            'wb_timefeed_2299035862':'1',
        }'''
        print(self.cookies)

        post_data = dict(
            location='v6_group_content_home',
            text='真的冷了 降10度',
            appkey='',
            style_type='1',
            pic_id='',
            tid='', 
            pdetail='', 
            mid='', 
            isReEdit='false',
            rank='0',
            rankid='', 
            module='stissue',
            pub_source='main_',
            pub_type='dialog',
            isPri='0',
            _t='0',
            )

        #self.logger.info(post_data)
        # 请求登录
        yield scrapy.FormRequest(
            url = self.add_url,
            formdata = post_data,
            callback = self.addok,
            cookies = self.cookies
            )


    def parse(self, response):
        pass


    # 登录成功
    def addok(self, response):

        self.logger.info(response)
        if response.status == 200:
            self.logger.info('add ok')
        else:
            self.logger.info('add fail')


    # 读取COOKIE
    def readCookie(self):
        cookies_str = None
        with open(self.cookie_filename, 'r') as f:
            cookies_str = f.read()
        if cookies_str is None:
            return None

        cookies_arr = cookies_str.split(';')
        cookies_arr_new = (cookie.strip().split('=', 1) for cookie in cookies_arr)
        cookies_arr_new = dict(cookies_arr_new)
        return cookies_arr_new