# -*- coding: utf-8 -*-
import logging
import os
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from apscheduler.schedulers.twisted import TwistedScheduler
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging
from lottery_scrapy import crawl_jobs

if __name__ == "__main__":
    if os.getenv('ENV') == 'pro':
        os.environ['SCRAPY_SETTINGS_MODULE'] = "lottery_scrapy.pro_settings"
    elif os.getenv('ENV') == 'stg':
        os.environ['SCRAPY_SETTINGS_MODULE'] = "lottery_scrapy.stg_settings"
    else:
        os.environ['SCRAPY_SETTINGS_MODULE'] = "lottery_scrapy.settings"
    settings = get_project_settings()
    handler = SentryHandler(settings.get('SENTRY_DSN'))
    handler.setLevel(logging.ERROR)
    setup_logging(handler)
    configure_logging(settings)
    scheduler = TwistedScheduler()
    scheduler.add_job(lambda: crawl_jobs.crawl_ft_match(settings), 'interval', minutes=20)
    scheduler.add_job(lambda: crawl_jobs.crawl_ft_rate(settings), 'interval', minutes=5)
    scheduler.add_job(lambda: crawl_jobs.crawl_ft_result(settings), 'interval', minutes=30)
    scheduler.add_job(lambda: crawl_jobs.crawl_lottery_notice(settings), 'interval', hours=3)
    scheduler.start()
    reactor.run()
