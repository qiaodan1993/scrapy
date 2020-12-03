import scrapy
from tender.items import TenderItem 

class HainanZhongBiaoSpider(scrapy.Spider):
    name = 'hainan_zhongbiao'
    allowed_domains = ['www.ccgp-hainan.gov.cn']
    start_urls = ['https://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?begindate=&enddate=&title=&bid_type=108&proj_number=&zone=&ctype=']
    base_url = 'https://www.ccgp-hainan.gov.cn'
    
    province = '海南'
    typical = '中标'

    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.Request(self.start_urls[0], self.parse)

    def parse(self, response):
        for row_data in response.xpath('//div[@class="index07_07_02"]/ul/li'):
            url = self.base_url + row_data.css('li span a::attr(href)').extract_first()

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('li span em::text').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail)
            request.meta['item'] = item

            yield request
        if self.next_page < self.max_page:  # 控制爬取的页数
            yield response.follow(self.start_urls[0] + '&currentPage=' + str(self.next_page), self.parse)
            self.next_page = self.next_page + 1
    
    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="zx-xxxqy"]/h2/text()').get().strip() 
        item['content'] = response.xpath('//div[@class="content01"]').get().strip()
        item['html_source'] = response.body

        yield item