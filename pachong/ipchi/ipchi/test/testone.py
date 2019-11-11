# -*- utf-8 -*-
# 代理检测 手动

import requests

def main():
    proxies = {'http': 'http://119.179.162.27:8060'}

    #url = 'http://www.baidu.com'
    url = 'http://httpbin.org/ip'
    response = requests.get(url, proxies=proxies, timeout=2)
    print(response.text)


if __name__ == '__main__':
    main()