import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response

class JilinZhongBiaoSpider(scrapy.Spider):
    name = 'jilin_zhongbiao'
    allowed_domains = ['www.ccgp-jilin.gov.cn']
    start_urls = ['http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action']

    province = '吉林'
    typical = '中标'

    form_data = {'currentPage': '1', 'categoryId': '124', 'noticetypeId':'9'}

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 5,
    }
    
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']


        for pageNum in range(next_page, max_page):
            self.form_data["currentPage"] = str(pageNum)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)


    def parse(self, response):
        for row_data in response.xpath('//div[@id="list_right"]/ul/li'):
            url = response.urljoin(row_data.css('a::attr(href)').get())
            
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('span/text()').get()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']

        item['title'] = response.xpath('//div[@id="xiangqingneiron"]/h2[@class="sd"]/font/text()').get()
        item['content'] = response.xpath('//div[@id="xiangqingneiron"]').get()
        item['html_source'] = response.body

        yield item