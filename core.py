# !/usr/bin/env python
# coding=utf-8

import os
import datetime
import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

from receivers import MAIL_RECEIVER

KEY_WORD = '区块链'
PRE_URL = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word=' + KEY_WORD + '&pn='
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}

MAIL_ENCODING = "utf8"

# 隐私数据存放在环境变量中
MAIL_HOST = os.environ.get("MAIL_HOST") #'smtp.qq.com'#固定写死
MAIL_PORT = 465 #固定端口
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS") #授权码（这个要填自己获取到的）
MAIL_SENDER = os.environ.get("MAIL_SENDER")

today = datetime.datetime.now().date()
EMAIL_TITLE = "区块链资讯早报" + str(today) + "📅"

def crawl_news(pageNum):
    """
    爬取百度咨询前pageNum页新闻标题
    """
    # print("pageNum:",pageNum)
    titlesText = ''

    for i in range(pageNum):
        START_URL = PRE_URL + str(i * 10)
        # print(START_URL)
        titlesText += "</br>" + "<a href='" + START_URL + "'>" + "查看搜索详情页面" + "</a></br>"

        resp = requests.get(START_URL, headers=HEADERS)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text,'html.parser')  # 'html.parser'这是BeautifulSoup库的HTML解析器的用法,用于解析HTML
        # print(resp.text)

        titles = soup.select('h3')
        
        for title in titles:  # 使用循环输出爬取到的网页上的所有新闻标题
            # print(title.text)
            titlesText += title.text + '</br>'
        # print(titlesText)
    
    return titlesText

def build_emailHTML(content):
    """
    构造邮件全文HTML
    """
    html = """
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <div>
                <h1>{0}</h1>
                <p>{1}</p>
            <div>
        </body>
        </html>
    """
    # print(today)
    # print(str(html.format(today, content)))
    return html.format(EMAIL_TITLE, content)

def send_email(title,content):
    """
    发送邮件
    """
    content = build_emailHTML(content)
    message = MIMEText(content, "html", MAIL_ENCODING)
    message["From"] = Header("区块链资讯机器人", MAIL_ENCODING)
    message["To"] = Header("Reader", MAIL_ENCODING)
    message["Subject"] = Header(title, MAIL_ENCODING)
    try:
        smtp_obj = smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT)
        smtp_obj.login(MAIL_USER, MAIL_PASS)
        smtp_obj.sendmail(MAIL_SENDER, MAIL_RECEIVER, message.as_string())
        smtp_obj.quit()
    except Exception as e:
        print('Email send fail:' + str(e))
    print('Email send success')


if __name__ == "__main__":
    print("----------test crawl_news start----------")
    pageNum = 5
    content = crawl_news(pageNum)
    send_email(EMAIL_TITLE, content)
    print("----------test crawl_news end----------")