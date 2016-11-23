from urllib import parse, request
import re
import threading
from atexit import register

# 中间有跳转页 暂时不知道怎么处理

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
           #'Host': '91.t9l.space',
           'Referer': 'http://91.t9l.space/index.php',
           'Cookie': '__cfduid=d1264b2275a6d6f34d14a0eb09c06ba3f1479917979; CzG_sid=rrl9p0; CzG_visitedfid=19; '
                     'CzG_oldtopics=D215816D; CzG_fid19=1479919623; __utmt=1; AJSTAT_ok_pages=4; '
                     'AJSTAT_ok_times=1; __utma=127511109.2131495891.1479917987.1479917987.1479917987.1;'
                     ' __utmb=127511109.4.10.1479917987; __utmc=127511109;'
                     ' __utmz=127511109.1479917987.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}


_re_page_url = re.compile(r'<a href="(.*?)">(.*?)</a>')
url = 'http://91.t9l.space/forumdisplay.php?fid=19'
req = request.Request(url, headers=headers)
page = request.urlopen(req).read().decode()
print(page)
a = _re_page_url.findall(page)
print(a)


class Spider91(object):
    def __init__(self, start_page, end_page):
        self. start_page = start_page
        self. end_page = end_page
        self.base_url = 'http://91.t9l.space/forumdisplay.php?fid=19&page='
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}

    def make_url(self, page):
        return self.base_url + str(page)

