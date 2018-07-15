#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @date: 2018/7/15 上午10:30
# @author: Bill
# @file: main.py

import os
import re
from multiprocessing import Pool, cpu_count
import requests
from lxml import html
from choose_proxy import *
import random
from requests import ConnectionError

# Get random user-agent
def getUserAgent(ua_list):
    return random.choice(ua_list)



# Create a project directory
def createProjectDir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

# Choose a proxy address
def chooseProxy():
    ip = random.choice(proxy_ips)
    proxies = {"HTTP": ip}
    try:
        res = requests.get('http://www.tojker.com',proxies=proxies)
        if res.status_code == 200:
            return proxies
        else:
            return chooseProxy()
    except ConnectionError:
        return chooseProxy()


# Get set urls
def getSetUrls(indexurl):
    proxies = chooseProxy()
    try:
        res = requests.get(url=indexurl,headers=headers,proxies=proxies)
        tree = html.fromstring(res.text)
        set_urls = list()
        for each in tree.xpath('//ul[@class="boxlist"]/li'):
            hosturl = 'http://www.tojker.com'
            parturl = each.xpath('./a/@href')[0]
            set_url = hosturl + parturl
            set_urls.append(set_url)
        return set_urls
    except:
        print("Error!")


# Get pic urls
def getPicUrls(seturl):
    proxies = chooseProxy()
    try:
        res = requests.get(url=seturl,headers=headers,proxies=proxies)
        res.encoding = res.apparent_encoding
        tree = html.fromstring(res.text)
        illegal_str = r"[\/\\\:\*\?\"\<\>\| ]"  # 创建目录时的非法字符需要替换成_
        title = tree.xpath('//div[@class="content"]/h1/text()')[0].strip()
        new_title = re.sub(illegal_str,'_',title)
        for each in tree.xpath('//*[@class="imgbox"]'):
            pic_urls = each.xpath('./img/@data-original')
        return pic_urls,new_title
    except:
        print("Error")

# Download set pics
def saveImgs(pic_urls,new_title):
    header = {
        "User-Agent": getUserAgent(ua_list),
        "Host": "pic.tojker.com",
        "Referer": "http://www.tojker.com/hutu/page-1.html"
    }
    proxies = chooseProxy()
    if not os.path.exists(new_title):
        os.mkdir(new_title)
    print("开始下载套图{}！".format(new_title))
    for url in pic_urls:
        try:
            content = requests.get(url=url,headers=header,proxies=proxies).content
            # pic_name = md5(content).hexdigest()
            pic_name = projectdir + '/' + new_title + '/' + url.split('/')[-1]
            with open(pic_name,'wb') as f:
                f.write(content)
                print("正在下载：" + url)
        except:
            print("Error!")
    print("套图{}下载完毕！".format(new_title))


def main(set_url):
    # set_urls = getSetUrls(index_url)
    pic_urls,new_title = getPicUrls(set_url)
    saveImgs(pic_urls,new_title)



if __name__ == '__main__':
    headers = {
        "User-Agent": getUserAgent(ua_list),
        "Host": "www.tojker.com",
        "Referer": "http://www.tojker.com/hutu/page-2.html"
    }
    projectdir = os.getcwd() + '/tojker'
    createProjectDir(projectdir)
    os.chdir(projectdir)
    index_urls = ['http://www.tojker.com/hutu/page-{}.html'.format(i) for i in range(3,4)]
    for index_url in index_urls:
        set_urls = getSetUrls(index_url)
        pool = Pool(processes=cpu_count())
        pool.map(main,set_urls)




