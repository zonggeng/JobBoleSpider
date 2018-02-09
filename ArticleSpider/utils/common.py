import hashlib


def get_md5(url):
    # 在python3中str字符串就是 unicode 如果是str的话就转码
    if isinstance(url, str):
        url = url.encode('utf-8')  # 这个库不接受unicode编码的
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print(get_md5('http://jobbole.com'))
