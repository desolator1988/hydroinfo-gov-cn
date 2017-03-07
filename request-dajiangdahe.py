# coding: utf-8
import requests
import time
import re
from lxml import etree
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText


class Mail(object):
    mail_info = {
        "from": "812787189@qq.com",
        "to": '812787189@qq.com',
        "hostname": "smtp.qq.com",
        "username": "812787189@qq.com",
        "password": "dvtzncmdhmjwbejd",
        "mail_subject": "test",
        "mail_text": "hello, this is a test email, sended by py",
        "mail_encoding": "utf-8"
    }

    @classmethod
    def send_mail(cls, mail_from='', mail_to=None, host='', username='', password='', subject='', content='',
                  content_type='plain', encoding='utf-8'):
        # 这里使用SMTP_SSL就是默认使用465端口
        smtp = SMTP_SSL(host)
        smtp.set_debuglevel(1)

        smtp.ehlo(host)
        smtp.login(username, password)

        msg = MIMEText(content, content_type, encoding)
        msg["Subject"] = Header(subject, encoding)
        msg["From"] = mail_from
        msg["To"] = mail_to

        smtp.sendmail(mail_from, mail_to, msg.as_string())

        smtp.quit()

url = 'http://xxfb.hydroinfo.gov.cn/dwr/call/plaincall/IndexDwr.getSreachData.dwr'

data = {
    'callCount': 1,
    'page': '/ssIndex.html',
    'httpSessionId': 'AD86D68AC7071780898FE6C20A690666.tomcat1',
    'scriptSessionId': 'EFD5366A67FBD70A9F1C9AF0410971B4471',
    'c0-scriptName': 'IndexDwr',
    'c0-methodName': 'getSreachData',
    'c0-id': 0,
    'c0-param0': 'string:hd',
    'c0-param1': 'string:',
    'c0-param2': 'string:',
    'batchId': 1
}

cookies = dict(
    zhuzhan='57527109',
    wdcid='7089a8c7d50714ff',
    JSESSIONID='AD86D68AC7071780898FE6C20A690666.tomcat1',
    wdlast='1487431437'
)

res = requests.post(url, data=data, cookies=cookies)

page_dajiangdahe = res.text
print page_dajiangdahe

daxingshuiku_string = re.findall("<table[^>]*>[\s\S]*?<\/table>", page_dajiangdahe)[0]
page = etree.HTML(daxingshuiku_string)


tr_list = page.xpath('//tr')

output_list = []
for i in tr_list:
    liuyu = i.xpath('.//td')[0].xpath('./text()')[0]
    xingzhengqu = i.xpath('.//td')[1].xpath('./text()')[0]
    heming = i.xpath('.//td')[2].xpath('./text()')[0]
    zhanming = i.xpath('.//td')[3].xpath('./font/text()')[0]
    shijian = i.xpath('.//td')[4].xpath('./text()')[0]
    shuiwei = i.xpath('.//td')[5].xpath('./font')[0].xpath('./text()')[0]
    shuiwei_delta_flag = i.xpath('.//td')[5].xpath('./font')[1].xpath('./text()')[0]
    liuliang = i.xpath('.//td')[6].xpath('./text()')[0]
    jingjieshuiwei = i.xpath('.//td')[7].xpath('./text()')[0]
    # print liuyu, xingzhengqu, heming, zhanming, shijian, shuiwei, shuiwei_delta_flag, liuliang, jingjieshuiwei
    # print liuyu.decode('unicode-escape').encode('utf-8')
    output_list.append(
        dict(
            liuyu=liuyu.replace(u'\xa0', '').decode('unicode-escape').encode('gb2312'),
            xingzhengqu=xingzhengqu.replace(u'\xa0', '').decode('unicode-escape').encode('gb2312'),
            heming=heming.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            zhanming=zhanming.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            shijian=shijian.replace(u'\xa0', ''),
            shuiwei=shuiwei.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            shuiwei_delta_flag=shuiwei_delta_flag.replace(u'\xa0', ''),
            liuliang=liuliang.replace(u'\xa0', '').decode('unicode-escape').encode('gb2312'),
            jingjieshuiwei=jingjieshuiwei.replace(u'\xa0', ''),

        )
    )
print output_list

table_content = u''
for each in output_list:
    table_content += u'''
    <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
    </tr>
    '''.format(unicode(each['liuyu'], 'gb2312'),
               unicode(each['xingzhengqu'], 'gb2312'),
               unicode(each['heming'], 'utf-8'),
               unicode(each['zhanming'], 'utf-8'),
               unicode(each['shijian']),
               unicode(each['shuiwei'], 'utf-8'),
               each['shuiwei_delta_flag'].decode('unicode-escape'),
               unicode(each['liuliang'], 'gb2312'),
               unicode(each['jingjieshuiwei'])
               )

table_html = u'''
<table border="1">
  <tr>
    <th>流域</th>
    <th>行政区</th>
    <th>河名</th>
    <th>站名</th>
    <th>时间</th>
    <th>水位(米)</th>
    <th>水位变化</th>
    <th>流量(立方米/秒)</th>
    <th>警戒水位(米)</th>
  </tr>
  {}
  </table>
'''.format(table_content)

unix_time = int(time.time())
html = open('dajiangdahe-{}.html'.format(unix_time), 'w')

html.write(
    u"""
    <html>
    <head>
    <title>大江大河报告</title>
    </head>
    <body>
""".encode('gb2312')
           )

# print table_html
html.write(table_html.encode('GBK'))
html.close()

Mail.send_mail(
    mail_from='812787189@qq.com',
    mail_to='812787189@qq.com',
    host='smtp.qq.com',
    content_type='html',
    username='812787189@qq.com',
    password='dvtzncmdhmjwbejd',
    subject=u'大江大河报告({})'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(unix_time))),
    content=table_html
)
