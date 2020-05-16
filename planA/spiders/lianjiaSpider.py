# -*- coding: utf-8 -*-
import pymongo
import scrapy
import time,sys,datetime
from pymongo import MongoClient

client = pymongo.MongoClient('localhost', 27017)
lianjiaDB = client['lianjiaDB']
gzlianjiaT = lianjiaDB['gzlianjiaT']


class LianjiaspiderSpider(scrapy.Spider):
    name = 'lianjiaSpider'
    allowed_domains = ['gz.lianjia.com']
    start_urls = ['http://gz.lianjia.com/']

    headers = {'user-agent': "Mozilla/5.0"}

    def __init__(self, query='', **kwargs):

        self.query = query
        self.base_url = "https://gz.lianjia.com"

        self.curr_page_no = 1

        self.curr_url = "{}/{}pg{}".format(self.base_url, self.query, self.curr_page_no)

        self.last_url = None
        super().__init__(**kwargs)

    def start_requests(self):

        urls = [self.curr_url]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        houseList = response.xpath('//ul[@class="sellListContent"]/li')
        if len(houseList) == 0:
            sys.exit()
        # ['title','houseInfo1','houseInfo2','positionInfo1','positionInfo2','followInfo','totalPrice','unitPrice']
        for house in houseList:
            item = {
                'positionInfo1': house.xpath('.//div[@class="positionInfo"]/a/text()').extract(),
                'totalPrice': house.xpath('.//div[@class="totalPrice"]/span/text()').extract(),
                'unitPrice': house.xpath('.//div[@class="unitPrice"]/@data-price').extract(),
                'houseInfo2': house.xpath('.//div[@class="houseInfo"]/text()').extract(),
                'followInfo': house.xpath('.//div[@class="followInfo"]/text()').extract(),
                'title': house.xpath('.//div[@class="title"]/a/text()').extract(),
                'getDate': datetime.datetime.now().strftime('%Y%m%d')

            }
            result = gzlianjiaT.insert_one(item)
            yield item

        self.curr_page_no += 1

        time.sleep(5)

        curr_url = "{}/{}pg{}/".format(self.base_url, self.query, self.curr_page_no)
        yield scrapy.Request(url=curr_url, callback=self.parse, headers=self.headers)
