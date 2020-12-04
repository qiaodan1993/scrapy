import scrapy
from tender.items import TenderItem 

class TianjinZhongbiaoSpider(scrapy.Spider):
    name = 'tianjin_zhongbiao'
    allowed_domains = ['www.ccgp-tianjin.gov.cn']
    start_urls = ['http://www.ccgp-tianjin.gov.cn/portal/topicView.do']

    base_url = 'http://www.ccgp-tianjin.gov.cn/portal/documentView.do?method=view&ver=2&id='

    custom_settings = {
        'DOWNLOAD_DELAY': 5,
    }

    province = '天津'
    typical = '中标'

    form_data = {'method': 'view', 'page': '1', 'id': '2013', 'step': '1', 'view': 'Infor', 'st':'1'}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']
        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data)

    def parse(self, response):
        for row_data in response.xpath('//ul[@class="dataList"]/li'):
            url = self.base_url + row_data.css('li a::attr(href)').extract_first().split('=')[1][:-4]

            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('span::text').extract()
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail)
            request.meta['item'] = item

            yield request

        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["page"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data)
            self.next_page = self.next_page + 1


    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="pageInner"]/table//b/text()').extract_first()
        item['content'] = response.xpath('//div[@class="pageInner"]/table').get().strip()
        item['html_source'] = response.body

        yield item