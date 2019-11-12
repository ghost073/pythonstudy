# -*- coding: utf-8 -*-
# 
# 登录获得cookie
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

class WeibologinSpider(scrapy.Spider):
    name = 'weibologin'
    allowed_domains = ['www.weibo.com', 'login.sina.com.cn', 'passport.weibo.com', 'weibo.com']
    start_urls = ['https://www.weibo.com/']

    prelogin_url_pre = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={username}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1573466530670'
    login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
    ajaxlogin_url = 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&sudaref=weibo.com&display=0&retcode=101&reason=用么空间的'
    cookie_filename = 'weibo_cookies.txt'

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
            #'ipchi.middlewares.RandomUserAgentMiddleware': 543
        },
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": False
    }

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("E:\pythonweb\config\weibo.ini") 
        self.unifo['username'] = cf.get('weibo-user', 'username')
        self.unifo['password'] = cf.get('weibo-user', 'password')
        self.home_url = cf.get('weibo-user', 'home_url')
        # 实例化一个cookiejar对象
        #self.cookie_jar = CookieJar()


    # 开始请求, 先获得请求参数，cookie
    def start_requests(self):
        username = self.unifo['username']
        su = self.get_su(username)
        prelogin_url = self.prelogin_url_pre.format(username = su)
        yield Request(url=prelogin_url, callback=self.prelogin, meta={'su':su})

    # 登录预处理
    # 返回值 {'retcode': 0, 'servertime': 1573520958, 'pcid': 'tc-1b5bd681cbd4dc9cddb32b48ccdbe3ceac83', 'nonce': '3KJ0NX', 'pubkey': 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443', 'rsakv': '1330428213', 'is_openlock': 0, 'showpin': 0, 'exectime': 37}
    def prelogin(self, response):
        res = response.text.replace('sinaSSOController.preloginCallBack(', '')
        res = res[:-1]
        zidian = json.loads(res)
        upassword = self.unifo['password']
        # 密码
        password = self.get_sp_rsa(upassword, zidian['servertime'], zidian['nonce'], zidian['pubkey'])
        # 用户名
        #su = self.get_su(self.unifo['username'])
        su = response.meta.get('su')

        post_data = dict(
            entry='weibo',
            gateway=str('1'),
            savestate=str('7'),
            qrcode_flag=str('false'),
            useticket=str('1'),
            pagerefer='',
            vsnf=str('1'),
            su=su,
            service='miniblog',
            servertime=str(zidian['servertime']),
            nonce=zidian['nonce'],
            pwencode='rsa2',
            rsakv=zidian['rsakv'],
            sp=password,
            sr='1920*1200',
            encoding='UTF-8',
            prelt=str('102'),
            url='https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            returntype='META'
            )

        #self.logger.info(post_data)
        # 请求登录
        yield scrapy.FormRequest(
            url = self.login_url,
            formdata = post_data,
            callback = self.loginok,
            )


    def parse(self, response):
        pass


    # 加密方式
    # http://login.sina.com.cn/js/sso/ssologin.js
    # 获得登陆的加密用户名
    def get_su(self, user_name):
        username_zy = urllib.request.quote(user_name) # html字符转义
        username = str(base64.b64encode(username_zy.encode(encoding='utf-8')), 'utf-8')
        return username

    # 获得加密的密码
    def get_sp_rsa(self, passwd, servertime, nonce, weibo_rsa_n):
        # 这个值可以在prelogin得到,因为是固定值,所以写死在这里
        #weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
        weibo_rsa_e = 65537 # 10001对应的10进制
        message = str(servertime)+'\t'+str(nonce)+'\n'+passwd
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)
        message = message.encode('utf-8')
        encropy_pwd = rsa.encrypt(message, key)
        new_pwssword = binascii.b2a_hex(encropy_pwd)
        new_pwssword = str(new_pwssword, 'utf-8')
        return new_pwssword

    # 登录成功
    def loginok(self, response):

        if response.status == 200:
            #还没完！！！这边有一个重定位网址，包含在脚本中，获取到之后才能真正地登陆 
            p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
            try:
                login_url = p.search(response.text).group(1)
                yield Request(url=login_url, callback=self.loginokk)
            except:
                self.logger.info('login error')
        else:
            self.logger.info('login fail')


    def loginokk(self, response):
        # 查看登录结果
        p = re.compile('sinaSSOController\.feedBackUrlCallBack\((.*?)\)')
        okjson = p.search(response.text).group(1)
        if okjson is None:
            self.logger.info('login fail 2')
        else:
            okjson2 = json.loads(okjson)
            if okjson2['result'] == True:
                self.logger.info('login real success')

                # 跳转到首页保存数据
                yield Request(url=self.home_url, callback=self.homepage)
            else:
                self.logger.info('login fail 3')

    # 登录到首页
    def homepage(self, response):
        self.writepage(response)
        #请求Cookie
        self.writeCookie(response)

    # 网页写入文件查看
    def writepage(self, response):
        with open('%s%s%s' % (os.getcwd(), os.sep, 'logged.html'), 'wb') as f:
            f.write(response.body)

    # 写入cookie 新
    def writeCookie(self, response):
        cookie_arr = response.request.headers.getlist('Cookie')
        cookie = str(cookie_arr[0], 'utf-8')
        with open(self.cookie_filename, 'a') as f:
            f.write(cookie+'\n')

    # 写入cookie
    def writeCoookie2(self, response):
        # 保存cookie
        # 到这里我们的登录状态已经写入到response header中的'Set-Cookies'中了,
        # 使用extract_cookies方法可以提取response中的cookie
        self.cookie_jar.extract_cookies(response, response.request)
        # cookiejar是类字典类型的,将它写入到文件中
        with open(self.cookie_filename, 'a+') as f:
            for cookie in self.cookie_jar:
                f.write(str(cookie) + '\n')

    # 读取COOKIE
    def readCookie(self):
        with open(self.cookie_filename, 'r') as f:
            cookiejar = f.read()
            p = re.compile(r'<Cookie (.*?) for .*?>')
            cookies = re.findall(p, cookiejar)
            cookies = (cookie.split('=', 1) for cookie in cookies)
            cookies = dict(cookies)
            return cookies

