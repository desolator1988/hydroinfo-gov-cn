# coding: utf-8
import requests
import time
import re
from lxml import etree
from smtplib import SMTP_SSL
import smtplib
from email.header import Header
import csv
import email
from email import MIMEMultipart, MIMEText, MIMEBase
import mimetypes
import os.path


url = 'http://xxfb.hydroinfo.gov.cn/dwr/call/plaincall/IndexDwr.getSreachData.dwr'
unix_time = int(time.time())
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
    output_list.append(
        dict(
            liuyu=liuyu.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            xingzhengqu=xingzhengqu.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            heming=heming.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            zhanming=zhanming.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            shijian=shijian.replace(u'\xa0', ''),
            shuiwei=shuiwei.replace(u'\xa0', '').decode('unicode-escape').encode('utf-8'),
            shuiwei_delta_flag=shuiwei_delta_flag.replace(u'\xa0', ''),
            liuliang=liuliang.replace(u'\xa0', '').decode('unicode-escape').encode('gb2312'),
            jingjieshuiwei=jingjieshuiwei.replace(u'\xa0', ''),

        )
    )
# print output_list

with open('dajiangdahe.csv', 'wb') as csvfile:
    fieldnames = ['流域', '行政区', '河名', '站名', '时间', '水位(米)', '水位变化', '流量(立方米/秒)', '警戒水位(米)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for each in output_list:

        writer.writerow({
            '流域': each['liuyu'],
            '行政区': each['xingzhengqu'],
            '河名':  each['heming'],
            '站名': each['zhanming'],
            '时间': each['shijian'],
            '水位(米)': each['shuiwei'],
            '水位变化': each['shuiwei_delta_flag'].decode('unicode-escape').encode('utf-8'),
            '流量(立方米/秒)': each['liuliang'],
            '警戒水位(米)': each['jingjieshuiwei'],
        })

main_msg = MIMEMultipart.MIMEMultipart()
file_name = 'dajiangdahe.csv'
data = open(file_name, 'rb')
ctype, encoding = mimetypes.guess_type(file_name)
if ctype is None or encoding is not None:
    ctype = 'application/octet-stream'
maintype, subtype = ctype.split('/', 1)
file_msg = MIMEBase.MIMEBase(maintype, subtype)
file_msg.set_payload(data.read())
data.close()
email.Encoders.encode_base64(file_msg)  # 把附件编码
basename = os.path.basename(file_name)
file_msg.add_header('Content-Disposition', 'attachment', filename=basename)  # 修改邮件头
main_msg.attach(file_msg)
print '------1111-1--1-1-1-----'
main_msg['From'] = '812787189@qq.com'
main_msg['To'] = '812787189@qq.com'
main_msg['Subject'] = Header(u'大江大河报告({})'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(unix_time))))
fullText = main_msg.as_string()
print '------2222--------'
print fullText
smtp = SMTP_SSL('smtp.qq.com')
smtp.set_debuglevel(1)
smtp.ehlo('smtp.qq.com')
smtp.login("812787189@qq.com", "dvtzncmdhmjwbejd")


smtp.sendmail('812787189@qq.com', '584190248@qq.com', fullText)

