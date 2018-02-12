import hashlib

import re


def get_md5(url):
    # 在python3中str字符串就是 unicode 如果是str的话就转码
    if isinstance(url, str):
        url = url.encode('utf-8')  # 这个库不接受unicode编码的
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def Remove_the_comma(text):
    return int(text.replace(',', ''))


if __name__ == '__main__':
    print(get_md5('http://jobbole.com'))
