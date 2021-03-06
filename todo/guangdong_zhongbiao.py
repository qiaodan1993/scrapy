import scrapy
from tender.items import TenderItem 

class GuangdongZhongbiaoSpider(scrapy.Spider):
    name = 'guangdong_zhongbiao'
    allowed_domains = ['www.ccgp-guangdong.gov.cn']
    start_urls = ['http://www.ccgp-guangdong.gov.cn/queryMoreInfoList.do']

    province = '广东'
    typical = '中标'

    form_data = {'sitewebName': '省直','pageSize': '15', 'channelCode': '0008', 'pageIndex': '1'}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']
        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)

    def parse(self, response):
        for row_data in response.xpath('//ul[@class="m_m_c_list"]/li'):
            url = response.urljoin(row_data.css('li a::attr(href)')[1].get())
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.css('li em::text').get().strip().split(' ')[0]
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request

        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["pageIndex"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)
            self.next_page = self.next_page + 1


    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="zw_c_c_title"]/text()').get().strip()
        item['content'] = response.xpath('//div[@class="zw_c_c_cont"]').get().strip()
        item['html_source'] = response.body

        yield item