#the script may not work properly if there are any changes to website layouts
#script last updated on 22nd April 2024

import scrapy
from scrapy.crawler import CrawlerProcess

class WebtoonSpider(scrapy.Spider):
    name = 'webtoon'
    allowed_domains = ['webtoons.com']
    start_urls = ['https://www.webtoons.com/en/genres']
    custom_settings = {
        'FEEDS': {
            'webtoons.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': ['genre','title', 'author', 'likes', 'ratings', 'released_info'],
                'indent': 4,
            },
        'ROBOTSTXT_OBEY': True
        },
    }

    def parse(self, response):
        genres = response.css('div.snb_wrap a')
        for genre in genres:
            link = genre.css('::attr(href)').get()
            genre_name = genre.css('::text').get().strip()
            # Check that link is not None, not empty, and not just '#' 
            #note: some genre links on the site are empty or #
            if link and link.strip() != '#' and link.strip():
                yield response.follow(link, callback=self.parse_genre_page, meta={'genre_name': genre_name})

    def parse_genre_page(self, response):
        genre_name = response.meta['genre_name']
        webtoons = response.css('#content > div.card_wrap.genre > ul > li')
        for webtoon in webtoons:
            title = webtoon.css('a > div .subj::text').get()
            author = webtoon.css('a > div .author::text').get()
            likes = webtoon.css('a > div .grade_area em.grade_num::text').get()
            detail_page_link = webtoon.css('a::attr(href)').get()

            print(f"Attempting to scrape link: {detail_page_link}")

            item = {
                'genre': genre_name,
                'title': title,
                'author': author,
                'likes': likes,
                'detail_page_link': response.urljoin(detail_page_link)
            }
            yield response.follow(detail_page_link, self.parse_detail_page, meta={'item': item})

    def parse_detail_page(self, response):
        item = response.meta['item']
        item['ratings'] = response.css('#_starScoreAverage::text').get()
        item['released_info'] = response.css('#_asideDetail .day_info::text').get()
        yield item

# Start the crawl process
process = CrawlerProcess()
process.crawl(WebtoonSpider)
process.start()
