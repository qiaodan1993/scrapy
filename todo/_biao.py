import scrapy
from tender.items import TenderItem 

class BiaoSpider(scrapy.Spider):
    name = 'biao'
    allowed_domains = ['']
    start_urls = ['']

    province = ''
    typical = ''

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            yield scrapy.Request(self.start_urls[0]+ '&pageNum=' + str(pageNum), self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in response.xpath('//div[@class="zc_contract_top"]/table/tr'):
            url = response.urljoin(row_data.css('a::attr(href)').get())

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('td[position()=2]/a/text()').get()[1:-1]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['title'] = response.xpath('//div[@class="frameNews"]/h1/text()').get()
        item['content'] = response.xpath('//div[@class="frameNews"]').get()
        item['html_source'] = response.body

        yield item