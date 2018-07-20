# -*- coding: utf-8 -*-
import sitting
from downloader import Downloader
import items
import re
from bs4 import BeautifulSoup
from threading import Lock
import xlwt
import mq


class Spider(object):

    start_urls = ['']

    def __init__(self):
        self.count = 0       # 用于记录xls的行数
        self.downloader = Downloader()
        self.next_url = None
        self.mutex = Lock()  # 创建一个锁 用于文件的读写

    def __enter__(self):
        # 创建 xls 文件对象
        self.wb = xlwt.Workbook()
        # 新增一个表单
        self.sheet = self.wb.add_sheet('Sheet 1')

        self.start_request()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wb.save('data.xls')

    def start_request(self):
        for url in self.start_urls:
            self.downloader.add_job(priority_number=1, job=url, handle=self.parse)
        self.downloader.create_threads()

    def parse(self, response):
        pass


class ReviewSpider(Spider):

    start_urls = [sitting.START_URL, 'https://www.tripadvisor.cn/ShowUserReviews-g298557-d324509-r55902827.html',
                  'https://www.tripadvisor.cn/ShowUserReviews-g298557-d324509-r537566344.html']

    def __init__(self):
        super().__init__()

    def parse(self, response, args=None):
        """评论列表解析"""
        ratings = []
        dates = []

        soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')
        titles = [title.text for title in soup.find_all('span', class_='noQuotes')]
        contents = [content.text for content in soup.find_all('p', class_='partial_entry')]
        ratings_and_dates = soup.find_all('div', class_='rating reviewItemInline')

        for i in ratings_and_dates:
            ratings.append(str(i.contents[0]['class'][1][-2]))
            dates.append(i.contents[1]['title'])

        names = [name.text for name in soup.find_all('div', class_='username mo')]

        for name, content, title, rating, date in zip(names, contents, titles, ratings, dates):
            self.downloader.add_job('https://www.tripadvisor.com/members/'+name, handle=self.parse_article,
                                    args=(content, title, rating, date))

        item = soup.find('a', class_='nav next taLnk ')

        try:
            self.next_url = 'https://www.tripadvisor.cn' + item['href']
        except TypeError:
            pass

    def parse_article(self, response, args=None):
        """用户信息解析"""
        name = None
        review_time = None
        review_rating = None
        age = None
        sex = None
        place = None
        join_date = None

        soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')

        try:
            name = soup.find('span', class_='nameText').text

            place = soup.find('div', class_='hometown').text
            if not re.search('\D+', place):
                place = None

            join_date = soup.find('div', class_='ageSince')

            age_and_sex = str(join_date.contents[-1]).replace(' ', '')
            if age_and_sex:
                age, sex = (re.split('yearold', age_and_sex))

            join_date = join_date.p.text

            time_and_rating = [i.text for i in soup.find_all('li', class_='content-info')
                               if re.search('Reviews|Ratings', i.text)]
            for item in time_and_rating:
                value = re.search('\d+', item).group()
                if re.search('Reviews', item):
                    review_time = value
                else:
                    review_rating = value
        except AttributeError:
            pass
        print("fetch: {}".format('https://www.tripadvisor.com/members/'+str(name)))
        mq.message.put("fetch: {}".format('https://www.tripadvisor.com/members/'+str(name)))
        with self.mutex:
            self.count += 1
            for i, item in enumerate((name, place, age, sex, join_date, review_time, review_rating, *args)):
                self.sheet.write(self.count, i, item)


def run():
    spiderman = ReviewSpider()
    with spiderman:
        while True:
            while spiderman.next_url is None:
                True
            spiderman.downloader.add_job(priority_number=1, job=spiderman.next_url, handle=spiderman.parse)
            spiderman.next_url = None
