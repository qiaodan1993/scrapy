import scrapy
from tender.items import TenderItem 
from scrapy.shell import inspect_response

class HubeiZhaobiaoSpider(scrapy.Spider):
    name = 'hubei_zhaobiao'
    allowed_domains = ['www.ccgp-hubei.gov.cn']
    start_urls = ['http://www.ccgp-hubei.gov.cn:9040/quSer/search']

    province = '湖北'
    typical = '招标'

    form_data = {'queryInfo.type': 'xmgg', 'queryInfo.key': '', 'queryInfo.jhhh':'', 'queryInfo.fbr':'', 
    'queryInfo.cglx':'','queryInfo.cgfs':'','queryInfo.cgr':'','queryInfo.begin': '','queryInfo.end':'',
    'queryInfo.pageSize':'15', 'queryInfo.pageTotle': '540',
    'queryInfo.gglx': '招标公告（公开招标、邀请招标）', 'queryInfo.city': '湖北省', 'queryInfo.district': '全省', 'queryInfo.pageNo': '1'}
    def start_requests(self):
        self.next_page = self.settings['COMMAND_NEXT_PAGE']
        self.max_page = self.settings['COMMAND_MAX_PAGE']

        yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, headers={'Cookie': 'JSESSIONID=DFD296E5EE46FCE11B4FB126923FDFA7; JSESSIONID=639632984F5A1C4E50D480A727B23C14'}, dont_filter=True)

    def parse(self, response):
        inspect_response(response, self)

        for row_data in response.xpath('//li[@class="serach-page-results-item"]'):
            url = response.urljoin(row_data.css('li div div a::attr(href)').get())

            item = TenderItem()
            item['url'] = url
            item['province'] = self.province
            item['typical'] = self.typical

            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item

            yield request

        if self.next_page < self.max_page:  # 控制爬取的页数
            self.form_data["queryInfo.pageNo"] = str(self.next_page)
            yield scrapy.FormRequest(self.start_urls[0], formdata=self.form_data, dont_filter=True)
            self.next_page = self.next_page + 1


    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="art_con"]/span/text()').get()
        item['publish_at'] = response.xpath('//div[@class="art_con"]/div/div/span/text()').split(' ')[1]
        item['content'] = response.xpath('//div[@class="art_con"]/div[2]"]').get()
        item['html_source'] = response.body
        
        yield item