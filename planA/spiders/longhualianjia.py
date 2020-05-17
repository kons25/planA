# -*- coding: utf-8 -*-
import pymongo
import scrapy
import requests
import time,sys,datetime
from pymongo import MongoClient

client = pymongo.MongoClient('localhost', 27017)
lianjiaDB = client['lianjiaDB']
longhualianjiaT = lianjiaDB['longhualianjiaT']

class longhualianjiaSpider(scrapy.Spider):
    name = 'longhualianjia'
    allowed_domains = ['sz.lianjia.com']
    start_urls = ['http://sz.lianjia.com/']

    headers = {'user-agent': "Mozilla/5.0"}


    def __init__(self, query='', **kwargs):

        self.query = query
        self.base_url = "https://sz.lianjia.com/ershoufang/longhuaqu/sf1bp0ep800"

        self.curr_page_no = 1

        self.curr_url = "{}/pg{}".format(self.base_url, self.curr_page_no, self.query)

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
                '楼盘信息': house.xpath('.//div[@class="positionInfo"]/a/text()').extract()[0],
                '地区信息': house.xpath('.//div[@class="positionInfo"]/a/text()').extract()[1],
                '总价': house.xpath('.//div[@class="totalPrice"]/span/text()').extract()[0],
                '单价': house.xpath('.//div[@class="unitPrice"]/@data-price').extract()[0],
                '楼层信息': house.xpath('.//div[@class="houseInfo"]/text()').extract()[0],
                '关注人数': house.xpath('.//div[@class="followInfo"]/text()').extract()[0],
                '描述': house.xpath('.//div[@class="title"]/a/text()').extract()[0],
                'getDate': datetime.datetime.now().strftime('%Y%m%d')

            }
            result = longhualianjiaT.insert_one(item)
            yield item

        self.curr_page_no += 1

        time.sleep(5)

        curr_url = "{}/pg{}".format(self.base_url, self.curr_page_no, self.query)
        yield scrapy.Request(url=curr_url, callback=self.parse, headers=self.headers)

if __name__ == '__main__':
    from scrapy import cmdline
    args = "scrapy crawl longhualianjia".split()
    cmdline.execute(args)

#运行spider命令2
#scrapy runspider longhualianjia.py -a query=ershoufang/ie2y4l2l3a3a4p5
