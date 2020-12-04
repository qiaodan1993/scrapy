import scrapy
from tender.items import TenderItem 


class ShenzhenZhaoBiaoSpider(scrapy.Spider):
    name = 'shenzhen_zhaobiao'

    allowed_domains = ['ggzy.sz.gov.cn']
    start_urls = ['http://ggzy.sz.gov.cn/cn/jyxx/jsgc/jsgz_zbgg/']

    province = '深圳'
    typical = '招标'

    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.Request(self.start_urls[0], self.parse)

    def parse(self, response):
        for row_data in response.xpath('//div[@class="tag-list4"]/ul/li'):
            url = row_data.css('li a::attr(href)').get()
            
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('span::text').get()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail)
            request.meta['item'] = item

            yield request
            # return
        if self.next_page < self.max_page:  # 控制爬取的页数
            yield response.follow(self.start_urls[0] + 'index_' + str(self.next_page) + '.html', self.parse)
            self.next_page = self.next_page + 1

    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="container"]//div[@class="bt"]/text()').get().strip()
        item['content'] = response.xpath('//div[@class="container"]//div[@class="text"]').get().strip()
        item['html_source'] = response.body

        yield item
    

        