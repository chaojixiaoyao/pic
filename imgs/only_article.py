# encoding:utf-8
import os
import hashlib
import sqlite3
import requests
import json
from lxml import etree
from lxml.html.clean import Cleaner
import lxml.html.clean as clean
import uuid
import re


conn = sqlite3.connect('pic.db')
c = conn.cursor()


def md5(pwd):
    SALT = b'!@#123qwe'  # 约定好要加的盐值，可以为任何值
    # 实例化对象
    obj = hashlib.md5(SALT)
    # 写入要加密的字节
    obj.update(pwd.encode('utf-8'))
    # 获取密文
    return obj.hexdigest()


def decode_():
    if md5('How-to-start-Python1') == '6f4c254fc80675de0d889045be871495':  # 字符串为加盐之后散列后的MD5值
        print('登录成功')
    else:
        print('登录失败')


def upload(img_path):
    data = {
        "list": [img_path]
    }
    rsp = requests.post('http://127.0.0.1:9898/upload', data=json.dumps(data)).text
    print(rsp)


def cut(img_ls):
    from PIL import Image
    for img_item in img_ls:
        img = Image.open(img_item['last_name'])
        cropped = img.crop((0, 0, img.size[0], img.size[1] - 100))  # (left, upper, right, lower)
        cropped.save(img_item['last_name'])


def download_img_csdn(csdn_url):
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    url = csdn_url
    rsp = requests.get(url, headers=headers).text
    print(rsp)
    xhtml = etree.HTML(rsp)
    img_href = xhtml.xpath('//div[@id="content_views"]//img/@src')
    # img_href = xhtml.xpath('//*[@id="js_content"]/section//img/@data-src')
    print(img_href)
    hrefs = []
    for href in img_href:
        last_name = href.split('/')[-1]
        bty = requests.get(href, headers=headers).content
        if 'png' not in last_name or 'jpg' not in last_name:
            last_name = str(uuid.uuid4()) + '.png'
            # print(href, '>>', last_name)
        with open(last_name, 'wb')as fp:
            fp.write(bty)
        hrefs.append({'href': href, 'last_name': last_name})
    return hrefs


def download_img_wechat():
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    with open('article.html', 'r', encoding='utf-8')as fp:
        rsp = fp.read()
    img_href = re.findall(r'src="(.*?)"', rsp)
    hrefs = []
    for href in img_href:
        if 'https' not in href:
            continue
        last_name = href.split('/')[-1]
        try:
            bty = requests.get(href, headers=headers).content
        except requests.exceptions.MissingSchema as me:
            continue
        if 'png' not in last_name or 'jpg' not in last_name:
            last_name = str(uuid.uuid4()) + '.png'
            # print(href, '>>', last_name)
        with open(last_name, 'wb')as fp:
            fp.write(bty)
        hrefs.append({'href': href, 'last_name': last_name})
    return hrefs


# https://mmbiz.qpic.cn/mmbiz_gif/h6NqozYcCQ6cuFGiakibI3WcZh51ibcIHF3mRgdJEPYOZmMap3O0cqOm1TQI3pFwzL0hYRL29wvzrqojgc7ICicafQ

def upload_last():
    path = os.path.dirname(os.path.realpath(__file__))
    # 获取该目录下所有文件，存入列表中
    fileList = os.listdir(path)
    fileList.remove('tran.py')
    fileList.remove('pic.db')
    fileList.remove('article.html')
    fileList.remove('last_article.html')

    for i in fileList:
        # 设置旧文件名（就是路径+文件名）
        old_name = path + os.sep + i  # os.sep添加系统分隔符

        data = {
            "list": [old_name]
        }
        rsp = requests.post('http://127.0.0.1:9898/upload', data=json.dumps(data)).text
        print(old_name, '======>', rsp)
        os.remove(old_name)


def passed():
    path = os.path.dirname(os.path.realpath(__file__))
    # 获取该目录下所有文件，存入列表中
    fileList = os.listdir(path)
    fileList.remove('tran.py')
    fileList.remove('pic.db')
    fileList.remove('article.html')
    fileList.remove('last_article.html')

    for i in fileList:
        # 设置旧文件名（就是路径+文件名）
        old_name = path + os.sep + i  # os.sep添加系统分隔符

        # 设置新文件名
        last_name = i.split('.')[1]
        new_salt_name = str(uuid.uuid1())

        os.rename(old_name, new_salt_name + f'.{last_name}')  # 用os模块中的rename方法对文件改名
        print(old_name, '======>', 'https://src.codeschat.com/imgs/' + new_salt_name + f'.{last_name}')

    # sql = "INSERT INTO pics(name, md5_salt_name, type) VALUES(?, ?, ?)"
    # c.executemany(sql, ls)
    # conn.commit()


def sub_href(href_ls, ID_):
    import sqlite3
    db = sqlite3.connect('../../../db.sqlite3')
    cc = db.cursor()
    sql = f"""SELECT id, content FROM post_post WHERE url='{ID_}.html'"""
    cc.execute(sql)
    val = cc.fetchone()
    content = val[1]
    id_ = val[0]
    for href in href_ls:
        print(href['last_name'])
        content = content.replace(href['href'], 'https://src.codeschat.com/imgs/' + href['last_name'])
    cc.execute(f"UPDATE post_post SET content='{content}' WHERE id={id_}")
    db.commit()


def sub_href_from_website():
    with open('article.html', 'r', encoding='utf-8')as fp:
        content_base = fp.read()

    safe_attrs = clean.defs.safe_attrs
    cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=['src'])
    content = cleaner.clean_html(content_base)
    # content = Cleaner(style=True).clean_html(content_base)

    # for href in href_ls:
        # print(href['last_name'])
        # print(href['href'])
        # content = content.replace(href['href'], 'https://src.codeschat.com/imgs/' + href['last_name'])
    with open('last_article.html', 'w', encoding='utf-8')as fp:
        fp.write(content)


if __name__ == '__main__':
    # decode_()
    # passed()
    # test()

    # result = download_img('https://mp.weixin.qq.com/s/FTBmbiMwxTTB0Y-okk0_6A')

    # url = 'https://mp.weixin.qq.com/s/lXlAlm6Ay4A38ChyC0S_Lg'
    # result = download_img_wechat()

    # cut(result)
    # result = []
    sub_href_from_website()

    # passed()
    # upload_last()