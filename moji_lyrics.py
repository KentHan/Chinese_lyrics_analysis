# coding=utf-8

import scrapy
from pymongo import MongoClient


class MojiLyricsSpider(scrapy.Spider):
    name = 'moji'
    # start_urls = ['https://mojim.com/twh100092.htm'] # 張學友
    start_urls = ['https://mojim.com/twh105643.htm'] # 石頭

    client = MongoClient("mongodb://localhost:27017")

    def parse(self, response):
        for href in response.css('.hc3 a::attr(href)'):
            full_url = response.urljoin(href.extract())[:-4] + ".html"
            print(full_url)
            yield scrapy.Request(full_url, callback=self.parse_song)

    def parse_song(self, response):
        artist = response.css('dl#fsZx1.fsZx1::text').extract_first().strip()
        title = response.css('dt#fsZx2.fsZx2::text').extract_first()
        lyrics = " ".join(response.css('dd#fsZx3.fsZx3::text').extract())

        print(artist)
        print(title)
        print(lyrics)

        db = self.client.test
        db.lyrics.insert({'artist': artist, 'title': title, 'lyrics': lyrics})

        yield {
            'artist': artist,
            'title': title,
            'lyrics': lyrics
        }