import scrapy


class XinjiangZhaobiaoSpider(scrapy.Spider):
    name = 'xinjiang_zhaobiao'
    allowed_domains = ['www.ccgp-xinjiang.gov.cn']
    start_urls = ['http://www.ccgp-xinjiang.gov.cn/front/search/category']

    province = '新疆'
    typical = '招标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']

        for pageNum in range(next_page, max_page):
            # post数据拼装
            form_data = {
                # 固定的中标渠道id
                'categoryCode': "ZcyAnnouncement2",
                'districtCode': ["659900"],
                'pageNo': '1',
                'pageSize': '"15"',
                'utm': "sites_group_front.2ef5001f.0.0.e08104004a7611eb85834fcb3e351a15",
            }
            yield scrapy.FormRequest(self.start_urls[0], formdata=form_data, callback=self.parse, dont_filter=True)
            return 

    def parse(self, response):

        print(response.text)
        return 
        rs =  json.loads(response.text)
        if not rs:
            return 
        for row_data in rs['rows']:
            url = self.content_url.replace('{infoId}',row_data['id'])
            item = TenderItem()
            item['url'] = url
            item['publish_at'] = row_data['releaseDate']
            item['title'] = row_data['title']
            item['province'] = self.province
            item['typical'] = self.typical 
            request = SplashRequest(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        content = response.xpath("//form[@name='thisform']").get()

        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        item['content'] = re_style.sub('', content) # 去掉a标签
        item['html_source'] = response.body
        yield item

