#!/usr/bin/env python3

import sys
import getopt
import numpy as np
import datetime
import re
import urllib.request
from bs4 import BeautifulSoup
from distutils.filelist import findall
import smtplib
from email.mime.text import MIMEText

def get_contents(url):
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        req_o = urllib.request.urlopen(req)
        contents = BeautifulSoup(req_o, 'html.parser')#.decode('gb2312')
        if req_o.status == 200:
            return contents
        else:
            return None
    except Exception:
        print('Request error!')
        return None

def filt_keywords(text_, keywords_):
    text_title_ = text_.find_all('dt')
    text_data_ = text_.find_all('dd')
    article_count_ = len(text_title_)
    result_ = []
    for count in range(article_count_):
        key_word_mark_all_ = False
        key_word_mark_ = [False for x in range(len(keywords_))]
        for j in range(len(keywords_)):
            if text_data_[count].find('p',text=re.compile(keywords_[j])) != None or \
            re.compile(keywords_[j]).search(text_data_[count].find('div', class_='list-title mathjax').get_text()) != None :
                key_word_mark_[j] = True
                key_word_mark_all_ = True
        if key_word_mark_all_:
            id_ = text_title_[count].find('span',{'class': 'list-identifier'}).get_text()
            link_ = text_title_[count].find('span',{'class': 'list-identifier'}).find('a',{'title': 'Abstract'})['href']
            link_ = ''.join(['https://arxiv.org%s' %(link_)])
            title_ = text_data_[count].find('div', class_='list-title mathjax').get_text().replace('\n','')
            subject_ = text_data_[count].find('div', {'class': 'list-subjects'}).get_text()[1:].replace('\n','')
            authors_ = text_data_[count].find('div', class_='list-authors').get_text().replace('\n','')[8:]
            text_ = text_data_[count].find('p').get_text().replace('\n',' ')
            key_word_str_ = '\nKey words: '
            for j in range(len(keywords_)):
                if key_word_mark_[j] == True:
                    key_word_str_ += str(keywords_[j])+' '
            result_.append(['['+str(count+1)+']'+str(id_), title_, authors_, str(subject_)+'\n', \
                            text_, key_word_str_, link_, '---------------\n'])
    return article_count_, result_

def get_info(contents_, keywords_):
    date_info_ = contents_.find('div', {'id': 'dlpage'}).find('h3').get_text()
    text_new_ = contents_.find('div', {'id': 'dlpage'}).find_all('dl')[0]
    text_cross_ = contents_.find('div', {'id': 'dlpage'}).find_all('dl')[1]
    article_count_new_, result_new_ = filt_keywords(text_new_, keywords_)
    article_count_cross_, result_cross_ = filt_keywords(text_cross_, keywords_)
    return date_info_, article_count_new_, article_count_cross_, result_new_, result_cross_ 

def main_process(keywords_):
    url = 'https://arxiv.org/list/astro-ph/new'
    DFT_key_words = ['cluster', 'AGN']
    if keywords_ == None:
        key_words = DFT_key_words
    else:
        key_words = np.char.split(keywords_, sep=',').tolist()
    contents = get_contents(url)
    date_info, article_count_new, article_count_cross, result_new, result_cross = get_info(contents, key_words)
    out_string = 'Total: ' + str(article_count_new + article_count_cross) + ' new articles (' + \
    str(article_count_cross) + ' in Cross-lists)\nKey words: ' + str(', '.join(str(i) for i in key_words)) \
    + '\nResults: ' + str(len(result_new)+len(result_cross)) + ' articles (' + str(len(result_cross)) + \
    ' in Cross-lists)\n\n'+str(date_info)+'\n\n' + '\n'.join(('\n'.join(str(i) for i in j)) for j in result_new) + '\n'.join(('\n'.join(str(i) for i in j)) for j in result_cross) + '\nend'
    return(out_string)

def send_mail(out_string_, usr_, pwd_, sender_, receivers_):
    mail_host = 'smtp.sjtu.edu.cn'  
    mail_user = usr_
    mail_password = pwd_
    sender = sender_
    receivers = receivers_
    message = MIMEText(out_string_,'plain','utf-8')   
    message['Subject'] = '[Auto] arxiv_filter - astro-ph | '+str(datetime.date.today())
    message['From'] = sender 
    message['To'] = receivers[0]
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_password) 
        smtpObj.sendmail(
            sender,receivers,message.as_string()) 
        smtpObj.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)

def usage():
    print('>>> Usage')
    print('Use parameters or edit main code directly to define your mail server.')
    print('-h --help: <help>')
    print('-k --keywords: <keywords> string A or "A,B,C"')
    print('-u --usr: <mail server username> string A\n-p --pwd: <mail server password> string A')
    print('-s --send: <mail sender address> string A')
    print('-r --receive: <mail receiver address> string A or "A,B,C"') 
    print('Example: -k "Galaxy,AGN" -u sdf -p 12345678 -s sdf@sdf.edu.cn -r "sdf@sdf.edu.cn"')


def main(argv):
    keywords = None
    usr = None
    pwd = None
    send = None
    receive = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'k:u:p:s:r:h', ['keywords=', 'usr=', 'pwd=', 'send=', 'receive=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit()
        elif opt in ['-k', '--keywords']:
            keywords = arg
            pass
        elif opt in ['-u', '--usr']:
            usr = arg
            pass
        elif opt in ['-p', '--pwd']:
            pwd = arg
            pass
        elif opt in ['-s', '--send']:
            send = arg
            pass
        elif opt in ['-r', '--receive']:
            receive = arg
            pass
        else:
            usage()
            sys.exit()
    if usr == None:
        usr = '<username>'
    if pwd == None:
        pwd = '<password>'
    if send == None:
        send = '<mail sender>'
    if receive == None:
        receive = ['<mail receiver 1>', '<mail receiver 2>']
    else:
        receive = np.char.split(receive, sep=',').tolist()
    send_mail(main_process(keywords), usr, pwd, send, receive)

if __name__ == '__main__':
    main(sys.argv)

