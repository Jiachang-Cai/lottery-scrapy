# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime, timedelta

"""
竞彩足球对阵信息采集 
"""


class FootballMatchSpider(scrapy.Spider):
    name = 'football_match'
    allowed_domains = ['info.sporttery.cn']
    start_urls = ['http://info.sporttery.cn/football/match_list.php/']
    weekday_number = {
        "周一": "1",
        "周二": "2",
        "周三": "3",
        "周四": "4",
        "周五": "5",
        "周六": "6",
        "周日": "7",
    }
    play_type = {
        6: "FT01;",
        7: "FT02;",
        8: "FT03;",
        9: "FT04;",
        10: "FT05;"
    }

    def get_unsupport_list(self, tds, indexs):
        unsupport_multi = []
        unsupport_single = []
        for index in indexs:
            class_value = tds[index].xpath('.//div/@class').extract_first()
            if class_value != None:
                class_value = class_value.strip()
                if class_value == "u-cir":  # 仅开售过关方式
                    unsupport_single.append(self.play_type[index])
                elif class_value == "u-kong":  # 未开售此玩法空白：待开售此玩法
                    unsupport_multi.append(self.play_type[index])
                elif class_value == "u-dan":  # 开售单关方式和过关方式
                    pass
        return "".join(unsupport_multi), "".join(unsupport_single)

    def parse(self, response):
        match_list = response.xpath('//div[@class="match_list"]')
        match_tables = match_list.xpath('./table')
        data_dict = {}
        for table in match_tables:
            trs = table.xpath('./tr')
            # 赛事编号 | 联赛 | 主队VS客队 | 比赛开始时间 | 比赛资讯 | 胜平负 | 让球胜平负 | 比分 | 总进球数 | 半全场胜平负 | 特别提示
            for tr in trs:
                tds = tr.xpath('./td')
                # 验证tds 长度
                if len(tds) != 12:
                    continue
                match_time = tds[3].xpath('./text()').extract_first()
                match_date = match_time.split(" ")[0]
                game = 'FT'
                match_color = tds[1].xpath('./@bgcolor').extract_first()
                league = tds[1].xpath('./text()').extract_first()
                league_name = tds[1].xpath('./@title').extract_first()
                home_team, vs, away_team = tds[2].xpath('.//span/text()').extract()
                team_name = home_team + ":" + away_team
                pattern = re.compile(r'([\u4e00-\u9fff]+)(\d+)', re.I)
                m = re.match(pattern, tds[0].xpath('./text()').extract_first())
                match_weekday_str, match_index = m.groups()
                match_weekday = self.weekday_number[match_weekday_str]
                match_number = match_date.replace("-",
                                                  "").strip() + "*" + match_weekday + "*" + match_index.strip()
                unsupport_multi, unsupport_single = self.get_unsupport_list(tds, [6, 7, 8, 9, 10])
                # 验证 match_number
                if len(match_number) != 14:
                    raise Exception("match_number 格式错误")

                match_status_text = tds[5].xpath('./text()').extract_first().strip()
                match_status = 0
                if "已开售" in match_status_text:
                    match_status = 1

                # 大于 9点 和等于 零点 则 截至时间为 开场时间的 前15分钟 否则 为开场时间的 前一天的 23:45
                match_time_obj = datetime.strptime(match_time, '%Y-%m-%d %H:%M')
                end_time = 0
                if match_time_obj.hour > 9 or match_time_obj == 0:
                    end_time = (match_time_obj - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M")
                else:
                    end_time = match_time_obj - timedelta(1)
                    end_time = end_time.replace(hour=23, minute=45).strftime("%Y-%m-%d %H:%M")
                data_dict[match_number] = {
                    "game": game,
                    "team_name": team_name,
                    "league": league,
                    "home_team": home_team,
                    "away_team": away_team,
                    "match_color": match_color,
                    "match_number": match_number,
                    "match_date": match_date,
                    "match_weekday": match_weekday,
                    "match_index": match_index,
                    "unsupport_multi": unsupport_multi,
                    "unsupport_single": unsupport_single,
                    "match_status": match_status,
                    "match_time": match_time,
                    "end_time": end_time,
                }

        yield data_dict
