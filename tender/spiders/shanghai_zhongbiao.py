import scrapy
import json
from tender.items import TenderItem 
import re

class ShanghaiZhongBiaoSpider(scrapy.Spider):
    name = 'shanghai_zhongbiao'
    allowed_domains = ['www.zfcg.sh.gov.cn']
    start_urls = ['http://www.zfcg.sh.gov.cn/front/search/category']

    province = '上海'
    typical = '中标'

    form_data = {'districtCode': ['319900'], 'categoryCode': 'ZcyAnnouncement4', 'pageSize': '15', "pageNo":"2"}
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

        content = js['content']
        re_style = re.compile('<\s*style[^>].*>[^<]*<\s*/\s*style\s*>', re.I)
        content = re_style.sub('', content)
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = re_style.sub('', content)

        item['content'] = content  # 去掉a标签
        item['publish_at'] = js["publishDate"]
        item['html_source'] = js['content']
        yield item