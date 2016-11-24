from urllib import parse, request
import re
import os
import threading
from atexit import register
from time import ctime
_re_img = re.compile(r'<a href=["\'](.*?.jpg)["\'] title=["\'].*?[\'"].*?>')


class RosiMm(object):
    def __init__(self):
        self.url = 'http://www.mmxyz.net/rosi-'

    def make_url(self, id_num):
        return self.url + str(id_num) + '/'

    def get_data(self, pattern, url):
        page = request.urlopen(url).read().decode()
        all_imgs_url = pattern.findall(page)
        return all_imgs_url

    def mk_dir(self, id_num):
        if os.path.exists('rosi-' + str(id_num)):
            print("已经爬过 rosi-%s" % id_num)
            return False
        else:
            print('创建 rosi-%s' % id_num)
            os.mkdir('rosi-%s' % id_num)
            return True

    def pull_img(self, data, id_num):
        i = 0
        for img_url in data:
            print('%s 正在努力加载 rosi-%s img-%s ' % (threading.current_thread().name, id_num, i))
            with open(os.path.join('rosi-%s' % id_num, str(i)) + '.jpg', 'wb') as file:
                file.write(request.urlopen(img_url).read())
            i += 1

    def get_one(self, id_num):
        url = self.make_url(id_num)
        data = self.get_data(_re_img, url)
        if self.mk_dir(id_num):
            t = threading.Thread(target=self.pull_img, args=(data, id_num))
            t.start()
        else:
            pass

    def get_many(self, start, end):
        for i in range(start, end + 1):
            t = threading.Thread(target=self.get_one, args=(i,))
            t.start()

@register
def _atexit():
    print('报告长官 完成任务 %s' % ctime())

if __name__ == '__main__':
    r = RosiMm()
    r.get_many(1000, 1300)

