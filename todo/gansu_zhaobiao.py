import scrapy
import json
from tender.items import TenderItem
from scrapy_splash import SplashRequest
import re


script = """
         function main(splash, args)
             assert(splash:go(args.url))
             assert(splash:wait(args.wait))
             if(args.pageNum ==1)
             then
                js = string.format("document.getElementById('c1280501').click();submitSearch();");
             else
                js = string.format("document.getElementById('c1280501').click();submitSearch();");
             end
             splash:evaljs(js)
             assert(splash:wait(args.wait))
             return splash:html()
         end
         """
class GansuZhaobiaoSpider(scrapy.Spider):
    name = 'gansu_zhaobiao'
    allowed_domains = ['www.ccgp-gansu.gov.cn']
    start_urls = ['http://www.ccgp-gansu.gov.cn/web/doSearchmxarticlels.action']

    province = '甘肃'
    typical = '招标'
    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        for pageNum in range(next_page, max_page):
            yield SplashRequest(self.start_urls[0], callback=self.parse,endpoint='execute',args={'lua_source': script, 'pageNum':pageNum, 'wait': 2})
    def parse(self, response):
        list = response.xpath('//ul[@class="Expand_SearchSLisi"]/li')
        for row_data in list:
            url = row_data.css('li a::attr(href)').get()
            if url is None:
                continue
            url = response.urljoin(url)
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data.xpath('./p[1]/span/text()').get().split("|")[1].strip().lstrip("发布时间：")
            item['title'] = row_data.xpath('./a/text()').get().strip()
            item['province'] = self.province
            item['typical'] = self.typical 
            print(item)
            return 
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request
    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='biaotq']/following-sibling::div[1]").get()
        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item

