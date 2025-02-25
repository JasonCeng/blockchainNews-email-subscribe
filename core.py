# !/usr/bin/env python
# coding=utf-8

import os
import time
import datetime
import requests
import smtplib
import re
from email.header import Header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import jieba # cutting Chinese sentences into words
from collections import Counter
from wordcloud import WordCloud,STOPWORDS

from receivers import MAIL_RECEIVER

KEY_WORD = '区块链'
PRE_URL = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word=' + KEY_WORD + '&pn='
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Connection": "close",
}
requests.DEFAULT_RETRIES = 5

MAIL_ENCODING = "utf8"

# 隐私数据存放在环境变量中
MAIL_HOST = os.environ.get("MAIL_HOST") #'smtp.qq.com'#固定写死
MAIL_PORT = 587 #固定端口
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS") #授权码（这个要填自己获取到的）
MAIL_SENDER = os.environ.get("MAIL_SENDER")

today = datetime.datetime.now().date()
EMAIL_TITLE = "区块链资讯午报" + str(today)

FONTS_PATH = "./fonts/msyh.ttc"
STOP_WORDS_PATH = "./config/stop_words.txt"

def crawl_news(pageNum):
    """
    爬取百度咨询前pageNum页新闻标题
    """
    # print("pageNum:",pageNum)
    titlesText = ''

    s = requests.session()
    s.keep_alive = False

    for i in range(pageNum):
        START_URL = PRE_URL + str(i * 10)
        # print(START_URL)
        titlesText += "</br>" + "<a href='" + START_URL + "'>" + "查看搜索详情页面" + "</a></br>"

        # time.sleep(60)
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
    # IMAGE_HREF = "https://github.com/JasonCeng/blockchainNews-email-subscribe/blob/main/wordcloud/single_wcd.png"
    return html.format(EMAIL_TITLE, content)

def send_email(title, content):
    """
    发送邮件
    """
    content = build_emailHTML(content)
    message = MIMEText(content, "html", MAIL_ENCODING)
    message["From"] = Header(f"{MAIL_SENDER}")
    message["To"] = Header("Reader")
    message["Subject"] = Header(EMAIL_TITLE)
    try:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as smtp_obj:
            # smtp_obj.set_debuglevel(1)  # 开启调试输出
            # 显式开启TLS
            smtp_obj.starttls()
            smtp_obj.login(MAIL_USER, MAIL_PASS)
            smtp_obj.sendmail(MAIL_SENDER, MAIL_RECEIVER, message.as_string())
    except Exception as e:
        print('Email send Exception:' + str(e))
    print('Email send success')

def cut_word(text):
    """
    利用jieba对text进行分词处理，排除长度为1的词
    """
    # 加载自定义停用词
    STOPWORDS_CH = open(STOP_WORDS_PATH, encoding='utf8').read().split()
    # 去除字母、数字、标点符号
    preText = re.sub('[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\。\@\#\\\&\*\%]', '', text)
    # 进行jieba分词并剔除停用词及长度为1的词
    word_list = [
        w for w in jieba.cut(preText) 
        if w not in set(STOPWORDS_CH) and len(w) > 1
        ]
    # for word in word_list:
    #     print(word)
    return word_list

def generate_wordcloud(word_list):
    freq = dict(Counter(word_list))
    wcd = WordCloud(font_path=FONTS_PATH, stopwords=STOPWORDS, background_color='white')
    wcd.generate_from_frequencies(freq)
    return wcd

def plt_imshow(x, ax=None, show=True):
    if ax is None:
        fig, ax = plt.subplots()
    ax.imshow(x)
    ax.axis("off")
    # if show: plt.show()
    return ax

def save_wordcloud(ax):
    ax.figure.savefig(f'./wordcloud/single_wcd.png', bbox_inches='tight', dpi=1000)

if __name__ == "__main__":
    print("----------test crawl_news start----------")
    pageNum = 5
    content = crawl_news(pageNum)
    # word_list = cut_word(content)
    # wcd = generate_wordcloud(word_list)
    # ax = plt_imshow(wcd,)
    # save_wordcloud(ax)
    send_email(EMAIL_TITLE, content)
    print("----------test crawl_news end----------")