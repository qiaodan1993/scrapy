import scrapy
from tender.items import TenderItem 


class BeijingZhaoBiaoSpider(scrapy.Spider):
    name = 'beijingzhaobiao'
    allowed_domains = ['ccgp-beijing.gov.cn']
    start_urls = ['http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjzbgg/']

    province = '北京'
    typical = '招标'
    next_page = 1
    max_page = 4

    def parse(self, response):
        for row_data in response.xpath('//ul[@class="xinxi_ul"]/li'):
            url = self.start_urls[0] + row_data.css('li a::attr(href)').extract_first()
            
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('span::text').extract_first()
            item['province'] = self.province
            item['city'] = self.province
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
        item['title'] = response.xpath('//body/div[2]/div[2]/span/text()').get().strip()
        item['html_content'] = response.xpath('//body/div[2]/div[3]').get().strip()

        yield item
    

        