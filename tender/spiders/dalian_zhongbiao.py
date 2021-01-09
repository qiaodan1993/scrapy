import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re


script = """
         function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(args.wait))
            js = string.format("var arr = document.getElementsByTagName('a');for(var i = 0; i < arr.length; i++) {var title = arr[i].getAttribute('title');if(title == `转到第%s页`) {arr[i].click()}}",args.pageNum)
            splash:evaljs(js)
            assert(splash:wait(args.wait))
            return splash:html()
         end
         """
class DalianZhongbiaoSpider(scrapy.Spider):
    name = 'dalian_zhongbiao'
    allowed_domains = ['www.ccgp-dalian.gov.cn']
    start_urls = ['http://www.ccgp-dalian.gov.cn/dlweb/showinfo/bxmoreinfo.aspx?CategoryNum=003002001']

    province = '大连'
    typical = '中标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield SplashRequest(self.start_urls[0], callback=self.parse,endpoint='execute',args={'lua_source': script, 'pageNum':pageNum, 'wait': 2})
    def parse(self, response):
        # print(response.text)
        list = (response.xpath('//table[@id="MoreInfoList_DataGrid1"]/tbody/tr'))
        for row_data in list:
            url = row_data.css('td a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('./td[3]/text()').get().strip()
            item['title'] = row_data.xpath('./td[2]/a/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical  
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request
    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//td[@id='TDContent']").get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item

