import scrapy
from tender.items import TenderItem 

class ShandongZhaobiaoSpider(scrapy.Spider):
    name = 'shandong_zhaobiao'
    allowed_domains = ['www.ccgp-shandong.gov.cn']
    start_urls = ['http://www.ccgp-shandong.gov.cn/sdgp2017/site/listnew.jsp']

    base_url = 'http://www.ccgp-shandong.gov.cn'

    province = '山东'
    typical = '招标'

    form_data = {'firstpage': '1', 'colcode': '2501', 'curpage': '1'}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']
        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data)

    def parse(self, response):
        for row_data in response.xpath('//ul[@class="news_list2"]/li'):
            url = self.base_url + row_data.css('li span span a::attr(href)').extract_first()

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('//span[@class="hits"]/text()').get()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail)
            request.meta['item'] = item

            yield request

        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["curpage"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data)
            self.next_page = self.next_page + 1


    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//h1[@class="title"]/text()').get().strip()
        item['content'] = response.xpath('//div[@class="content"]').get().strip()
        item['html_source'] = response.body
        
        yield item