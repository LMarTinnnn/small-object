from bs4 import BeautifulSoup as BS
import requests
import re

if __name__ == '__main__':
    page = requests.get('http://91.t9l.space/forumdisplay.php?fid=19&page=2', allow_redirects=False)
    page.encoding = 'utf-8'
    soup = BS(page.text, 'lxml')
    # print(soup.prettify())
    print(str(soup.head.title.string))

    """
    url_list_dup = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if ('viewthread' and 'extra') in href and 'page=' not in href:
            url_list_dup.append(link.get('href'))
    url_list_single = list(set(url_list_dup))
    for url in url_list_single:
        print(url)
    """