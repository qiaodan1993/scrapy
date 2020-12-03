import scrapy
from tender.items import TenderItem 

class JiangsuZhongBiaoSpider(scrapy.Spider):
    name = 'jiangsu_zhongbiao'
    allowed_domains = ['www.ccgp-jiangsu.gov.cn']
    start_urls = ['http://www.ccgp-jiangsu.gov.cn/ggxx/zbgg/']

    province = '江苏'
    typical = '中标'

    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.Request(self.start_urls[0], self.parse)


    def parse(self, response):
        for row_data in response.xpath('//*[@id="newsList"]/ul/li'):
            url = self.start_urls[0] + row_data.css('li a::attr(href)').extract_first()
            
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('li::text').extract()[-1].split()[0]
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
        item['title'] = response.xpath('//div[@class="dtit"]/h1/text()').get().strip()
        item['content'] = response.xpath('//div[@class="content"]').get().strip()
        item['html_source'] = response.body

        yield item
    

        