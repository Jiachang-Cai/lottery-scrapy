# -*- coding: utf-8 -*-
import scrapy
import re
import datetime


class FootballResultSpider(scrapy.Spider):
    name = 'football_result'
    allowed_domains = ['info.sporttery.cn']
    edate = datetime.date.today()
    sdate = edate - datetime.timedelta(days=7)
    start_urls = [
        'http://info.sporttery.cn/football/match_result.php?search_league=0&start_date={sdate}&end_date={edate}&dan='.format(
            sdate=sdate, edate=edate)]
    weekday_number = {
        "周一": "1",
        "周二": "2",
        "周三": "3",
        "周四": "4",
        "周五": "5",
        "周六": "6",
        "周日": "7",
    }

    def parse(self, response):
        # 获取分页
        pages = response.xpath(
            '//div[@class="match_list"]//table[@class="m-page"]//li[contains(@class,"u-pg")]/a/text()|//div[@class="match_list"]//table[@class="m-page"]//li[contains(@class,"u-pg")]/span/text()').extract()
        page_list = []
        for item in pages:
            if item.isdigit():
                page_list.append(int(item))
        if page_list:
            last_page = max(page_list)
            for item in range(1, last_page + 1):
                # 查询一周
                url = "match_result.php?page={page}&search_league=0&start_date={sdate}&end_date={edate}&dan=".format(
                    sdate=self.sdate,
                    edate=self.edate, page=item)
                yield scrapy.Request(url=response.urljoin(url),
                                     callback=self.parse_item,
                                     dont_filter=True)

    def parse_item(self, response):
        match_tables = response.xpath('//div[@class="match_list"]/table[@class="m-tab"]')
        page_data = {'data':[]}
        if len(match_tables) > 0:
            match_table = match_tables[0]
            trs = match_table.xpath('./tr')
            for tr in trs:
                tds = tr.xpath('./td')
                if len(tds) <= 1:  # 分页行跳过
                    continue
                match_date = tds[0].xpath('./text()').extract_first()
                pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
                m = re.match(pattern, tds[1].xpath('./text()').extract_first())
                match_weekday_str, match_index = m.groups()
                match_weekday = self.weekday_number[match_weekday_str]
                match_number = match_date.replace("-",
                                                  "").strip() + "*" + match_weekday + "*" + match_index.strip()

                status = tds[9].xpath('./text()').extract_first()  # 已完成 进行中
                result_detail_url = tds[10].xpath('./a/@href').extract_first()
                if "已完成" in status:
                    rqs = tds[3].xpath('.//span/text()').extract_first()
                    bcbf = tds[4].xpath('./span/text()').extract_first()
                    qcbf = tds[5].xpath('./span/text()').extract_first()
                    pattern = re.compile(r'()\((.*?)\)', re.I)
                    rqs_data = pattern.findall(rqs)
                    ft_let_point_multi = 0
                    if len(rqs_data) <= 0:
                        raise Exception("让球数 格式解析错误")
                    else:
                        ft_let_point_multi = int(rqs_data[0][1])
                    ft_half_home_point, ft_half_away_point = bcbf.split(":")
                    ft_home_point, ft_away_point = qcbf.split(":")

                    data = {
                        "ft_half_home_point": int(ft_half_home_point),
                        "ft_half_away_point": int(ft_half_away_point),
                        "ft_home_point": int(ft_home_point),
                        "ft_away_point": int(ft_away_point),
                        "match_status": 2,  # 2-比赛结束(赛果已出)
                        "ft_let_point_multi": int(ft_let_point_multi),
                        "match_number": match_number
                    }
                    page_data['data'].append(data)
                    # yield scrapy.Request(url=response.urljoin(result_detail_url),
                    #                      callback=self.parse_award,
                    #                      dont_filter=True)
        yield page_data

    def parse_award(self, response):
        print(response.body)
