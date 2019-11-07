# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import json
import codecs
import sqlite3
import os
import codecs

class IpchiPipeline(object):

    def process_item(self, item, spider):
        if item['ip'] is not None:
            return item
        else:
            raise DropItem('Missing ip in {0}'.format(item))

class SqlitePipeline(object):

    def __init__(self):
        db_dir = os.getcwd()+'/pachong.db'
        self.conn = sqlite3.connect(db_dir)
        #self.conn.row_factory = sqlite3.dict_factory
        self.c = self.conn.cursor()
        

    def process_item(self, item, spider):

        # 先查询IP是否插入过
        self.c.execute('select id from ip where ip=?', (item['ip'],))
        ip_exists = self.c.fetchone()
        if ip_exists is None:           
            # 插入数据
            insert_pre = 'INSERT INTO ip (ip,port,address,is_niming,leixing,is_active) VALUES (?,?,?,?,?,?)'
            insert_data = (item['ip'],item['port'],item['address'],item['is_niming'],item['leixing'],item['is_active'])

            self.c.execute(insert_pre, insert_data)


    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()


class JsonPipeline(object):

    def __init__(self):
        print('打开文件准备写入')
        self.file = codecs.open('hunzinanyi.json', 'wb', encoding='utf-8')

    def process_item(self, item, spider):
        print('正在写入')
        line = json.dumps(dict(item), ensure_ascii=False)+"\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        print('写入完成，关闭文件')
        self.file.close()
        