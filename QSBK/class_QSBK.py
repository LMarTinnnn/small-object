from urllib import request
import re
import threading
import time
import sys


class QSBK(object):
    def __init__(self):
        self.url = 'http://www.qiushibaike.com/text/page/'
        self.page_now = 1
        # initiate headers
        self.headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        # store articles
        self.articles = []
        self.End = False

    def create_url(self):
        return self.url + str(self.page_now)

    def get_data(self, url):
        # 获得一页数据 当前页数加一
        self.page_now += 1
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        # re_match
        html = response.read().decode().replace('\n', '')
        _re_author = re.compile(r'<h2>(.*?)</h2>')
        _re_content = re.compile(r'<div class="content"><span>(.*?)</span></div>')
        _re_comment = re.compile(r'<i class="number">(.*?)</i>')
        author_list = _re_author.findall(html)
        content_list = [item for item in _re_content.findall(html) if item]
        comment_list = _re_comment.findall(html)
        article_one_page = []
        for i in range(len(author_list)):
            article_one_page.append([author_list[i], content_list[i], comment_list[i]])
        return article_one_page

    def load_article(self):
        while True:
            if self.End:
                break
            if len(self.articles) < 2:
                # load 5 pages each time
                for i in range(5):
                    self.articles.append(self.get_data(self.create_url()))
            time.sleep(60)

    def get_one_page(self):
        one_page = self.articles.pop(0)
        return one_page

    def output(self):
        page = self.get_one_page()
        while True:
            author, content, comment = page.pop(0)
            article = '\n作者：{}  赞:{}\n{}\n'.format(author, comment, content.replace('<br/>', '\n'))
            print(article)

            check = input("[Q]for quit, 回车继续阅读:")
            if check == 'Q':
                self.End = True
                break
            if len(page) == 0:
                break

    def run(self):
        load_thread = threading.Thread(target=self.load_article)
        load_thread.start()
        print('----------please wait a moment----------')
        time.sleep(2)
        while not self.End:
            self.output()


myQSBK = QSBK()
myQSBK.run()
print('Thanks for using!')
