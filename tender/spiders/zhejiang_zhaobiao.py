import scrapy
import json
from tender.items import TenderItem 
import time

class ZhejiangZhaoBiaoSpider(scrapy.Spider):
    name = 'zhejiang_zhaobiao'
    allowed_domains = ['czt.zj.gov.cn']
    start_urls = ['https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&sourceAnnouncementType=3001%2C3020&url=notice']

    province = '浙江'
    typical = '招标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0]+ '&pageNo=' + str(pageNum), self.parse, dont_filter=True)


    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["articles"]:

            item = TenderItem()
            item['url'] = row_data["url"]
            timeArray = time.localtime(int(row_data["pubDate"])/1000)
            item['publish_at'] = time.strftime("%Y-%m-%d", timeArray)
            item['province'] = self.province
            item['typical'] = self.typical
            item['title'] = row_data["projectName"]

            request = scrapy.Request(item['url'], callback=self.parse_detail)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['content'] = response.xpath('//div[@class="gpoz-detail-content"]').get().strip()
        item['html_source'] = response.body
        yield item