from urllib import parse, request
from _re_ import get_data, _re_private_domain
import os
import threading
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}

class TaoMM(object):
    def __init__(self):
        self.url = 'http://mm.taobao.com/json/request_top_list.htm'
        self.threads = []

    def get_page(self, page_index):
        page_url = 'http://mm.taobao.com/json/request_top_list.htm' + '?page=' + str(page_index)
        req = request.Request(page_url, headers=headers)
        page = request.urlopen(req).read().decode('GBK')
        return page

    def get_data(self, page_html):
        data = get_data(page_html)
        return data

    # 淘女郎主页会有访问限制 不知道怎么整
    ''' 先不管了
    def All_img(self, one_data):
        img_url = one_data[1]
        print(img_url)
        page = request.urlopen(img_url).read().decode('GBK')
        print(_re_img.findall(page))'''

    def mk_dir(self, data):
        if os.path.exists(data[0]):
            print('%s目录已存在' % data[0])
            return False
        else:
            print('创建名字为 %s 的文件夹' % data[0])
            os.makedirs(data[0])
            return True

    def save_icon(self, data):
        icon_url = data[2].split('_60x60.jpg')[0]
        with open(os.path.join(data[0], '%s_icon.jpg' % data[0]), 'wb') as file:
            file.write(request.urlopen(icon_url).read())

    def save_info(self, data):
        info = '%s\n%s\n%s' % (data[0], data[3], data[4])
        with open(os.path.join(data[0], '%s_information.txt' % data[0]), 'w') as file:
            file.write(info)

    # 访问限制
    def save_mm_page(self, data):
        page = data[1]
        with open(os.path.join(data[0], '%s_主页.html' % data[0]), 'wb') as file:
            file.write(request.urlopen(page).read())

    def save(self, data):
        if self.mk_dir(data):
            self.save_icon(data)
            self.save_info(data)
            self.save_mm_page(data)
        else:
            self.save_info(data)
            self.save_icon(data)
            self.save_mm_page(data)

    def get_a_page(self, page_index):
        page = self. get_page(page_index)
        data_page = self.get_data(page)
        for data in data_page:
            print(data)
            req = request.Request(data[1] + '&is_coment=false', headers=headers)
            gr_page = request.urlopen(req).read().decode('GBK')
            print(gr_page)
            #domain = _re_private_domain.findall(gr_page)
            #print(domain)
            t = threading.Thread(target=self.save, args=(data,))
            self.threads.append(t)
            t.start()

    def get_pages(self, start, end):
        for i in range(start, end + 1):
            t = threading.Thread(target=self.get_a_page, args=(i,))
            t.start()
        for t in self.threads:
            t.join()


if __name__ == '__main__':
    spider = TaoMM()
    spider.get_pages(1, 1)
