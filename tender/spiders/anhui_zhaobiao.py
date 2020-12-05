import scrapy
from tender.items import TenderItem 

class AnhuiZhaoBiaoSpider(scrapy.Spider):
    name = 'anhui_zhaobiao'
    allowed_domains = ['www.ccgp-anhui.gov.cn']
    start_urls = ['http://www.ccgp-anhui.gov.cn/cmsNewsController/getCgggNewsList.do?bid_type=011']

    province = '安徽'
    typical = '招标'

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
            item['publish_at'] = row_data.xpath('td[position()=2]/a/text()').get().strip()[1:-1]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
            # return
        # if self.next_page < self.max_page:  # 控制爬取的页数
        #     yield response.follow(self.start_urls[0] + '&pageNum=' + str(self.next_page), self.parse, dont_filter=True)
        #     self.next_page = self.next_page + 1
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['title'] = response.xpath('//div[@class="frameNews"]/h1/text()').get().strip()
        item['content'] = response.xpath('//div[@class="frameNews"]').get().strip()
        item['html_source'] = response.body

        yield item