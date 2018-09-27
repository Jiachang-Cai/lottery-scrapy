from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from lottery_scrapy.spiders.ft_rate import FootballRateSpider
from lottery_scrapy.spiders.ft_match import FootballMatchSpider
from lottery_scrapy.spiders.ft_result import FootballResultSpider
from lottery_scrapy.spiders.lottery_notice import LotteryNoticeSpider


@defer.inlineCallbacks
def crawl_ft_match(settings):
    runner = CrawlerRunner(settings)
    yield runner.crawl(FootballMatchSpider)


@defer.inlineCallbacks
def crawl_ft_rate(settings):
    runner = CrawlerRunner(settings)
    yield runner.crawl(FootballRateSpider)


@defer.inlineCallbacks
def crawl_ft_result(settings):
    runner = CrawlerRunner(settings)
    yield runner.crawl(FootballResultSpider)


@defer.inlineCallbacks
def crawl_lottery_notice(settings):
    runner = CrawlerRunner(settings)
    yield runner.crawl(LotteryNoticeSpider)
