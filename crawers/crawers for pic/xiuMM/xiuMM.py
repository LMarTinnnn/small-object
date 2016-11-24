from urllib import request
import re
import os
import threading
from atexit import register
from time import ctime, sleep
# 取第一个name
_re_page_name = re.compile(r'(美媛馆.*?V[Oo][Ll].*?)<')
_re_img = re.compile('<img src="(.*?.jpg)" alt')
_re_page_num = re.compile(r'共(\d*)页')
_re_page_url = re.compile(r'<a href="(/photos.*?)">')


class XiuMM(object):
    def __init__(self):
        self.url = 'http://www.xiumm.cc/albums/MyGirl'
        self.base_url = 'http://www.xiumm.cc'

    def make_url(self, page):
        if page == 1:
            return self.url + '.html'
        else:
            return self.url + '-%s' % page + '.html'

    # url在这个情况下 是 不包含 base_url 的不完全版, 所以要加上前缀
    def get_full_url_list(self, page_id):
        url = self.make_url(page_id)
        page = request.urlopen(url).read().decode()
        url_list = []
        for url in _re_page_url.findall(page):
            url_list.append(self.base_url + url)
        return url_list

    # return all image urls in a url and its name
    def re_img_list_and_page_name(self, url):
        img_url_list = []
        # 先弄第一页
        page = request.urlopen(url).read().decode()
        page_name = _re_page_name.findall(page)[0]
        img_url = _re_img.findall(page)
        for img in img_url:
            temp = self.base_url + img
            img_url_list.append(temp)
        page_num = _re_page_num.findall(page)[0]
        print('开始加载 %s' % page_name)
        # 再弄后面的
        for index in range(2, int(page_num) + 1):
            # 'http://www.xiumm.cc/photos/BoLoli-795.html'
            u = url.rstrip('.html') + '-%s' % index + '.html'
            page = request.urlopen(u).read().decode()
            img_url = _re_img.findall(page)
            try:
                # 跟上面的情况相同
                for img in img_url:
                    img_url_list.append(self.base_url + img)
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
def _at_exit():
    print('禀报老爷 完成任务用时 %s' % (ctime() - start_time))

if __name__ == '__main__':
    X = XiuMM()
    start_time = ctime()
    for n in range(1, 11):
        X.run(n, n)
        sleep(300)
