import requests
from bs4 import BeautifulSoup
import re
from time import ctime
from prettytable import PrettyTable


class WeatherSina(object):
    def __init__(self, city):
        self.url = 'http://php.weather.sina.com.cn/search.php'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
        # self.proxies = {'http://185.103.21.53': 'http://185.103.21.53:80',
                        # 'http://88.159.151.163': 'http://88.159.151.163:80',
                        # '197.97.146.62': '197.97.146.62:8080'}
        self.city = city
        self.data = ctime()
        self.soup = None
        self.today = None
        self.other_four_day = None

    def get_soup(self):
        params = {'f': 1, 'c': 1, 'city': self.city, 'dpc': 1}
        page = requests.get(self.url, headers=self.headers, params=params)
        self.soup = BeautifulSoup(page.content.decode('GBK'), 'lxml')

    def parse_soup(self):
        today = self.soup.find(name='div', class_=re.compile(r'^mod_today'))
        other_four_day = self.soup.find_all(name='div', class_='mod_02')

        #  today_detail['day'] => ['2℃', '阴', '无持续风向 ≤3级']
        today_detail_dic = dict(day='  '.join(list(today('div', class_='day')[0].ul.stripped_strings)[2:]),
                                night='  '.join(list(today('div', class_='night')[0].ul.stripped_strings)))

        # other_four_day_detail[day0] => ['阴', '9℃', '无持续风向', '≤3级']
        other_four_day_dic = dict()
        for i in range(4):
            other_four_day_dic['day%s' % i] = '  '.join(other_four_day[i]
                                                        ('div', class_='mod_03')[0].ul.stripped_strings)
            other_four_day_dic['night%s' % i] = '  '.join(other_four_day[i]
                                                          ('div', class_='mod_03')[1].ul.stripped_strings)

        self.today = today_detail_dic
        self.other_four_day = other_four_day_dic

    def show_data(self):
        """
        today = '今天\n' + '白天: ' + self.today['day'] + '\n夜晚: ' + self.today['night']
        one_after = '明天\n' + '白天：' + self.other_four_day['day0'] + '\n夜晚: ' + self.other_four_day['night0']
        two_after = '后天\n' + '白天: ' + self.other_four_day['day1'] + '\n夜晚: ' + self.other_four_day['night1']
        three_after = '大后天\n' + '白天: ' + self.other_four_day['day2'] + '\n夜晚: ' + self.other_four_day['night2']
        four_after = '大大后天\n' + '白天: ' + self.other_four_day['day3'] + '\n夜晚: ' + self.other_four_day['night3']
        weather_list = [today, one_after, two_after, three_after, four_after]
        for day in weather_list:
            print(day, '\n')
        """

        date = ['明天', '后天', '大后天 ', '大大后天']
        table = PrettyTable(['日期', '白天', '夜间'])
        table.add_row(['今天', self.today['day'], self.today['night']])
        for i in range(4):
            table.add_row([date[i], self.other_four_day['day%s' % i], self.other_four_day['night%s' % i]])
        print(table)

    def run(self):
        self.get_soup()
        self.parse_soup()
        self.show_data()

if __name__ == '__main__':
    while True:
        C = input('City [Q for quit]: ')
        if C == 'Q':
            break
        try:
            w = WeatherSina(C)
            w.run()
        except TypeError:
            print('城市名称输入错误\n')
