# -*- utf-8 -*-
# ip代理

import sqlite3
import requests
import time
import random
from multiprocessing import Process,Queue

class Proxy(object):

    def __init__(self):
        pass

    # 代理验证
    def verifyPorxy(self):

        print('verify proxy start...')
        # 使用的队列 
        old_queue = Queue()
        success_queue = Queue()
        fail_queue = Queue()

        # 子进程列表
        works = []

        # 生成15个子进程
        # 父进程中的变量，子进程无法使用，使用queue
        for _ in range(15):
            works.append(Process(target=self.verifyProxyOne, args=(old_queue, success_queue, fail_queue)))

        # 启动子进程 
        for work in works:
            work.start()

        success_proxy_ids = []
        fail_proxy_ids = []
        # 进程old_queue 队列中插入数据
        # 链接sqlite3 数据库
        conn = sqlite3.connect('pachong.db')
        # 设置row 返回字典格式
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        conn.row_factory = dict_factory
        # 游标
        cursor = conn.cursor()

        # 查询500条数据
        sel_sql = 'select ip,port,leixing,id from ip order by id desc'
        cursor.execute(sel_sql)
        for row in cursor:
            old_queue.put(row)

        
        # ip验证结束，子进程输入0， 告知子进程结束
        for work in works:
            old_queue.put(0)

        # 父进程等待子进程执行完毕在退出
        for work in works:
            work.join()

        # 成功队列中获取数据
        while True:
            try:
                success_proxy_ids.append(success_queue.get(timeout=1))
            except:
                break

        # 失败队列中获取数据
        while True:
            try:
                fail_proxy_ids.append(fail_queue.get(timeout=1))
            except:
                break

        # 更新数据库中IP池数据，给其他爬虫使用
        # 问号数量, ? 把格式化的数据当成字符串 防止sql注入
        questionmarks = '?'*len(success_proxy_ids)
        upd_query = 'update ip set is_active=1 where id in ({})'.format(','.join(questionmarks))
        cursor.execute(upd_query, success_proxy_ids)

        # 失败的ip
        questionmarks = '?'*len(fail_proxy_ids)
        upd_query = 'update ip set is_active=0 where id in ({})'.format(','.join(questionmarks))
        cursor.execute(upd_query, fail_proxy_ids)

        # 提交更新执行
        conn.commit()

        # 关闭数据库
        conn.close()

        print('成功:{success}, 失败:{fail}'.format(success=len(success_proxy_ids), fail=len(fail_proxy_ids)))

        print('verify proxy end...')


    # 验证代理操作子进程中
    def verifyProxyOne(self, old_queue, success_queue, fail_queue):
        while True:
            proxy = old_queue.get()
            # 收到结束子进程
            if proxy == 0:
                break

            # 协议
            protocol = proxy['leixing'].lower()
            # 组装 request使用的代理 需要用all 
            # https://requests.readthedocs.io/en/latest/user/advanced/#proxies
            proxies = {'all': protocol+'://'+proxy['ip']+':'+proxy['port']}

            # 访问百度验证代理状态
            try:
                if requests.get('http://httpbin.org/ip', proxies=proxies, timeout=2).status_code == 200:
                    success_queue.put(proxy['id'])
            except:
                fail_queue.put(proxy['id'])


if __name__  == '__main__':
    proxy = Proxy()
    proxy.verifyPorxy()

