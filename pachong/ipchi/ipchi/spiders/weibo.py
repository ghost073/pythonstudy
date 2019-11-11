# -*- coding: utf-8 -*-
# 
# 参考： https://www.jianshu.com/p/36a39ea71bfd
# https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTIzNDU2&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1573466530670
# 
import scrapy
from scrapy import Request
import urllib
import base64
import json

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['www.weibo.com', 'login.sina.com.cn']
    start_urls = ['https://www.weibo.com/']

    prelogin_url_pre = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={username}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1573466530670'

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": { 
            'Host':'login.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
        "DOWNLOADER_MIDDLEWARES": {
            'ipchi.middlewares.RandomUserAgentMiddleware': 543
        }
    }

    # 开始请求, 先获得请求参数，cookie
    def start_requests(self):
        username = 'wb_develop@sina.cn'
        su = self.get_su(username)
        prelogin_url = self.prelogin_url_pre.format(username = su)
        yield Request(url=prelogin_url, callback=self.prelogin)

    # 登录预处理
    def prelogin(self, response):
        res = response.text.replace('sinaSSOController.preloginCallBack(', '')
        res = res[:-1]
        zidian = json.loads(res)
        self.logger.info(zidian['retcode'])

    def parse(self, response):
        pass


    # 加密方式
    # http://login.sina.com.cn/js/sso/ssologin.js
    # 获得登陆的加密用户名
    def get_su(self, user_name):
        username_ = urllib.request.quote(user_name) # html字符转义
        username = str(base64.b64encode(username_.encode(encoding='utf-8')), 'utf-8')
        return username

    # 获得加密的密码
    def get_sp_rsa(self, passwd, servertime, nonce):
        # 这个值可以在prelogin得到,因为是固定值,所以写死在这里
        weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
        weibo_rsa_e = 65537 # 10001对应的10进制
        message = str(servertime)+'\t'+str(nonce)+'\n'+passwd
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)
        encropy_pwd = rsa.encrypt(message, key)
        new_pwssword = binascii.b2a_hex(encropy_pwd)
        return new_pwssword