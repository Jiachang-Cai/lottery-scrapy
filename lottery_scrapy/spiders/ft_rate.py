# -*- coding: utf-8 -*-
import scrapy
import re
import time
import json


"""
竞彩足球赔率让球数采集
"""


class FootballRateSpider(scrapy.Spider):
    name = 'football_rate'
    allowed_domains = ['info.sporttery.cn']
    start_urls = ['http://info.sporttery.cn/football/hhad_list.php']
    urls = [
        'http://i.sporttery.cn/odds_calculator/get_odds?i_format=json&i_callback=getData&poolcode[]=hhad&poolcode[]=had&_=',
        'http://i.sporttery.cn/odds_calculator/get_odds?i_format=json&i_callback=getData&poolcode[]=crs&_=',
        'http://i.sporttery.cn/odds_calculator/get_odds?i_format=json&i_callback=getData&poolcode[]=ttg&_=',
        'http://i.sporttery.cn/odds_calculator/get_odds?i_format=json&i_callback=getData&poolcode[]=hafu&_=']

    weekday_number = {
        "周一": "1",
        "周二": "2",
        "周三": "3",
        "周四": "4",
        "周五": "5",
        "周六": "6",
        "周日": "7",
    }

    spf_number = {
        'a': '0',
        'd': '1',
        'h': '3'
    }

    # docker run  --restart=always -p 5023:5023 -p 8050:8050 -p 8051:8051  -d  scrapinghub/splash --max-timeout 3600
    # 现在可以通过0.0.0.0:8050(http),8051(https),5023 (telnet)来访问Splash了。
    def start_requests(self):
        yield scrapy.Request(url=self.urls[0] + str(int(round(time.time() * 1000))),
                             callback=self.parse_spf_rq_url,
                             dont_filter=True)
        # for url in self.start_urls:
        # yield SplashRequest(url, self.parse_spf_rq, endpoint='render.html', dont_filter=True,
        #                     args={'wait': 1})

    def parse_spf_rq_url(self, response):
        match_rate_data = {}
        body = response.body_as_unicode().replace("getData(", "").replace(");", "")
        data = json.loads(body)
        for k, v in data['data'].items():
            match_date = v['date']
            pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
            m = re.match(pattern, v['num'])
            match_weekday_str, match_index = m.groups()
            match_weekday = self.weekday_number[match_weekday_str]
            match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
            # 验证 match_number
            if len(match_number) != 14:
                raise Exception("match_number 格式错误")
            if not match_number in match_rate_data:
                match_rate_data.setdefault(match_number, {
                    "ft01_rate_single": "",
                    "ft02_rate_single": "",
                    "ft03_rate_single": "",
                    "ft04_rate_single": "",
                    "ft05_rate_single": "",
                    "match_date": str(match_date),
                })

            #  胜平负 赔率
            # rqs = v['fixedodds']
            spf_rate = []
            if 'had' in v:
                spf_rate.append('3' + "=" + str(v['had']['h']))
                spf_rate.append('1' + "=" + str(v['had']['d']))
                spf_rate.append('0' + "=" + str(v['had']['a']))
            rq_rate = []
            if 'hhad' in v:
                rq_rate.append('3' + "=" + str(v['hhad']['h']))
                rq_rate.append('1' + "=" + str(v['hhad']['d']))
                rq_rate.append('0' + "=" + str(v['hhad']['a']))
                match_rate_data[match_number]['ft_let_point_multi'] = int(v['hhad']['fixedodds'])
            match_rate_data[match_number]["ft01_rate_single"] = ";".join(spf_rate)
            match_rate_data[match_number]["ft02_rate_single"] = ";".join(spf_rate)
        yield scrapy.Request(
            url=self.urls[1] + str(
                int(round(time.time() * 1000))),
            meta={'match_rate_data': match_rate_data},
            callback=self.parse_bf_url,
            dont_filter=True)

    def parse_bf_url(self, response):
        match_rate_data = response.meta['match_rate_data']
        body = response.body_as_unicode().replace("getData(", "").replace(");", "")
        data = json.loads(body)
        for k, v in data['data'].items():
            match_date = v['date']
            pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
            m = re.match(pattern, v['num'])
            match_weekday_str, match_index = m.groups()
            match_weekday = self.weekday_number[match_weekday_str]
            match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
            # 验证 match_number
            if len(match_number) != 14:
                raise Exception("match_number 格式错误")
            if not match_number in match_rate_data:
                match_rate_data.setdefault(match_number, {
                    "ft01_rate_single": "",
                    "ft02_rate_single": "",
                    "ft03_rate_single": "",
                    "ft04_rate_single": "",
                    "ft05_rate_single": "",
                    "match_date": match_date,
                    # "ft_let_point_multi": 0,
                })
            bf_rate = []
            bf_rate.append("10=" + str(v['crs']['0100']))
            bf_rate.append("20=" + str(v['crs']['0200']))
            bf_rate.append("21=" + str(v['crs']['0201']))
            bf_rate.append("30=" + str(v['crs']['0300']))
            bf_rate.append("31=" + str(v['crs']['0301']))
            bf_rate.append("32=" + str(v['crs']['0302']))
            bf_rate.append("40=" + str(v['crs']['0400']))
            bf_rate.append("41=" + str(v['crs']['0401']))
            bf_rate.append("42=" + str(v['crs']['0402']))
            bf_rate.append("50=" + str(v['crs']['0500']))
            bf_rate.append("51=" + str(v['crs']['0501']))
            bf_rate.append("52=" + str(v['crs']['0502']))
            bf_rate.append("90=" + str(v['crs']['-1-h']))  # 胜其他
            bf_rate.append("00=" + str(v['crs']['0000']))
            bf_rate.append("11=" + str(v['crs']['0101']))
            bf_rate.append("22=" + str(v['crs']['0202']))
            bf_rate.append("33=" + str(v['crs']['0303']))
            bf_rate.append("99=" + str(v['crs']['-1-d']))  # 平其他
            bf_rate.append("01=" + str(v['crs']['0001']))
            bf_rate.append("02=" + str(v['crs']['0002']))
            bf_rate.append("12=" + str(v['crs']['0102']))
            bf_rate.append("03=" + str(v['crs']['0003']))
            bf_rate.append("13=" + str(v['crs']['0103']))
            bf_rate.append("23=" + str(v['crs']['0203']))
            bf_rate.append("04=" + str(v['crs']['0004']))
            bf_rate.append("14=" + str(v['crs']['0104']))
            bf_rate.append("24=" + str(v['crs']['0204']))
            bf_rate.append("05=" + str(v['crs']['0005']))
            bf_rate.append("15=" + str(v['crs']['0105']))
            bf_rate.append("25=" + str(v['crs']['0205']))
            bf_rate.append("09=" + str(v['crs']['-1-a']))  # 负其他
            match_rate_data[match_number]["ft03_rate_single"] = ";".join(bf_rate)
        yield scrapy.Request(
            url=self.urls[2] + str(
                int(round(time.time() * 1000))),
            callback=self.parse_zjq_url,
            meta={'match_rate_data': match_rate_data},
            dont_filter=True)

    def parse_zjq_url(self, response):
        match_rate_data = response.meta['match_rate_data']
        body = response.body_as_unicode().replace("getData(", "").replace(");", "")
        data = json.loads(body)
        for k, v in data['data'].items():
            match_date = v['date']
            pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
            m = re.match(pattern, v['num'])
            match_weekday_str, match_index = m.groups()
            match_weekday = self.weekday_number[match_weekday_str]
            match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
            # 验证 match_number
            if len(match_number) != 14:
                raise Exception("match_number 格式错误")
            if not match_number in match_rate_data:
                match_rate_data.setdefault(match_number, {
                    "ft01_rate_single": "",
                    "ft02_rate_single": "",
                    "ft03_rate_single": "",
                    "ft04_rate_single": "",
                    "ft05_rate_single": "",
                    "match_date": str(match_date),
                    # "ft_let_point_multi": 0,
                })
            zjq_rate = []
            if 'ttg' in v:
                zjq_rate.append("0=" + str(v['ttg']['s0']))
                zjq_rate.append("1=" + str(v['ttg']['s1']))
                zjq_rate.append("2=" + str(v['ttg']['s2']))
                zjq_rate.append("3=" + str(v['ttg']['s3']))
                zjq_rate.append("4=" + str(v['ttg']['s4']))
                zjq_rate.append("5=" + str(v['ttg']['s5']))
                zjq_rate.append("6=" + str(v['ttg']['s6']))
                zjq_rate.append("7=" + str(v['ttg']['s7']))
            match_rate_data[match_number]["ft04_rate_single"] = ";".join(zjq_rate)
        yield scrapy.Request(
            url=self.urls[3] + str(
                int(round(time.time() * 1000))),
            meta={'match_rate_data': match_rate_data},
            callback=self.parse_bqc_url,
            dont_filter=True)

    def parse_bqc_url(self, response):
        match_rate_data = response.meta['match_rate_data']
        body = response.body_as_unicode().replace("getData(", "").replace(");", "")
        data = json.loads(body)
        for k, v in data['data'].items():
            match_date = v['date']
            pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
            m = re.match(pattern, v['num'])
            match_weekday_str, match_index = m.groups()
            match_weekday = self.weekday_number[match_weekday_str]
            match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
            # 验证 match_number
            if len(match_number) != 14:
                raise Exception("match_number 格式错误")
            if not match_number in match_rate_data:
                match_rate_data.setdefault(match_number, {
                    "ft01_rate_single": "",
                    "ft02_rate_single": "",
                    "ft03_rate_single": "",
                    "ft04_rate_single": "",
                    "ft05_rate_single": "",
                    "match_date": str(match_date),
                    # "ft_let_point_multi": 0,
                })
            bqc_rate = []
            if 'hafu' in v:
                bqc_rate.append("33=" + str(v['hafu']['hh']))
                bqc_rate.append("31=" + str(v['hafu']['hd']))
                bqc_rate.append("30=" + str(v['hafu']['ha']))
                bqc_rate.append("13=" + str(v['hafu']['dh']))
                bqc_rate.append("11=" + str(v['hafu']['dd']))
                bqc_rate.append("10=" + str(v['hafu']['da']))
                bqc_rate.append("03=" + str(v['hafu']['ah']))
                bqc_rate.append("01=" + str(v['hafu']['ad']))
                bqc_rate.append("00=" + str(v['hafu']['aa']))
            match_rate_data[match_number]["ft05_rate_single"] = ";".join(bqc_rate)
        return match_rate_data

    # 胜平负/让球胜平负
    # def parse_spf_rq(self, response):
    #     match_table = response.xpath('//table[@id="mainTbl"]')
    #     trs = match_table.xpath('./tbody/tr[contains(@id,"list_")]')
    #     match_date_tds = match_table.xpath('./tbody//td[@class="bDateTd"]')
    #     match_date_dict = {}
    #     for td in match_date_tds:
    #         text = "".join(td.xpath('./text()').extract())
    #         bindex = td.xpath('./@bindex').extract_first()
    #         match = re.search('\d{4}-\d{2}-\d{2}', text)
    #         date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #         match_date_dict[bindex] = str(date)
    #
    #     for tr in trs:
    #         tds = tr.xpath('./td')
    #         bindex = tr.xpath('./@bindex').extract_first()
    #         match_date = match_date_dict[bindex]
    #         match_weekday_str, match_index = tds[0].xpath('./text()').extract()
    #         match_weekday = self.weekday_number[match_weekday_str]
    #         match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
    #         # print(match_number)
    #         rqs = tds[5].xpath('./div[2]/text()').extract_first()
    #         # spf3, spf1, spf0 = tds[6].xpath('./div[1]/text()').extract()
    #         # rq3, rq1, rq0 = tds[6].xpath('./div[2]/text()').extract()
    #
    #         spf3, spf1, spf0, rq3, rq1, rq0 = tds[6].xpath('./div/span/text()').extract()
    #         print(match_number, spf3, spf1, spf0, rq3, rq1, rq0, "spf_rq")
    #     # 展开全部
    #     script = """
    #     function main(splash, args)
    #       assert(splash:go(args.url))
    #       assert(splash:wait(args.wait))
    #       element = splash:select("#openCrsAll")
    #       element:mouse_click()
    #       assert(splash:wait(args.wait))
    #       return splash:html()
    #     end
    #     """
    #     yield SplashRequest(response.urljoin('cal_crs.htm'), self.parse_bf, endpoint='execute',
    #                         args={'lua_source': script, 'wait': 5},
    #                         dont_filter=True)
    #     yield SplashRequest(response.urljoin('cal_ttg.htm'), self.parse_zjq, endpoint='render.html',
    #                         dont_filter=True,
    #                         args={'wait': 1})
    #     yield SplashRequest(response.urljoin('cal_hafu.htm'), self.parse_bqc, endpoint='render.html',
    #                         dont_filter=True,
    #                         args={'wait': 1})

    # 比分
    # def parse_bf(self, response):
    #     # print(response.body_as_unicode())
    #     match_table = response.xpath('//table[@id="mainTbl"]')
    #     match_date_tds = match_table.xpath('./tbody//td[@class="bDateTd"]')
    #     trs = match_table.xpath('./tbody/tr[@class="listTr"]')
    #     odd_trs = match_table.xpath('./tbody/tr[@class="crsOddsTr"]')
    #     match_date_dict = {}
    #     for td in match_date_tds:
    #         text = "".join(td.xpath('./text()').extract())
    #         bindex = td.xpath('./@bindex').extract_first()
    #         match = re.search('\d{4}-\d{2}-\d{2}', text)
    #         date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #         match_date_dict[bindex] = str(date)
    #
    #     for index, tr in enumerate(trs):
    #         odd_tr = odd_trs[index]
    #         odd_tr_trs = odd_tr.xpath('.//tr')
    #         print(odd_tr_trs.extract())
    #         win_list = odd_tr_trs[0].xpath('./td/span/text()').extract()
    #         draw_list = odd_tr_trs[1].xpath('./td/span/text()').extract()
    #         lose_list = odd_tr_trs[2].xpath('./td/span/text()').extract()
    #         print(win_list, draw_list, lose_list)
    #
    #         tds = tr.xpath('./td')
    #         bindex = tr.xpath('./@bindex').extract_first()
    #         match_date = match_date_dict[bindex]
    #         pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
    #         m = re.match(pattern, tds[0].xpath('./text()').extract_first())
    #         match_weekday_str, match_index = m.groups()
    #         match_weekday = self.weekday_number[match_weekday_str]
    #         match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
    #         print(match_number, "bf")

    # 总进球
    # def parse_zjq(self, response):
    #     match_table = response.xpath('//table[@id="mainTbl"]')
    #     trs = match_table.xpath('./tbody//tr[contains(@id,"list_")]')
    #     match_date_tds = match_table.xpath('./tbody//td[@class="bDateTd"]')
    #     match_date_dict = {}
    #     for td in match_date_tds:
    #         text = "".join(td.xpath('./text()').extract())
    #         bindex = td.xpath('./@bindex').extract_first()
    #         match = re.search('\d{4}-\d{2}-\d{2}', text)
    #         date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #         match_date_dict[bindex] = str(date)
    #     for tr in trs:
    #         tds = tr.xpath('./td')
    #         bindex = tr.xpath('./@bindex').extract_first()
    #         match_date = match_date_dict[bindex]
    #         match_weekday_str, match_index = tds[0].xpath('./text()').extract()
    #         match_weekday = self.weekday_number[match_weekday_str]
    #         match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
    #         zjq0, zjq1, zjq2, zjq3, zjq4, zjq5, zjq6, zjq7 = tds[5].xpath('./span/text()').extract()
    #         print(match_number, zjq0, zjq1, zjq2, zjq3, zjq4, zjq5, zjq6, zjq7, "zjq")

    # 半全场
    # def parse_bqc(self, response):
    #     match_table = response.xpath('//table[@id="mainTbl"]')
    #     trs = match_table.xpath('./tbody/tr[contains(@id,"list_")]')
    #     match_date_tds = match_table.xpath('./tbody//td[@class="bDateTd"]')
    #     match_date_dict = {}
    #     for td in match_date_tds:
    #         text = "".join(td.xpath('./text()').extract())
    #         bindex = td.xpath('./@bindex').extract_first()
    #         match = re.search('\d{4}-\d{2}-\d{2}', text)
    #         date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    #         match_date_dict[bindex] = str(date)
    #     for tr in trs:
    #         tds = tr.xpath('./td')
    #         bindex = tr.xpath('./@bindex').extract_first()
    #         match_date = match_date_dict[bindex]
    #         match_weekday_str, match_index = tds[0].xpath('./text()').extract()
    #         match_weekday = self.weekday_number[match_weekday_str]
    #         match_number = match_date.replace("-", "").strip() + "*" + match_weekday + "*" + match_index.strip()
    #         ss, sp, sf, ps, pp, pf, fs, fp, ff = tds[4].xpath('./span/text()').extract()
    #         print(match_number, ss, sp, sf, ps, pp, pf, fs, fp, ff, "bqc")
