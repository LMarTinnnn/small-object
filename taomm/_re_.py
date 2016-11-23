import re
from urllib import request
_re_name = re.compile(r'<a class="lady-name".*?>(.*?)</a>')
_re_info_url = re.compile(r'<a class="lady-name" href="(.*?)" target="_blank">')
_re_icon = re.compile(r'img src="(.*?)"')
_re_location = re.compile(r'<span>(.*?市)')
_re_job = re.compile(r'<em>(平面模特.*?)</em>')
_re_private_domain = re.compile(r'<span>(//.*?)</span>')


def get_data(page):
    name = _re_name.findall(page)
    info_url = _re_info_url.findall(page)
    icon = _re_icon.findall(page)
    location = _re_location.findall(page)
    job = _re_job.findall(page)

    result = []
    i = 0
    while 1:
        try:
            result.append([name[i], 'http:' + info_url[i], 'http:' + icon[i], location[i], job[i]])
            i += 1
        except IndexError:
            break
    return result
