import scrapy
import json
from tender.items import TenderItem 

class ZhejiangZhongBiaoSpider(scrapy.Spider):
    name = 'zhejiangzhongbiao'
    allowed_domains = ['czt.zj.gov.cn']
    start_urls = ['https://zfcgmanager.czt.zj.gov.cn/cms/api/cors/remote/results?pageSize=15&sourceAnnouncementType=3004%2C4005%2C4006&url=notice']

    province = '浙江'
    typical = '中标'
    next_page = 2
    max_page = 4
    def parse(self, response):
        js = json.loads(response.body) 
        for row_data in js["articles"]:

            item = TenderItem()
            item['url'] = row_data["url"]
            item['publish_at'] = row_data["pubDate"]
            item['province'] = self.province
            item['typical'] = self.typical
            item['title'] = row_data["projectName"]
            item['city'] = row_data["districtName"]

            request = scrapy.Request(item['url'], callback=self.parse_detail)
            request.meta['item'] = item
            
            yield request
            # return
        if self.next_page < self.max_page:  # 控制爬取的页数
            yield response.follow(self.start_urls[0] + '&pageNo=' + str(self.next_page), self.parse)
            self.next_page = self.next_page + 1
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['html_content'] = response.xpath('//div[@class="gpoz-detail-content"]').get().strip()

        yield item