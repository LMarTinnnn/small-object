from urllib import parse, request, error
import re
from http import cookiejar
url = 'http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F'
user_agent = 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
headers = {
    # 'User_Agent': user_agent,
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Accept-Language': 'zh-CN,zh;q=0.8',
    # 'Cache-Control':'max-age=0',
    # 'Connection': 'keep-alive',
    # 'Content-Type': 'application/x-www-form-urlencoded',
    # 'Host': 'idas.uestc.edu.cn',
    # 'Origin': 'http://idas.uestc.edu.cn',
    # 'Referer': 'http://idas.uestc.edu.cn/authserver/login',
}
post_data = {
    # 这几个都是必须的
    'username': '',
    'password': '',
    'lt': '',
    'execution': '',
    'dllt': 'userNamePasswordLogin',
    '_eventId': 'submit',
    # 'rmShown': 1
}


# make cookiejar
filename = 'uestc_cookie.txt'
cookie = cookiejar.MozillaCookieJar(filename)
handler = request.HTTPCookieProcessor(cookie)
opener = request.build_opener(handler)

# get post data key value
response = opener.open(url)
source = response.read().decode()
_re_lt = re.compile(r'name="lt" value="([\w-]*)"')
_re_execution = re.compile(r'name="execution" value="([\w-]*)"')
lt = _re_lt.search(source).group(1)
execution = _re_execution.search(source).group(1)
post_data['username'] = input('学号: ')
post_data['password'] = input('密码: ')
post_data['lt'] = lt
post_data['execution'] = execution
data_url_encode = parse.urlencode(post_data).encode()


_request = request.Request(url, data=data_url_encode, headers=headers)
response = opener.open(_request)
cookie.save(ignore_discard=True, ignore_expires=True)

course_ulr = 'http://portal.uestc.edu.cn/index.portal'
resp = opener.open(course_ulr)
with open('kecheng.html', 'wb') as file:
    file.write(resp.read())
print('嘿嘿～')


