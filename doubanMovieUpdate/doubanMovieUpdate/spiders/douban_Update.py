import re
from logging import getLogger

from doubanMovieUpdate.items import DoubanmovieupdateItem

from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
import scrapy

log = getLogger(__name__)


class DoubanUpdate(CrawlSpider):
    name = "movieUpdate"
    allowed_domains = ["douban.com"]
    items_id = set()
    start_urls = [
        "https://movie.douban.com/nowplaying/beijing/"
    ]
 
    rules=(
        #Rule(LinkExtractor(allow=(r'https://movie.douban.com/nowplaying/beijing/',))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/subject/\d+/\?from=playing_poster',)),callback="parse_item"),
    )

    def parse_item(self, response):
        log.info("parsing {}".format(response.url))

        selector = Selector(response)
        item = DoubanmovieupdateItem()
        item['name'] = selector.xpath('//*[@id="content"]/h1/span[1]/text()').extract()
        item['year'] = selector.xpath('//*[@id="content"]/h1/span[2]/text()').re(r'\((\d+)\)')
        item['score'] = selector.xpath('//strong[@class="ll rating_num"]/text()').extract()

        movieid = re.match(r'https://.*/.*/(.*)/.*', response.url).group(1)
        item['movieid'] = movieid
        item['director'] = selector.xpath('//span[@class="attrs"]/a[@rel="v:directedBy"]/text()').extract()
        item['classification'] = selector.xpath('//span[@property="v:genre"]/text()').extract()
        item['actor'] = selector.xpath('//span[@class="attrs"]/a[@rel="v:starring"]/text()').extract()

        # get the first recommended poster
        list_poster_url = 'https://movie.douban.com/subject/{}/photos?type=R'.format(movieid)
        yield scrapy.Request(list_poster_url, callback=self.parse_poster_url, meta={'item': item})

    def parse_poster_url(self, response):
        item = response.meta['item']
        selector = Selector(response)

        first_poster_thumb_url = selector.xpath('//*[@id="content"]/div/div[1]/ul/li[1]/div[1]/a/img/@src').extract_first()
        item['poster_url'] = first_poster_thumb_url.replace('thumb', 'photo')
        yield item


