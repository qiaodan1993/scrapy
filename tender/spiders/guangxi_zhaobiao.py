import scrapy
import datetime
from tender.items import TenderItem
import json
class GuangdongZhaobiaoSpider(scrapy.Spider):
    name = 'guangxi_zhaobiao'
    allowed_domains = ['www.ccgp-guangxi.gov.cn']
    start_urls = ['http://www.ccgp-guangxi.gov.cn/front/search/category']

    province = '广西'
    typical = '招标'

    form_data = {'categoryCode': 'ZcyAnnouncement1', 'pageSize': '15', "pageNo":"1"}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.http.JsonRequest(self.start_urls[0], data=self.form_data, dont_filter=True)

    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["hits"]["hits"]:
            url = response.urljoin(row_data["_source"]["url"])
            item = TenderItem()
            item['url'] = url
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
            # return
        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["pageNo"] = str(self.next_page)
            yield scrapy.http.JsonRequest(self.start_urls[0], data=self.form_data, dont_filter=True)
            self.next_page = self.next_page + 1
    
    def parse_detail(self, response):
        item = response.meta['item']
        js = json.loads(response.xpath('//input[@name="articleDetail"]/@value').get())
        item['title'] = js['title']
        item['content'] = js['content']
        item['publish_at'] = js["publishDate"]
        item['html_source'] = js['content']
        yield item