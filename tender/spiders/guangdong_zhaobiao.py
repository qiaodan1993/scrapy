import scrapy
import datetime
from tender.items import TenderItem
import re

class GuangdongZhaobiaoSpider(scrapy.Spider):
    name = 'guangdong_zhaobiao'
    allowed_domains = ['www.ccgp-guangdong.gov.cn']
    start_urls = ['http://www.ccgp-guangdong.gov.cn/queryMoreInfoList.do']

    province = '广东'
    typical = '招标'

    def start_requests(self):
        next_page = self.settings['COMMAND_NEXT_PAGE']
        max_page = self.settings['COMMAND_MAX_PAGE']
        # 结束日期今天
        end_date = datetime.datetime.now().date()
        # 开始日期日期今天前30天
        begin_date = end_date + datetime.timedelta(days=-30)

        for pageNum in range(next_page, max_page):
            # post数据拼装
            if pageNum == 1:
                form_data = {
                    # 固定的中标渠道id
                    'stockTypes': '',
                    'channelCode': '0005',
                    'regionIds': '',
                    'sitewebName': '省直',
                    'sitewebId': '4028889705bebb510105bec068b00003',
                    'title': '',
                    'stockNum': '',
                    'purchaserOrgName': '',
                    'issueOrgan': '',
                    'performOrgName': '',
                    'stockIndexName': '',
                    'operateDateFrom': str(begin_date),
                    'operateDateTo': str(end_date),
                    'poor': '',
                }
            else:
                form_data = {
                    # 固定的中标渠道id
                    'channelCode': '0005',
                    'issueOrgan': '',
                    'operateDateFrom': str(begin_date),
                    'operateDateTo': str(end_date),
                    'performOrgName': '',
                    'poor': '',
                    'purchaserOrgName': '',
                    'regionIds': '',
                    'sitewebId': '4028889705bebb510105bec068b00003',
                    'sitewebName': '省直',
                    'stockIndexName': '',
                    'stockNum': '',
                    'stockTypes': '',
                    'title': '',
                    'pageIndex': str(pageNum),
                    'pageSize': '15',
                    'pointPageIndexId': str(pageNum - 1),
                }
            yield scrapy.FormRequest(self.start_urls[0], formdata=form_data, callback=self.parse, dont_filter=True)

    def parse(self, response):
        for row_data in (response.xpath('//*[@class="m_m_cont"]/ul/li')):
            item = TenderItem()
            url = response.urljoin(row_data.css('li a::attr(href)')[1].extract())
            item['url'] = url
            publish_at_time = row_data.xpath('em/text()')[0].extract()
            # 根据空格分割 只要年月日
            item['publish_at'] = publish_at_time.split()[0]
            item['province'] = self.province
            item['typical'] = self.typical
            request = scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
            request.meta['item'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['item']
        item['title'] = response.xpath('//div[@class="zw_c_c_title"]/text()').get()

        re_style = re.compile('<\s*a[^>].*>[^<]*<\s*/\s*a\s*>', re.I)
        content = response.xpath('//div[@class="zw_c_c_cont"]').get()
        item['content'] = re_style.sub('', content) # 去掉a标签

        item['html_source'] = response.body
        yield item