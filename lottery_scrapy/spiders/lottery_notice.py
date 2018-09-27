# -*- coding: utf-8 -*-
import scrapy


class LotteryNoticeSpider(scrapy.Spider):
    name = 'lottery_notice'
    allowed_domains = ['info.sporttery.cn']
    start_urls = ['http://info.sporttery.cn/iframe/lottery_notice.php']

    def parse(self, response):
        # 获取分页
        pages = response.xpath(
            '//div[@class="all-wrap"]//table[@class="m-page"]//li[contains(@class,"u-pg")]/a/text()|//div[@class="all-wrap"]//table[@class="m-page"]//li[contains(@class,"u-pg")]/span/text()').extract()
        page_list = []
        for item in pages:
            if item.isdigit():
                page_list.append(int(item))
        if page_list:
            last_page = max(page_list)
            for item in range(1, last_page + 1):
                url = response.url + '?page=' + str(item)
                yield scrapy.Request(url=url,
                                     callback=self.parse_item,
                                     dont_filter=True)

    def parse_item(self, response):
        sales_boxs = response.xpath('//div[@class="all-wrap"]//div[@class="sales_box"]')
        page_data = {'data': []}
        for sales_box in sales_boxs:
            title = sales_box.xpath('./div[@class="sales_tit"]//text()').extract_first()
            content = sales_box.xpath('./div[@class="sales_con"]//text()').extract_first()
            notice_time = title.split(u'\xa0')[1].replace(u'\t', '')
            page_data['data'].append({
                "title": title.replace(u'\xa0', ' ').replace(u'\t', ''),
                "content": content,
                "notice_time": notice_time
            })
        yield page_data