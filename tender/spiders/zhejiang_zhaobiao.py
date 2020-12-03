import scrapy
import json
from tender.items import TenderItem 

class ZhejiangZhaoBiaoSpider(scrapy.Spider):
    name = 'zhejiang_zhaobiao'
    allowed_domains = ['czt.zj.gov.cn']
    start_urls = ['https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&sourceAnnouncementType=3001%2C3020&url=notice']

    province = '浙江'
    typical = '招标'

    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.Request(self.start_urls[0], self.parse)    

    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["articles"]:

            item = TenderItem()
            item['url'] = row_data["url"]
            item['publish_at'] = row_data["pubDate"]
            item['province'] = self.province
            item['typical'] = self.typical
            item['title'] = row_data["projectName"]

            request = scrapy.Request(item['url'], callback=self.parse_detail)
            request.meta['item'] = item
            
            yield request
            # return
        if self.next_page < self.max_page:  # 控制爬取的页数
            yield response.follow(self.start_urls[0] + '&pageNo=' + str(self.next_page), self.parse)
            self.next_page = self.next_page + 1
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['content'] = response.xpath('//div[@class="gpoz-detail-content"]').get().strip()
        item['html_source'] = response.body
        yield item