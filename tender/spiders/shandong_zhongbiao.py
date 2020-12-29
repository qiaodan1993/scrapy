import scrapy
from tender.items import TenderItem 
import re

class ShandongZhongbiaoSpider(scrapy.Spider):
    name = 'shandong_zhongbiao'
    allowed_domains = ['www.ccgp-shandong.gov.cn']
    start_urls = ['http://www.ccgp-shandong.gov.cn/sdgp2017/site/listnew.jsp']

    province = '山东'
    typical = '中标'

    form_data = {'firstpage': '1', 'colcode': '2502', 'curpage': '1'}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']
        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)

    def parse(self, response):
        for row_data in response.xpath('//ul[@class="news_list2"]/li'):
            url = response.urljoin(row_data.css('li span span a::attr(href)').get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('//span[@class="hits"]/text()').get()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request

        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["curpage"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)
            self.next_page = self.next_page + 1


    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//h1[@class="title"]/text()').get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = response.xpath('//div[@class="content"]').get()
        item['content'] = re_style.sub('', content)  # 去掉a标签
        item['html_source'] = response.body
        
        yield item