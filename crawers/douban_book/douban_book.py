from bs4 import BeautifulSoup
import random
import requests
from queue import Queue
from urllib import parse
from IP_Pool.v2.Ip_pool_foreign import IpPool
import threading
from time import sleep
ua = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) "
    "Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
]

# ip in proxies is like 'http://host:port'

proxies = IpPool('https://book.douban.com/subject/26895253/', ip_number=5, foreign=False).give_me_ip()
assert proxies != [], '获取代理失败 可能是ip代理网站挂掉了 TAT。。。'
# proxies = ['http://94.23.249.218:3128']


class Page(object):
    def __init__(self, url):
        assert url.startswith('http:') or url.startswith('https:'), print('URL格式错误')
        self.url = url
        # self.headers = {'User-Agent': random.choice(headers)}
        self.ua = ua
        self.links = ''
        self.soup = self.get_soup()

    def get_soup(self):
        while True:
            proxy = dict(http=random.choice(proxies), https=random.choice(proxies))
            try:
                headers = dict(Uesr_Agent=random.choice(self.ua), Host='book.douban.com',
                               Referer='https://www.douban.com/')
                html = requests.get(self.url, headers=headers, proxies=proxy, timeout=2)
                assert html.status_code != 403
                return BeautifulSoup(html.text, 'lxml')
            except:
                print('%s was forbidden！！' % proxy['http'])

    def parse_links(self):
        links = []
        # print(self.soup.prettify())
        for a in self.soup.find_all('a'):
            try:
                link = a['href']
                if link.startswith('/') or link.startswith('http'):
                    links.append(link)
            except KeyError:
                print('发现错误链接....忽略ta...')
        return links

    def get_book_info(self):
        info = dict()
        info['title'] = list(self.soup.find('h1').stripped_strings)[0]
        info_list = list(self.soup.find(id='info').stripped_strings)
        # for i in enumerate(info_list):
            # print(i)
        info['author'] = info_list[2]
        info['price'] = info_list[15]
        info['ISBN'] = info_list[-1]
        info['rating'] = self.soup.find('strong').string.strip()
        return info


class Crawler(object):
    count = 0

    def __init__(self, url_start):
        self.url_queue = Queue()
        self.url_queue.put(url_start)
        self.seen = set()
        # 用于限定爬取的域名范围
        self.netloc = parse.urlparse(url_start).netloc

    def find_links_and_books(self):
        url = self.url_queue.get()
        page = Page(url)
        Crawler.count += 1
        print('\n(%s)' % Crawler.count)
        print('URL: ' + url)

        # 不太会匹配。。。。
        if 'subject' in url:
            print(2 * '------------------------------------------------------------')
            try:
                self.add_book(page)
            except AttributeError:
                print('好多subject域名啊 。。。。')
            except IndexError:
                print('页面残缺啊啊啊啊  怎么匹配啊')

        links = page.parse_links()
        for link in links:
            # douban url start with 'https'
            if link.startswith('/'):
                link = 'https://' + self.netloc + link

            if link not in self.seen:
                print('* ' + link),
                self.seen.add(link)
                if self.netloc not in link:
                    pass
                    # print('... discard, not in domain')
                else:
                    # Queue is not iterable ， and I don't know how to solve it  ！！！！！！！！！
                    '''
                    if link not in self.url_queue:
                        print('...new, add into queue')
                        self.url_queue.put(link)
                    else:
                        print('...discard, already in queue')
                    '''
                    if 'amazon' not in link:
                        self.url_queue.put(link)
            # if already seen
            else:
                pass
                # print('...discard, already seen')

    def add_book(self, page):
        print(page.get_book_info())

    def run(self):
        while True:
            while threading.active_count() > 20:
                sleep(3)
            threading.Thread(target=self.find_links_and_books, args=()).start()
            sleep(random.randint(3, 10))
        print('没有啦～')


def main():
    # url = input('Start at: ')
    url = 'https://book.douban.com/subject/26895253/'
    if not url:
        return
    if not url.startswith('https'):
        url = 'https://%s/' % url
    c = Crawler(url)
    c.run()

if __name__ == '__main__':
    # print('Waiting for getting proxies')
    main()
    '''header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) '
                            'Gecko/20100101 Firefox/23.0'}
    proxy = dict(http=random.choice(proxies), https=random.choice(proxies))
    page = requests.get('https://book.douban.com/subject/26895253/', allow_redirects=False, timeout=2,
                        proxies=proxy, headers=header)
    print(page)'''

