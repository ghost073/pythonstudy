# -*- utf-8 -*-
# 代理检测

import requests

ip = '117.30.113.164'
port = '9999'
protocol = 'https'

proxies = {'all': protocol+'://'+ip+':'+port}

response  = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=2)
response.encoding = 'utf-8'
s = response.text
print(s)