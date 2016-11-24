from urllib import request
import re
import os
import threading
from atexit import register
from time import ctime
import time

# 会重复两次
_re_page_url = re.compile(r'<a href="(.*?)" target="_blank">')
_re_img = re.compile(r'<li><img alt=".*?" src="(.*?)" /></a></li>')

# name取列表最后一个
_re_page_name = re.compile(r'<h1>(.*?)</h1>')


class LesMao(object):
    def __init__(self, url):
        self.url = url

    def make_url(self, page):
        return self.url + str(page) + '.html'

    def get_full_url_list(self, page_id):
        url = self.make_url(page_id)
        page = request.urlopen(url).read().decode()
        page_list = _re_page_url.findall(page)
        return list(set(page_list))

    def re_img_list_and_page_name(self, url):
        img_url_list = []
        # 先弄第一页
        page = request.urlopen(url).read().decode()
        page_name = _re_page_name.findall(page)[-1]
        img_url = _re_img.findall(page)
        img_url_list += img_url
        page_num = 5
        print('开始加载 %s' % page_name)
        # 再弄后面的
        for index in range(2, page_num + 1):
            # 'http://www.lesmao.com/thread-15032-1-1.html'
            _re_temp = re.compile(r'(http://www\.lesmao\.com/thread-\d*?)-\d*?-\d*?\.html')
            u = _re_temp.findall(url)[0] + '-%s-%s' % (index, index) + '.html'
            page = request.urlopen(u).read().decode()
            img_url = _re_img.findall(page)
            try:
                img_url_list += img_url
            except IndexError:
                pass
        return img_url_list, page_name

    def mk_dir(self, page_name):
        if os.path.exists('%s' % page_name):
            print("已经爬过 %s" % page_name)
            return False
        else:
            print('创建 %s' % page_name)

            # 文件名字中可能会出现 '／'影响文件夹创建 再想想好办法 -------------------------------
            os.mkdir(('%s' % page_name)[:16])
            return True

    def pull_img(self, img_url_list, page_name):
        i = 0
        for img_url in img_url_list:
            print('%s 正在努力加载 %s img-%s ' % (threading.current_thread().name, page_name, i))
            with open(os.path.join(('%s' % page_name)[:16], str(i)) + '.jpg', 'wb') as file:
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
        print('显示加载后可能会因为网速 有20秒左右没反应 请稍等(不要着急 我试了 没bug的)')
        for i in range(start, end + 1):
            full_url_list = self.get_full_url_list(i)
            for one_url in full_url_list:
                t = threading.Thread(target=self.get_one, args=(one_url,))
                t.start()

@register
def _atexit():
    print('报告长官 完成任务 %s' % ctime())

if __name__ == '__main__':
    url = 'http://www.lesmao.com/forum-43-'
    l = LesMao(url)
    l.run(7, 9)
