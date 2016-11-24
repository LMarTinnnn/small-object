from urllib import request
import re
import os
import threading
from atexit import register
from time import ctime
import time

# 这家的前端程序员干活不讲规矩啊！！！ 他妈的 html标签居然大写的？？？？   
# 更糟心的是chrome 开发者状态查看的时候会自动小写 QAQ
# 各种匹配不上
_re_page_url = re.compile(r'<A href="(.*?)" title')

# 单引号要转义
_re_img = re.compile(r'<img src=\'(.*?.jpg)\' alt.*? title.*?>')
_re_page_num = re.compile(r'共(\d*)页')
_re_page_name = re.compile(r'<H1>(.*?)</H1>')


class Hmrt(object):
    def __init__(self):
        self.url = 'http://www.hmrenti.net/tuigirl/'
        self.base_url = 'http://www.hmrenti.net'

    def make_url(self, page):
        if page == 1:
            return self.url
        else:
            return self.url + str(page) + '.html'
     
    # 下面这三个函数实现get一个图片系列下 ‘所有页面’ 的子图集URL的获取 其实写成一个函数就好  
    # 开始写的时候思路有些不清晰 因此选择分步骤 其实意义不大
    def get_url_list(self, page_id):
        url = self.make_url(page_id)
        page = request.urlopen(url).read().decode('GBK')
        page_list = _re_page_url.findall(page)
        return list(set(page_list))
   
    def make_full_url_list(self, page_list):
        new_list = []
        for page in page_list:
            page = self.base_url + page
            new_list.append(page)
        return new_list

    # 上面两个函数的 wrapper
    def get_full_url_list(self, page_id):
        ls = self.get_url_list(page_id)
        return self.make_full_url_list(ls)

    # 子图集所有页面的 iamge url 以及 子图集的名称
    def re_img_list_and_page_name(self, url):
        img_url_list = []
        # 先弄第一页
        page = request.urlopen(url).read().decode('GBK')
        page_name = _re_page_name.findall(page)[0]
        img_url = _re_img.findall(page)
        img_url_list.append(img_url[0])
        page_num = _re_page_num.findall(page)[0]
        print('开始加载 %s' % page_name)
        # 再弄后面的
        for index in range(2, int(page_num) + 1):
            u = url.rstrip('.html') + '_%s' % index + '.html'
            page = request.urlopen(u).read().decode('GBK')
            img_url = _re_img.findall(page)
            try:
                img_url_list.append(img_url[0])
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

    h = Hmrt()
    h.run(2, 3)
    #print(h.re_img_list_and_page_name('http://www.hmrenti.net/tuigirl/7127.html'))