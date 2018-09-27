# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from datetime import datetime
from scrapy.utils.project import get_project_settings
from DBUtils.PooledDB import PooledDB

settings = get_project_settings()
database = settings.get('DATABASES')
hostname = database['default']['HOST']
username = database['default']['USER']
password = database['default']['PASSWORD']
database = database['default']['NAME']
pool = PooledDB(psycopg2, 10, host=hostname, port=5432, user=username, password=password,
                database=database)


class LotteryPipeline(object):
    ft_game_rate_sql = """
    insert into cdd_game_rate(game,match_number,match_date,
    ft_let_point_multi,ft01_rate_single,ft02_rate_single,ft03_rate_single,
    ft04_rate_single,ft05_rate_single,ft01_rate_multi,ft02_rate_multi,ft03_rate_multi,ft04_rate_multi,ft05_rate_multi,
    update_time) values('%(game)s','%(match_number)s','%(match_date)s','%(ft_let_point_multi)s','%(ft01_rate_single)s',
    '%(ft02_rate_single)s','%(ft03_rate_single)s','%(ft04_rate_single)s','%(ft05_rate_single)s','%(ft01_rate_multi)s',
    '%(ft02_rate_multi)s','%(ft03_rate_multi)s','%(ft04_rate_multi)s','%(ft05_rate_multi)s','%(update_time)s') ON CONFLICT (match_number,game) DO UPDATE
    set match_date='%(match_date)s',ft_let_point_multi='%(ft_let_point_multi)s',ft01_rate_single='%(ft01_rate_single)s',
    ft02_rate_single='%(ft02_rate_single)s',ft03_rate_single='%(ft03_rate_single)s',ft04_rate_single='%(ft04_rate_single)s',
    ft05_rate_single='%(ft05_rate_single)s',ft01_rate_multi='%(ft01_rate_multi)s',ft02_rate_multi='%(ft02_rate_multi)s',
    ft03_rate_multi='%(ft03_rate_multi)s',ft04_rate_multi='%(ft04_rate_multi)s',ft05_rate_multi='%(ft05_rate_multi)s',update_time='%(update_time)s';
    """
    # is_normal 如何处理?
    ft_game_match_sql = """
    insert into cdd_game_match(game,team_name,league,home_team,away_team,match_color,
    match_number,match_date,match_weekday,match_index,unsupport_multi,
    unsupport_single,match_status,match_time,end_time) values('%(game)s',
    '%(team_name)s','%(league)s','%(home_team)s','%(away_team)s','%(match_color)s','%(match_number)s','%(match_date)s',
    %(match_weekday)s,'%(match_index)s','%(unsupport_multi)s','%(unsupport_single)s',%(match_status)s,'%(match_time)s','%(end_time)s'
    ) ON CONFLICT (match_number,game) DO UPDATE set match_status=%(match_status)s,unsupport_multi='%(unsupport_multi)s',
    unsupport_single='%(unsupport_single)s',match_time='%(match_time)s',end_time='%(end_time)s'
     where cdd_game_match.match_status in (0,1);
    """
    ft_game_match_result_sql = """
    update cdd_game_match set match_status=%(match_status)s,ft_let_point_multi=%(ft_let_point_multi)s,ft_half_home_point=%(ft_let_point_multi)s,
    ft_half_away_point=%(ft_half_away_point)s,
    ft_home_point=%(ft_half_away_point)s,ft_away_point=%(ft_away_point)s where match_number='%(match_number)s' and game='FT';
    """

    lottery_notice_sql = """
    insert into cdd_lottery_notice(title,content,notice_time) values(
    '%(title)s','%(content)s','%(notice_time)s'
    ) ON CONFLICT (notice_time) DO UPDATE set title='%(title)s', content='%(content)s';
    """

    def process_item(self, item, spider):

        if spider.name == "football_rate":
            sql_list = []
            for k, v in item.items():
                sql_list.append(self.ft_game_rate_sql % {
                    "game": 'FT',
                    "match_number": k,
                    "match_date": v['match_date'],
                    "ft_let_point_multi": v['ft_let_point_multi'],
                    "ft01_rate_single": v['ft01_rate_single'],
                    'ft02_rate_single': v['ft02_rate_single'],
                    'ft03_rate_single': v['ft03_rate_single'],
                    'ft04_rate_single': v['ft04_rate_single'],
                    "ft05_rate_single": v['ft05_rate_single'],
                    "ft01_rate_multi": v['ft01_rate_single'],
                    'ft02_rate_multi': v['ft02_rate_single'],
                    'ft03_rate_multi': v['ft03_rate_single'],
                    'ft04_rate_multi': v['ft04_rate_single'],
                    "ft05_rate_multi": v['ft05_rate_single'],
                    "update_time": datetime.now()

                })
            if len(sql_list) > 0:
                conn = pool.connection()
                cur = conn.cursor()
                cur.execute("\n".join(sql_list))
                conn.commit()
                cur.close()
                conn.close()

        elif spider.name == "football_result":
            conn = pool.connection()
            cur = conn.cursor()
            sql_list = []
            for data in item['data']:
                sql_list.append(self.ft_game_match_result_sql % {
                    "match_status": data['match_status'],
                    "ft_let_point_multi": data['ft_let_point_multi'],
                    "ft_half_home_point": data['ft_half_home_point'],
                    "ft_half_away_point": data['ft_half_away_point'],
                    "ft_home_point": data['ft_home_point'],
                    "ft_away_point": data['ft_away_point'],
                    "match_number": data['match_number'],
                })
            if len(sql_list) > 0:
                cur.execute("\n".join(sql_list))
                conn.commit()
                cur.close()
                conn.close()
        elif spider.name == "football_match":
            sql_list = []
            for k, v in item.items():
                sql_list.append(self.ft_game_match_sql % {
                    "game": 'FT', 'team_name': v['team_name'], 'league': v['league'],
                    'home_team': v['home_team'], 'away_team': v['away_team'],
                    'match_color': v['match_color'], 'match_number': v['match_number'],
                    'match_date': v['match_date'], 'match_weekday': v['match_weekday'],
                    'match_index': v['match_index'],
                    'unsupport_multi': v['unsupport_multi'],
                    'unsupport_single': v['unsupport_single'], 'match_status': v['match_status'],
                    'match_time': v['match_time'],
                    'end_time': v['end_time']
                })
            if len(sql_list) > 0:
                conn = pool.connection()
                cur = conn.cursor()
                cur.execute("\n".join(sql_list))
                conn.commit()
                cur.close()
                conn.close()

        elif spider.name == "lottery_notice":
            conn = pool.connection()
            cur = conn.cursor()
            sql_list = []
            for data in item['data']:
                sql_list.append(self.lottery_notice_sql % {
                    "title": data['title'],
                    "content": data['content'],
                    "notice_time": data['notice_time'],
                })
            if len(sql_list) > 0:
                cur.execute("\n".join(sql_list))
                conn.commit()
                cur.close()
                conn.close()
        return item
