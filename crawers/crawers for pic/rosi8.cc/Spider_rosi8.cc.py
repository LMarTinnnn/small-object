from urllib import request
import re
import os
import threading
from atexit import register
from time import ctime

_re_page_url = re.compile(r'<li><a href="(.*?)".*?</li>')
_re_img = re.compile(r'<img src=\'(.*?.jpg)\' alt.*?>')

_re_page_num = re.compile(r'共(\d*)页')
_re_page_name = re.compile('<h1 class="yh">(.*?)</h1>')


class Rosi8(object):
    def __init__(self):
        self.url = 'http://www.rosi8.cc/AISS/'
        self.base_url = 'http://www.rosi8.cc'

    def make_url(self, page):
        return self.url + ('list%s' % page) + '.html'

    def get_url_list(self, page_id):
        url = self.make_url(page_id)
        page = request.urlopen(url).read().decode('GBK')
        page_list = _re_page_url.findall(page)
        return page_list

    def make_full_url_list(self, page_list):
        new_list = []
        for page in page_list:
            page = self.base_url + page
            new_list.append(page)
        return new_list

    def get_full_url_list(self, page_id):
        ls = self.get_url_list(page_id)
        return self.make_full_url_list(ls)

    def re_img_list_and_page_name(self, url):
        img_url_list = []
        # 先弄第一页
        page = request.urlopen(url).read().decode('GBK')
        page_name = _re_page_name.findall(page)[0]
        img_url = _re_img.findall(page)
        img_url_list.append(self.base_url + img_url[0])
        page_num = _re_page_num.findall(page)[0]
        print('开始加载 %s' % page_name)
        # 再弄后面的
        for index in range(2, int(page_num) + 1):
            u = url.rstrip('.html') + '_%s' % index + '.html'
            page = request.urlopen(u).read().decode('GBK')
            img_url = _re_img.findall(page)
            try:
                img_url_list.append(self.base_url + img_url[0])
            except IndexError:
                pass
        return img_url_list, page_name

    def mk_dir(self, page_name):
        if os.path.exists('%s' % page_name):
            print("已经爬过 %s" % page_name)
            return False
        else:
            print('创建 %s' % page_name)
            os.mkdir('%s' % page_name)
            return True

    def pull_img(self, img_url_list, page_name):
        i = 0
        for img_url in img_url_list:
            print('%s 正在努力加载 %s img-%s ' % (threading.current_thread().name, page_name, i))
            with open(os.path.join('%s' % page_name, str(i)) + '.jpg', 'wb') as file:
                file.write(request.urlopen(img_url).read())
            i += 1

    def get_one(self, one_url):
        img_url_list, page_name = self.re_img_list_and_page_name(one_url)
        if self.mk_dir(page_name):
            t = threading.Thread(target=self.pull_img, args=(img_url_list, page_name))
            print('%s 开始为老爷工作～～' % threading.current_thread().name)
            t.start()
        else:
            pass

    def run(self, start, end):
        for i in range(start, end + 1):
            full_url_list = self.get_full_url_list(i)
            for one_url in full_url_list:
                t = threading.Thread(target=self.get_one, args=(one_url,))
                t.start()


@register
def _atexit():
    print('报告长官 完成任务 %s' % ctime())


if __name__ == '__main__':
    R = Rosi8()
    R.run(51, 53)
