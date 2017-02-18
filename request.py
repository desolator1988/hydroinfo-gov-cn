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
        "to": "812787189@qq.com",
        "hostname": "smtp.qq.com",
        "username": "812787189@qq.com",
        "password": "dvtzncmdhmjwbejd",
        "mail_subject": "test",
        "mail_text": "hello, this is a test email, sended by py",
        "mail_encoding": "utf-8"
    }

    @classmethod
    def send_mail(cls, mail_from='', mail_to='', host='', username='', password='', subject='', content='',
                  content_type='plain', encoding='utf-8'):
        # 这里使用SMTP_SSL就是默认使用465端口
        smtp = SMTP_SSL(host)
        smtp.set_debuglevel(1)

        smtp.ehlo(host)
        smtp.login(username, password)

        msg = MIMEText(content, content_type, encoding)
        msg["Subject"] = Header(subject, encoding)
        msg["from"] = mail_from
        msg["to"] = mail_to

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
    'c0-param0': 'string:sk',
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

page_daxingshuiku = res.text
daxingshuiku_string = re.findall("<table[^>]*>[\s\S]*?<\/table>", page_daxingshuiku)[0]
page = etree.HTML(daxingshuiku_string)

tr_list = page.xpath('//tr')

output_list = []
for i in tr_list:
    liuyu = i.xpath('.//td')[0].xpath('./text()')[0]
    xingzhengqu = i.xpath('.//td')[1].xpath('./text()')[0]
    heming = i.xpath('.//td')[2].xpath('./text()')[0]
    kuming = i.xpath('.//td')[3].xpath('./font/text()')[0]
    kushuiwei = i.xpath('.//td')[4].xpath('./font/text()')[0]
    kushuiwei_delta_flag = i.xpath('.//td')[4].xpath('./font/font/text()')[0]
    xushuiliang = i.xpath('.//td')[5].xpath('./text()')[0]
    ruku = i.xpath('.//td')[6].xpath('./text()')[0]
    didinggaocheng = i.xpath('.//td')[7].xpath('./text()')[0]
    # print liuyu.decode('unicode-escape').encode('utf-8')
    output_list.append(
        dict(
            liuyu=liuyu.decode('unicode-escape').encode('gb2312'),
            xingzhengqu=xingzhengqu.decode('unicode-escape').encode('gb2312'),
            heming=heming.decode('unicode-escape').encode('utf-8'),
            kuming=kuming.decode('unicode-escape').encode('utf-8'),
            kushuiwei=kushuiwei.replace(u' ', ''),
            kushuiwei_delta_flag=kushuiwei_delta_flag.decode('unicode-escape').encode('utf-8'),
            xushuiliang=xushuiliang.decode('unicode-escape').encode('gb2312'),
            ruku=ruku,
            didinggaocheng=didinggaocheng.replace(u' ', ''),
        )
    )
# print output_list

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
               unicode(each['kuming'], 'utf-8'),
               unicode(each['kushuiwei']),
               unicode(each['kushuiwei_delta_flag'], 'utf-8'),
               unicode(each['xushuiliang'], 'gb2312'),
               unicode(each['ruku']),
               unicode(each['didinggaocheng'])
               )

table_html = u'''
<table border="1">
  <tr>
    <th>流域</th>
    <th>行政区</th>
    <th>河名</th>
    <th>水库名</th>
    <th>水库水位(米)</th>
    <th>水库水位变化</th>
    <th>需水量(亿立方米)</th>
    <th>入库(立方米/秒)</th>
    <th>堤顶高程(米)</th>
  </tr>
  {}
  </table>
'''.format(table_content)

unix_time = int(time.time())
html = open('daxingshuiku-{}.html'.format(unix_time), 'w')

html.write(
    u"""
    <html>
    <head>
    <title>大型水库报告</title>
    </head>
    <body>
""".encode('gb2312')
           )

# print table_html
html.write(table_html.encode('GBK'))
html.close()

Mail.send_mail(mail_from='812787189@qq.com', mail_to='812787189@qq.com', host='smtp.qq.com', content_type='html',
               username='812787189@qq.com', password='dvtzncmdhmjwbejd',
               subject=u'大型水库报告({})'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(unix_time))),
               content=table_html)
