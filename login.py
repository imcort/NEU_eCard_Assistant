# -*- coding:utf-8 -*-  
import urllib2
import cookielib
import urllib
import re
import sys
from lxml import html
import csv
#模拟登录

def getViewState(rawpage):
    
    res_tr = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value=(.*?)/>'  
    m_tr = re.findall(res_tr,rawpage,re.S|re.M)
    __VIEWSTATE = m_tr[0][1:-2]
    res_tr = r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value=(.*?)/>'  
    m_tr = re.findall(res_tr,rawpage,re.S|re.M)
    __EVENTVALIDATION = m_tr[0][1:-2]

    return __VIEWSTATE, __EVENTVALIDATION

CaptchaUrl = "http://ecard.neu.edu.cn/SelfSearch/validateimage.ashx"
PostUrl = "http://ecard.neu.edu.cn/SelfSearch/Login.aspx"
BaseinfoUrl = "http://ecard.neu.edu.cn/SelfSearch/User/baseinfo.aspx"
CustStateInfoUrl = "http://ecard.neu.edu.cn/SelfSearch/User/CustStateInfo.aspx"
PhotoUrl = "http://ecard.neu.edu.cn/SelfSearch/User/Photo.ashx"
ConsumeInfoUrl = "http://ecard.neu.edu.cn/SelfSearch/User/ConsumeInfo.aspx"
# 地址

headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Connection': 'keep-alive',
'Content-Type': 'application/x-www-form-urlencoded',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
}
# headers

cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)
# 将cookies绑定到一个opener cookie由cookielib自动管理

username = raw_input('学号： ')
password = raw_input('密码： ')
# 用户名和密码

rawpage = opener.open(PostUrl).read()
__VIEWSTATE, __EVENTVALIDATION = getViewState(rawpage)

picture = opener.open(CaptchaUrl).read()
# 用openr访问验证码地址,获取cookie
local = open('captcha.jpg', 'wb')
local.write(picture)
local.close()
# 保存验证码到本地
SecretCode = raw_input('输入验证码： ')
# 打开保存的验证码图片 输入

postData = {
'__EVENTVALIDATION': __EVENTVALIDATION,
'__VIEWSTATE': __VIEWSTATE,
'txtUserName': username,
'txtPassword': password,
'txtVaildateCode': SecretCode,
'hfIsManager': '0',
'__EVENTTARGET': 'btnLogin',
}
# 根据抓包信息 构造表单

data = urllib.urlencode(postData)
request = urllib2.Request(PostUrl, data, headers)
try:
    response = opener.open(request)
except urllib2.HTTPError, e:
    print e.code
# 构造request请求,登录

print 'Login OK.'

request = urllib2.Request(BaseinfoUrl)
try:
    response = opener.open(request)
    result = response.read()
    tree = html.fromstring(result)
    ps = tree.xpath("//table[@class='infoTb']//td//span")
    baseinfo = []
    for i in range(len(ps)/2):
        baseinfo.append(ps[i*2+1].text) 
    print baseinfo
except urllib2.HTTPError, e:
    print e.code
#获取基本信息

picture = opener.open(PhotoUrl).read()
local = open('photo.jpg', 'wb')
local.write(picture)
local.close()
# 获取照片

rawpage = opener.open(CustStateInfoUrl).read()
__VIEWSTATE, __EVENTVALIDATION = getViewState(rawpage)
postData = {
'__EVENTVALIDATION': __EVENTVALIDATION,
'__VIEWSTATE': __VIEWSTATE,
'ctl00$ContentPlaceHolder1$rbtnType': '0',
'ctl00$ContentPlaceHolder1$txtStartDate': '2013-12-25',
'ctl00$ContentPlaceHolder1$txtEndDate': '2018-06-15',
'ctl00$ContentPlaceHolder1$btnSearch': '查  询',
}
data = urllib.urlencode(postData)
request = urllib2.Request(CustStateInfoUrl, data, headers)
try:
    response = opener.open(request)
    result = response.read()
    res_tr = r'<td>\d\d\d</td><td>(.*?)</td><td align="right">(.*?)</td>'  
    m_tr = re.findall(res_tr,result,re.S|re.M)
    for i in m_tr:
        print i[0].decode('utf-8'),i[1]
except urllib2.HTTPError, e:
    print e.code
# 获取交易汇总信息

csvFile2 = open('csvFile2.csv','w') # 设置newline，否则两行之间会空一行
writer = csv.writer(csvFile2)

rawpage = opener.open(ConsumeInfoUrl).read()
__VIEWSTATE, __EVENTVALIDATION = getViewState(rawpage)
postData = {
'__EVENTVALIDATION': __EVENTVALIDATION,
'__VIEWSTATE': __VIEWSTATE,
'ctl00$ContentPlaceHolder1$rbtnType': '0',
'ctl00$ContentPlaceHolder1$txtStartDate': '2013-12-25',
'ctl00$ContentPlaceHolder1$txtEndDate': '2018-06-15',
'ctl00$ContentPlaceHolder1$btnSearch': '查  询',
}
data = urllib.urlencode(postData)
request = urllib2.Request(ConsumeInfoUrl, data, headers)
resultlist = []
resultpage = ''
numpages = 0
try:
    response = opener.open(request)
    result = response.read()
    resultpage = result
    res_tr = r'<span id="ContentPlaceHolder1_gridView_Label1_\d">(.*?)</span>\s*</td><td>(.*?)</td><td align="right">(.*?)</td><td align="right">(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>'  

    m_tr = re.findall(res_tr,result,re.S|re.M)
    
    for i in m_tr:
        print i[0].decode('utf-8'),i[1].decode('utf-8'),i[2].decode('utf-8'),i[3].decode('utf-8'),i[4].decode('utf-8'),i[5].decode('utf-8'),i[6].decode('utf-8')
        #resultlist.append(i)
        writer.writerow(i)

    res_tr = r'(\d+)&#39;[)]" style="margin-right:5px;">&gt;&gt;</a>'
    #print int(re.findall(res_tr,result,re.S|re.M)[0])
    numpages = int(re.findall(res_tr,result,re.S|re.M)[0])

except urllib2.HTTPError, e:
    print e.code

for i in range(numpages-2):
    __VIEWSTATE, __EVENTVALIDATION = getViewState(resultpage)
    postData = {
    '__EVENTVALIDATION': __EVENTVALIDATION,
    '__VIEWSTATE': __VIEWSTATE,
    'ctl00$ContentPlaceHolder1$rbtnType': '0',
    'ctl00$ContentPlaceHolder1$txtStartDate': '2013-12-25',
    'ctl00$ContentPlaceHolder1$txtEndDate': '2018-06-15',
    'ctl00$ContentPlaceHolder1$AspNetPager1_input': str(i+2),
    'ctl00$ContentPlaceHolder1$AspNetPager1': '转到',
    }
    data = urllib.urlencode(postData)
    request = urllib2.Request(ConsumeInfoUrl, data, headers)
    
    try:
        response = opener.open(request)
        result = response.read()
        resultpage = result
        res_tr = r'<span id="ContentPlaceHolder1_gridView_Label1_\d">(.*?)</span>\s*</td><td>(.*?)</td><td align="right">(.*?)</td><td align="right">(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>'  

        m_tr = re.findall(res_tr,result,re.S|re.M)
        for i in m_tr:
            print i[0].decode('utf-8'),i[1].decode('utf-8'),i[2].decode('utf-8'),i[3].decode('utf-8'),i[4].decode('utf-8'),i[5].decode('utf-8'),i[6].decode('utf-8')
            #resultlist.append(i)
            writer.writerow(i)

    except urllib2.HTTPError, e:
        print e.code

# 获取交易信息

csvFile2.close()
