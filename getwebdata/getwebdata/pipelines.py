# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from datetime import datetime
from getwebdata.items import GetwebdataCollinfo
from getwebdata.settings import my_mongo_uri, my_database
from getwebdata.mylib import emailme, get_pst_time_isostr

class GetwebdataPipeline(object):
    collection_name = ''

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=my_mongo_uri,
            mongo_db=my_database
#            mongo_uri=crawler.settings.get('MONGO_URI'),
#            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
    def open_spider(self, spider):
        if spider.coll == '':
            print "Coll name NULL! "
            return
        self.collection_name = spider.coll
        if spider.debug != '1':
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        if spider.debug != '1':
            #update with finish time
            spider.spider_return_stats['last_update_time'] = get_pst_time_isostr()
#            email_title = 'ufindcar: '+spider.spider_return_stats['last_update_time']+': ' \
#                + spider.spider_return_stats['coll_name'] \
#                +'--total_links:'+str(spider.spider_return_stats['total_processed_links']) \
#                +'--valid_links:'+str(spider.spider_return_stats['valid_links']) \
#                +'--total_pages:'+str(spider.spider_return_stats['total_processed_pages'])
#            emailme(email_title,'')
            self.db[self.collection_name].update(
                                    {'coll_name': self.collection_name},
                                    {
                                        '$set': dict(spider.spider_return_stats)
                                    },
                                    upsert=True,
                                    multi=True,
                                    )
            #print the summary dict, when running shell will redirect&save to log file
            cursor = self.db[self.collection_name].find({'coll_name': self.collection_name})
            if cursor != None:
                for document in cursor:
                    print document
            self.client.close()

    def process_item(self, item, spider):
        if spider.debug != '1':
            #save a python datetime object at server's local time
            #when query the db, it's also using datetime object at server's local time
            item['doc_update_date'] = datetime.now()
            if self.collection_name == 'craig':
                self.db[self.collection_name].update(
                        {"url":item['url']},
                        {
                            '$set': item
                        },
                        upsert=True,
                        multi=True,
                       )
            elif self.collection_name == 'dgdg':
                #only update entries every time, will make sure all cars are unique
                #dgdg has some cars with same VIN!
                self.db[self.collection_name].update(
                        {"vin":item['vin']},
                        {
                            '$set': item
                        },
                        upsert=True,
                        multi=True,
                       )
            elif self.collection_name == 'hertz':
                #use same VIN as key
                #use place + price as key to filter out same place, same price cars?
                self.db[self.collection_name].update(
                        {"vin":item['vin']},
                        {
                            '$set': item
                        },
                        upsert=True,
                        multi=True,
                       )
            else:
                print "#########collection name %s not found!"%self.collection_name
        return item

