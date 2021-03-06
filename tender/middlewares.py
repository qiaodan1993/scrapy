# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import pymysql
from scrapy.exceptions import CloseSpider
from scrapy.exceptions import IgnoreRequest
import random

class TenderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
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


class TenderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    connect = None

    def __init__(self, crawler):
        if TenderDownloaderMiddleware.connect is None:
            TenderDownloaderMiddleware.connect = pymysql.connect(
                host=crawler.settings['MYSQL_HOST'],
                user=crawler.settings['MYSQL_USER'],
                passwd=crawler.settings['MYSQL_PASSWD'],
                charset=crawler.settings['MYSQL_CHARSET'],
                db=crawler.settings['MYSQL_DB'],
                use_unicode=crawler.settings['MYSQL_UNICODE']
            )

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        sql = "SELECT count(1) FROM tender_source where url = %s"
        
        TenderDownloaderMiddleware.connect.ping()
        cursor = TenderDownloaderMiddleware.connect.cursor()
        cursor.execute(sql, (request.url))
        count = cursor.fetchone()
        cursor.close()
        if count[0] >= 1:
            raise IgnoreRequest(request.url)
        else:
            return None

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        

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
class ProxyMiddleWare(object):
    
    PROXIES = [
        '36.250.156.51:9999'
    ]

    def process_request(self, request, spider):
         
        proxy = random.choice(self.PROXIES)
        # print(proxy)
        # return
        request.meta['proxy'] = "http://" + proxy