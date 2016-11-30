# Queue and Set Daemon and
# Event 第一次用～ 用来调节生产
import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
from atexit import register

e_soup = threading.Event()
e_joke = threading.Event()


class Joke(object):
    def __init__(self):
        self.base_url = 'http://lengxiaohua.com/random'
        self.soup_queue = Queue()
        self.joke_queue = Queue()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}

    def get_soup(self):
        page = requests.get(self.base_url, headers=self.headers).text
        soup = BeautifulSoup(page, 'lxml')
        self.soup_queue.put(soup)

    def parse_soup(self):
        soup = self.soup_queue.get()
        for joke in soup.find_all('pre', js='joke_summary'):
            self.joke_queue.put(''.join(joke.strings))

    def produce_soup(self):
        while True:
            e_soup.wait()
            for i in range(5):
                self.get_soup()
            e_soup.clear()

    def produce_joke(self):
        while True:
            e_joke.wait()
            self.parse_soup()
            e_joke.clear()

    def consumer(self):
        # check if soup queue is close to empty
        if self.soup_queue.qsize() < 2:
            e_soup.set()

        # check if joke queue is close to empty
        if self.joke_queue.qsize() < 2:
            e_joke.set()

        joke = self.joke_queue.get()
        print(joke, '\n')

    def run(self):
        t1 = threading.Thread(target=self.produce_soup, args=())
        t1.setDaemon(True)
        t2 = threading.Thread(target=self.produce_joke, args=())
        t2.setDaemon(True)
        t1.start()
        t2.start()
        print('-------------------- Please wait a moment --------------------')
        while 1:
            self.consumer()
            check = input('Enter to continue ([Q] for quit): \n')
            if check == 'Q':
                break


@register
def atexit_():
    print('-------------------- Thanks for using～ --------------------')

if __name__ == '__main__':
    j = Joke()
    j.run()
