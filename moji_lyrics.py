# -*- coding: utf-8 -*-

import scrapy
from pymongo import MongoClient
from urlparse import urljoin


SELECTOR_SONG_IN_ARTIST_PAGE = '.hc3 a::attr(href), .hc4 a::attr(href)'
SELECTOR_ARTIST_IN_CATEGORY_PAGE = '.s_listA a::attr(href)'

class MojiLyricsSpider(scrapy.Spider):
    name = 'moji'

    # start_urls = ['https://mojim.com/twh105643.htm', 'https://mojim.com/twh100085.htm'] # 石頭 / 張宇
    # start_urls = ['https://mojim.com/twh100111.htm'] # 陳奕迅
    # start_urls = ['https://mojim.com/twza.htm'] # 華語男生
    start_urls = ['https://mojim.com/twzb.htm'] # 華語女生
    
    host = 'https://mojim.com'
    
    client = MongoClient("mongodb://localhost:27017")

    ''' start from artist 
    '''
    # def parse(self, response):
    #     for href in response.css(SELECTOR_SONG_IN_ARTIST_PAGE):
    #         full_url = response.urljoin(href.extract())[:-4] + ".html"
    #         print(full_url)
    #         yield scrapy.Request(full_url, callback=self.parse_song)

    ''' start from list 
    '''
    def parse(self, response): # start from list
        for href in response.css(SELECTOR_ARTIST_IN_CATEGORY_PAGE):
            full_url = urljoin(self.host, href.extract())
            yield scrapy.Request(full_url, callback=self.parse_artist)

    def parse_artist(self, response):
        for href in response.css(SELECTOR_SONG_IN_ARTIST_PAGE):
            full_url = response.urljoin(href.extract())[:-4] + ".html"
            print(full_url)
            yield scrapy.Request(full_url, callback=self.parse_song)

    def parse_song(self, response):
        artist = response.css('dl#fsZx1.fsZx1::text').extract_first().strip()
        title = response.css('dt#fsZx2.fsZx2::text').extract_first().strip()

        contents = response.css('dd#fsZx3.fsZx3::text').extract()
        lyrics = self.extract_lyrics(contents)
        composer = self.extract_composer(contents)
        lyricist = self.extract_lyricist(contents)

        db = self.client.test
        db.lyrics.insert({'artist': artist, 'title': title, 'lyrics': lyrics, 'lyricist': lyricist, 'composer': composer})

        yield {
            'artist': artist,
            'title': title,
            'lyricist': lyricist,
            'composer': composer,
            'lyrics': lyrics
        }

    def extract_lyrics(self, contents):
        lyrics = ""
        for line in contents:
            if line.endswith(u'主題曲'):
                pass
            elif line.startswith(u'更多更詳盡歌詞'):
                pass
            elif line.startswith('Repeat') or line.startswith('REPEAT'):
                pass
            elif len(line.strip()) is 0:
                pass
            elif line.startswith('['):
                pass
            elif ":" in line or u"：" in line:
                pass
            else:
                lyrics = lyrics + line + "\n"
        return lyrics

    def extract_composer(self, contents):
        for line in contents:
            if line.startswith(u'作曲：') or line.startswith(u'作曲:'):
                return line[3:].strip()
            elif  line.startswith(u'曲：') or line.startswith(u'曲:'):
                return line[2:].strip()
        return None

    def extract_lyricist(self, contents):
        for line in contents:
            if line.startswith(u'作詞：') or line.startswith(u'作詞:'):
                return line[3:].strip()
            elif  line.startswith(u'詞：') or line.startswith(u'詞:'):
                return line[2:].strip()
        return None


