import requests
import re, os, threading
from time import ctime
from queue import Queue
from time import sleep

# -------------------- 91 会屏蔽ip 需要重新拨号或者 使用代理------------


class Spider91(object):
    def __init__(self):
        self.content_url = 'http://91.t9l.space/forumdisplay.php?fid=19&page='
        self.base_url = 'http://91.t9l.space/'

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}

        self.cookies = {'cookie': '__cfduid=d1264b2275a6d6f34d14a0eb09c06ba3f1479917979;'
                                  ' CzG_visitedfid=19D11; CzG_sid=a3D31N; __utmt=1;'
                                  ' CzG_oldtopics=D215761D; CzG_fid19=1480082167; AJSTAT_ok_pages=3;'
                                  ' AJSTAT_ok_times=1; __utma=127511109.1348312587.1480080455.1480080455.1480080455.1;'
                                  ' __utmb=127511109.3.10.1480080455; __utmc=127511109;'
                                  ' __utmz=127511109.1480080455.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}

        self.proxies = {'http://185.103.21.53': 'http://185.103.21.53:80',
                        'http://88.159.151.163': 'http://88.159.151.163:80',
                        '197.97.146.62': '197.97.146.62:8080'}

        self.whole_page_num = None
        self._re_url = re.compile(r'<span id=".*?"><a href="(.*?);extra.*?">(.*?)</a></span>')
        self._re_img = re.compile(r'<img src=".*?" file="(.*?\.jpg)".*?>')
        # item in the Queue are two list
        self.queue_of_url_list_and_title_list = Queue()
        # item in the Queue are a list and a string
        self.queue_of_img_list_and_title = Queue()

    def make_url(self, page_num):
        return self.content_url + str(page_num)

    def get_page_url_and_title(self, content_url):
        """
        get_page_url(content_url) ==> put  (page_url_list, page_title) into queue1
        :param content_url:  url of content page
        :return: nothing
        """
        print('正在 %s 中搜索帖子...' % content_url)
        page_url_list = []
        title_list = []
        while True:
            try:
                r = requests.get(content_url, allow_redirects=False, timeout=1, proxies=self.proxies,
                                 cookies=self.cookies)
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    for page, title in self._re_url.findall(r.text)[9:]:
                        print('找到名为[%s]的帖子并加入队列...' % title)
                        # print(page, title)
                        page_url_list.append(self.base_url + page)
                        title_list.append(''.join(title.split('/')))
                    self.queue_of_url_list_and_title_list.put((page_url_list, title_list))
                    break
            except:
                print('链接故障 尝试重连')

    def get_img_url_and_pass_title(self, page_url, page_title):
        """
        get_img_url(page_url) ==> put tuple (img_url_list, page_title) into queue2
        :return: nothing
        """

        img_url_list = []
        while True:
            try:
                r = requests.get(page_url, allow_redirects=False, cookies=self.cookies, timeout=1)
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    for img in self._re_img.findall(r.text):
                        img_url_list.append(self.base_url + img)
                    if img_url_list:
                        self.queue_of_img_list_and_title.put((img_url_list, page_title))
                    break
            except:
                pass

    def mk_dir(self, page_title):
        if os.path.exists('%s' % page_title):
            print("已经爬过 %s" % page_title)
            return False
        else:
            print('创建 %s' % page_title)
            os.mkdir('%s' % page_title)
            return True

    def pull_img(self, img_url_list, page_title):

        print('当前有 %s 个线程在工作' % threading.active_count())
        print('----------开始下载 %s ...----------' % page_title)

        i = 0  # 用于给文件编号
        for img_url in img_url_list:
            print('%s 正在努力加载 %s img-%s ' % (threading.current_thread().name, page_title, i))
            with open(os.path.join('%s' % page_title, str(i)) + '.jpg', 'wb') as file:
                i += 1
                while True:
                    while True:
                        # 91porn 有个傻逼的机制 多次访问之后 会给你跳到别的页面去 多刷新几次就好了
                        # 擦。。。。 原来还会封ip！！！！
                        r = requests.get(img_url, allow_redirects=False, proxies=self.proxies)
                        # print(r.url)
                        if r.url == img_url:
                            break
                        sleep(5)

                    if r.status_code == 200:
                        file.write(r.content)
                        break
        print('----------%s 下载完毕----------' % page_title)

    def produce_page_and_title(self, start_page_num, end_page_num):
        """

        :param start_page_num:  the page number spider start at
        :param end_page_num:    the page number spider end at (include this page)
        put production into queue
        """
        self.whole_page_num = end_page_num - start_page_num + 1
        for page_num in range(start_page_num, end_page_num + 1):
            content_url = self.make_url(page_num)
            threading.Thread(target=self.get_page_url_and_title, args=(content_url,)).start()

    def produce_img_and_title(self):
        for i in range(self.whole_page_num):
            page_url_list, page_title_list = self.queue_of_url_list_and_title_list.get()
            zipped_list = list(zip(page_url_list, page_title_list))
            for page_url, page_title in zipped_list:
                threading.Thread(target=self.get_img_url_and_pass_title, args=(page_url, page_title)).start()

    def consume(self):
        """
        consume production in queue
        :return:  No Return
        """
        print('等待生产完成～')
        sleep(3)
        while True:
            try:
                img_url_list, page_title = self.queue_of_img_list_and_title.get(timeout=1)
                while threading.active_count() > 20:  # 限制当前线程数量
                    sleep(5)
                if self.mk_dir(page_title):
                    threading.Thread(target=self.pull_img, args=(img_url_list, page_title)).start()
            except:
                break

    def download(self, start_page_num, end_page_num):
        print('开始生产')
        self.produce_page_and_title(start_page_num, end_page_num)
        self.produce_img_and_title()
        self.consume()


if __name__ == '__main__':
    goal = 800
    now = 100

    s = Spider91()
    while now < goal:
        threading.Thread(target=s.download, args=(now, now + 5)).start()
        now += 6
        sleep(300)  # 限制爬虫速度
