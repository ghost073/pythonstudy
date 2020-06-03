# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import sqlite3
import os
import time

from scrapy.http import HtmlResponse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class IpchiSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IpchiDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class RandomUserAgentMiddleware(object):
    """ 随机更换浏览器头 """
    def __init__(self, user_agent):
        self.user_agent = user_agent


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent = crawler.settings.getlist('USER_AGENT')
            )

    def process_request(self, request, spider): 
        user_agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = user_agent

        return None


# 代理IP池
class RandomProxyMiddleware(object):
    """ 随机更换代理IP """
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        db_dir = os.getcwd()+'/pachong.db'
        # 链接sqlite3 数据库
        conn = sqlite3.connect(db_dir)
        # 设置row 返回字典格式
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        conn.row_factory = dict_factory

        cursor = conn.cursor()
        # 取出所有可用IP
        sel_sql = 'select * from ip where is_active=1'
        cursor.execute(sel_sql)
        ip_arr = cursor.fetchall()
        conn.close()

        return cls(
            proxies = ip_arr
            )

        
    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        proxy_str = '{0}://{1}:{2}'.format(proxy['leixing'].lower(), proxy['ip'], proxy['port'])
        request.meta['proxy'] = proxy_str
        
        spider.logger.info('proxy ip is:{}'.format(proxy_str))

        return None

# selenium 浏览器登录
class SeleniumMiddleware(object):
    """ 
        selenium 登录中间件 
    """

    ''' 
    引擎将上步中得到的请求（Requests）通过下载器中间件（Downloader Middlewares）发送给下载器（Downloader ）,这个过程中下载器中间件（Downloader Middlewares）中的process_request()函数会被调用到.
    '''
    def process_request(self, request, spider):
        # 依靠meta中的标记，来决定是否需要使用selenium来爬取
        usedSelenium = request.meta.get('usedSelenium', False)
        if usedSelenium:
            if request.meta.get('pageType', '') == 'login':
                # 先存储原始的url链接
                originalUrl = request.url

                try:
                    #options = webdriver.chrome.options.Options()
                    options = webdriver.ChromeOptions()
 
                    prefs = {
                        'profile.default_content_setting_values' : {
                            'images' : 2
                        }
                    }
                    options.add_experimental_option('prefs',prefs)

                    #options.add_argument('user-agent=%s'%user_ag)
                    # 无头模式
                    #options.add_argument('--headless')
                    #options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
                    options.add_argument('--disable-infobars') #隐藏"Chrome正在受到自动软件的控制"
                    options.add_argument('--start-maximized')
                    # 启动webdriver
                    driver = webdriver.Chrome(executable_path=spider.driver_executable_path, chrome_options=options)
                    # 打开登录页
                    driver.get(originalUrl)

                    wait = WebDriverWait(driver, 25)  # 指定元素加载超时时间
                    driver.set_page_load_timeout(20) #页面加载超时时间
                    # 最大化浏览器，有的元素遮挡无法显示
                    #driver.maximize_window()
                    
                    # 等待登录框出现
                    usernameInput = wait.until(
                        EC.presence_of_element_located((By.ID, "loginname"))
                    )

                    #usernameInput = driver.find_element_by_id('loginname')

                    # 输入用户名密码
                    usernameInput.send_keys(spider.unifo['username'])
                    driver.find_element_by_name("password").send_keys(spider.unifo['password'])
                    driver.find_element_by_class_name("login_btn").click()

                except Exception as e:
                    # 登录过程中出错
                    print(f"chrome user login handle error, Exception = {e}")
                    return HtmlResponse(url=request.url, status=500, request=request)
                else:

                    time.sleep(3)
                    # 跳转以后获得所有cookie
                    # 获得登录cookie
                    seleniumCookies = driver.get_cookies()

                    # 登录成功，传递cookie给下一次请求
                    cookie = [item['name']+':'+item['value'] for item in seleniumCookies]
                    cookMap = {}
                    for elem in cookie:
                        cookstr = elem.split(':')
                        cookMap[cookstr[0]] = cookstr[1]

                    # 中间件，对Request进行加工
                    # 开始用这个转换后的cookie重新构造Request，从源码中来看Request构造的原型
                    # Lib\site-packages\scrapy\http\request\__init__.py
                    request.cookies = cookMap # 让这个带有登录后cookie的Request继续爬取
                    request.meta['usedSelenium'] = False # 避免这个url发生重定向302，里面的meta信息会让它回到这个流程
                    
                    time.sleep(1)
                    # html源码
                    #html = driver.page_source
                    # 退出
                    #driver.quit()
                    #return HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')
                    


# selenium 浏览器登录
class SeleniumFirfoxMiddleware(object):
    """ 
        selenium 登录中间件 
    """

    ''' 
    引擎将上步中得到的请求（Requests）通过下载器中间件（Downloader Middlewares）发送给下载器（Downloader ）,这个过程中下载器中间件（Downloader Middlewares）中的process_request()函数会被调用到.
    '''
    def process_request(self, request, spider):
        # 依靠meta中的标记，来决定是否需要使用selenium来爬取
        usedSelenium = request.meta.get('usedSelenium', False)
        if usedSelenium:
            if request.meta.get('pageType', '') == 'login':
                # 先存储原始的url链接
                originalUrl = request.url

                try:
                    #options = webdriver.chrome.options.Options()
                    #options = webdriver.ChromeOptions()
                    options = webdriver.FirefoxOptions()

                    #options.add_argument('user-agent=%s'%user_ag)
                    # 无头模式
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
                    options.add_argument('--disable-infobars') #隐藏"Chrome正在受到自动软件的控制"
                    options.add_argument('--start-maximized')
                    # 启动webdriver
                    #driver = webdriver.Chrome(executable_path=spider.driver_executable_path, chrome_options=options)
                    
                    driver = webdriver.Firefox(executable_path=spider.driver_executable_path, firefox_options=options)
                    # 打开登录页
                    driver.get(originalUrl)

                    wait = WebDriverWait(driver, 25)  # 指定元素加载超时时间
                    driver.set_page_load_timeout(20) #页面加载超时时间
                    # 最大化浏览器，有的元素遮挡无法显示
                    #driver.maximize_window()
                    
                    # 等待登录框出现
                    usernameInput = wait.until(
                        EC.presence_of_element_located((By.ID, "loginname"))
                    )

                    #usernameInput = driver.find_element_by_id('loginname')

                    # 输入用户名密码
                    usernameInput.send_keys(spider.unifo['username'])
                    driver.find_element_by_name("password").send_keys(spider.unifo['password'])
                    driver.find_element_by_class_name("login_btn").click()

                except Exception as e:
                    # 登录过程中出错
                    print(f"chrome user login handle error, Exception = {e}")
                    return HtmlResponse(url=request.url, status=500, request=request)
                else:

                    time.sleep(3)
                    # 跳转以后获得所有cookie
                    # 获得登录cookie
                    seleniumCookies = driver.get_cookies()

                    # 登录成功，传递cookie给下一次请求
                    cookie = [item['name']+':'+item['value'] for item in seleniumCookies]
                    cookMap = {}
                    for elem in cookie:
                        cookstr = elem.split(':')
                        cookMap[cookstr[0]] = cookstr[1]

                    # 中间件，对Request进行加工
                    # 开始用这个转换后的cookie重新构造Request，从源码中来看Request构造的原型
                    # Lib\site-packages\scrapy\http\request\__init__.py
                    request.cookies = cookMap # 让这个带有登录后cookie的Request继续爬取
                    request.meta['usedSelenium'] = False # 避免这个url发生重定向302，里面的meta信息会让它回到这个流程
                    
                    time.sleep(1)
                    # html源码
                    #html = driver.page_source
                    # 退出
                    #driver.quit()
                    #return HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')