# -*- coding: utf-8 -*-

import sys
import time
import json
import re
import os
import requests
import random
import sys
from collections import Counter
import threading
from optparse import OptionParser

try:
	import requests
except:
	exit('pip install requests[security]')

cookie = 'www.xxx.com'

thread_total_number = 5

# Check py version
pyversion = sys.version.split()[0]
if pyversion >= "3" or pyversion < "2.7":
	exit('Need python version 2.6.x or 2.7.x')

reload(sys)
sys.setdefaultencoding('utf-8')

# Ignore warning
requests.packages.urllib3.disable_warnings()

## ----------------------------------
## Import Color log 颜色日志
from colorlog import ColoredFormatter
import logging

class LoggingLevel:
    SYSINFO = 9
    SUCCESS = 8
    ERROR = 7
    WARNING = 6


logging.addLevelName(LoggingLevel.SYSINFO, "*")
logging.addLevelName(LoggingLevel.SUCCESS, "+")
logging.addLevelName(LoggingLevel.ERROR, "-")
logging.addLevelName(LoggingLevel.WARNING, "!")

LOGGER = logging.getLogger("NosaferLog")

formatter = ColoredFormatter(
    "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        '*':    'cyan',
        '+':     'red',
        '-':  'green',
        '!':    'yellow',
    },
     secondary_log_colors={},
     style='%'
)
LOGGER_HANDLER = logging.StreamHandler()
LOGGER_HANDLER.setFormatter(formatter)
LOGGER.addHandler(LOGGER_HANDLER)
LOGGER.setLevel(LoggingLevel.WARNING)
## ----------------------------------------

def requests_proxies():
	'''
	Proxies for every requests
	'''
	proxies = {
	'http':'',#127.0.0.1:1080 shadowsocks
	'https':''#127.0.0.1:8080 BurpSuite
	}
	return proxies

def requests_headers():
	'''
	Random UA  for every requests && Use cookie to scan
	'''
	user_agent = ['Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0',
	'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre',
	'Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60','Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14',
	'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5']
	UA = random.choice(user_agent)
	headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Referer': 'http://www.xxx.com',
	'User-Agent':UA,'Upgrade-Insecure-Requests':'1','Connection':'keep-alive','Cache-Control':'max-age=0',
	'Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8','Cookie':cookie}
	return headers

def gettitle(url, thread_number):
    '''
	Get title,status_code,content_lenth
	'''
    headers = requests_headers()
    proxies = requests_proxies()
    url = url.replace(':443','').replace('http://','').replace('https://','')
    if '://' not in url:
        url = 'http://' + url
    if ':443' in url:
        url = 'https://' + url.replace(':443','').replace('http://','').replace('https://','')
    title,code,length,content = '','','',''
    #print "[*] Scaning " + url
    LOGGER.log(LoggingLevel.SYSINFO, "Thread_number = " + str(thread_number) + " Scaning " + url)
    try:
        req = requests.get(url=url ,headers = headers ,proxies = proxies,verify = False ,timeout = 3)
        code = req.status_code
        content = req.content
        length = len(content)
        if code in range(200,405) and length != 0:
            title = re.findall(r'<title>(.*?)</title>',req.content)[0]
    except Exception as e:
        #print("[-]",e)
        pass
    return title

def write_title(file):
    file.write('''
    <meta charset='UTF-8'>
    <style>td {text-align:center}</style>
    <table border="1" cellpadding="3" cellspacing="0" style="width: 80%;margin:auto">
    <tr>
    <td><b><font color="red">Path</font></b></td>
    <td><b><font color="blue">Status_code</b></td>
    <td><b>Content-length</font></b></td>
    <td><b><font color="red">Title</font></b></td>
    <td><b><font color="blue">Link</b></td>
    </tr>''')
    file.write("\n")
    file.close()

def getallcontent(url,json_data):
    path = []
    status = []
    length = []
    redirect = []
    for num in range(0,len(json_data)):
        if json_data[num]['status'] in range(200,405):
            if json_data[num]['redirect'] is None:
                path.append(json_data[num]['path'])
                status.append(str(json_data[num]['status']))
                length.append(str(json_data[num]['content-length']))
                redirect.append(url + json_data[num]['path'])
                #print "[*] Get " + str(json_data[num]['status']) + " " + url + json_data[num]['path'] + " " + str(json_data[num]['content-length'])
                LOGGER.log(LoggingLevel.SYSINFO, "Get " + str(json_data[num]['status']) + " " + url + json_data[num]['path'] + " " + str(json_data[num]['content-length']))
            else:
                path.append(json_data[num]['path'])
                status.append(str(json_data[num]['status']))
                length.append(str(json_data[num]['content-length']))
                redirect.append(json_data[num]['redirect'])
    return path,status,length,redirect

def open_thread(thread_total_number, path, status, length, redirect, filename):
    threads_for_list = []
    for thread_number in range(thread_total_number):
        thread = threading.Thread(target=use_thread, args=(thread_total_number, thread_number, path, status, length, redirect, filename))
        thread.start()
        threads_for_list.append(thread)

def write_content(path,status,length,redirect,filename):
    if len(path) == len(status) and len(path) == len(length) and len(path) == len(redirect):
        content = checkwaf(path,status,length,redirect) ##删除被waf的内容
        path = [i[0] for i in content]
        status = [i[1] for i in content]
        length = [i[2] for i in content]
        redirect = [i[3] for i in content]
        open_thread(thread_total_number, path, status, length, redirect, filename)

def use_thread(thread_total_number, thread_number, path, status, length, redirect, filename):
    file = open(filename,'a+')
    i = -1
    for num in range(0,len(path)):
        i += 1
        if i % thread_total_number == thread_number:
            title = gettitle(redirect[num], thread_number)
            if status[num] == '200':
                if not title is None:
                    file.write("<tr><td>" + path[num] + '</td><td><font color="red">' + status[num] + "</font></td><td>" + length[num] + '</td><td><font color="blue">' + title + '</font></td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")
                else:
                    file.write("<tr><td>" + path[num] + '</td><td><font color="red">' + status[num] + "</font></td><td>" + length[num] + "</td><td>" + "Something Wrong" + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")
                write_200_status(path[num],status[num],length[num],redirect[num],title,filename,2)
            elif status[num] == '403':
                if not title is None:
                    file.write("<tr><td>" + path[num] + '</td><td><font color="green">' + status[num] + "</font></td><td>" + length[num] + '</td><td><font color="blue">' + title + '</font></td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")
                else:
                    file.write("<tr><td>" + path[num] + '</td><td><font color="green">' + status[num] + "</font></td><td>" + length[num] + "</td><td>" + "Something Wrong" + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")  
                write_403_status(path[num],status[num],length[num],redirect[num],title,filename,2)  
            else:
                if not title is None:
                    file.write("<tr><td>" + path[num] + "</td><td>" + status[num] + "</td><td>" + length[num] + "</td><td>" + title + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")
                else:
                    file.write("<tr><td>" + path[num] + "</td><td>" + status[num] + "</td><td>" + length[num] + "</td><td>" + "Something Wrong" + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect[num],redirect[num]))
                    file.write("\n")
    file.close()

def write_200_status(path,status,length,redirect,title,filename,choice):
    filename = filename[0:-5] + '-200' + '.html'
    if choice == '1':
        if os.path.exists(filename):
            LOGGER.log(LoggingLevel.SYSINFO,"Deleting older " + filename + " ...")
            os.remove(filename)
            LOGGER.log(LoggingLevel.SUCCESS,"Deleting older "  + filename + " Done")
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing lastest " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing lastest " + filename + " title Done")
            file.close()
        else:
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing " + filename + " title Done")
            file.close()
    else:       
        if os.path.exists(filename):
            if path == status and path == length and path == redirect and path == title:
                pass
            else:
                file = open(filename,'a+')
                if not title is None:
                    file.write("<tr><td>" + path + '</td><td><font color="red">' + status + "</font></td><td>" + length + '</td><td><font color="blue">' + title + '</font></td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect,redirect))
                    file.write("\n")
                else:
                    file.write("<tr><td>" + path + '</td><td><font color="red">' + status + "</font></td><td>" + length + "</td><td>" + "Something Wrong" + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect,redirect))
                    file.write("\n")
                file.close()
        else:
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing " + filename + " title Done")
            file.close()

def write_403_status(path,status,length,redirect,title,filename,choice):
    filename = filename[0:-5] + '-403' + '.html'
    if choice == '1':
        if os.path.exists(filename):
            LOGGER.log(LoggingLevel.SYSINFO,"Deleting older " + filename + " ...")
            os.remove(filename)
            LOGGER.log(LoggingLevel.SUCCESS,"Deleting older "  + filename + " Done")
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing lastest " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing lastest " + filename + " title Done")
            file.close()
        else:
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing " + filename + " title Done")
            file.close()
    else:       
        if os.path.exists(filename):
            if path == status and path == length and path == redirect and path == title:
                pass
            else:
                file = open(filename,'a+')
                if not title is None:
                    file.write("<tr><td>" + path + '</td><td><font color="red">' + status + "</font></td><td>" + length + '</td><td><font color="blue">' + title + '</font></td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect,redirect))
                    file.write("\n")
                else:
                    file.write("<tr><td>" + path + '</td><td><font color="red">' + status + "</font></td><td>" + length + "</td><td>" + "Something Wrong" + '</td><td><a href="%s" target=_blank />%s</a></td></tr>' % (redirect,redirect))
                    file.write("\n")
                file.close()
        else:
            file = open(filename,'w')
            LOGGER.log(LoggingLevel.SYSINFO,"Writing " + filename + " title")
            write_title(file)
            LOGGER.log(LoggingLevel.SUCCESS,"Writing " + filename + " title Done")
            file.close()

def checkwaf(path,status,length,redirect): 
    content = zip(path,status,length,redirect)
    for i in Counter(length).most_common():
        if i[1] > 25: ## 判断重复大于25
            for j in range(len(content)-1,-1,-1):
                if content[j][2] == i[0]:
                    content.pop(j)
        else:
            pass
    return content

def main(argv=sys.argv[1:]):
    preg_url = ''
    path = []
    status = []
    length = []
    redirect = []
    flag = 0
        
    usage = 'Usage: python json-to-file.py [-i|--ifile] target.json'
    parser = OptionParser(usage)
    parser.add_option("-i","--ifile",action='store',dest="json_file",help="Input your json file",default=None)

    (options, args) = parser.parse_args()

    json_file = options.json_file

    if json_file is None:
        LOGGER.log(LoggingLevel.ERROR,'Input your json file')
        exit()
    else:
        if os.path.exists(json_file):
            pass
        else:
            LOGGER.log(LoggingLevel.ERROR,'Json file 404 not found')
            exit()
    filename = json_file[0:-5] + ".html"
    LOGGER.log(LoggingLevel.SYSINFO,"Make your choice\n1.Write a new html.\n2.Write an existing html.")
    choice = raw_input("Input your choice:")
    if choice == '1': ## Write a new html  写入一个新的html文件
        output_file = open(filename,'w') 
        #print "[+] Writing " + filename + " title"
        LOGGER.log(LoggingLevel.SYSINFO,"Writing " + filename + " title")
        write_title(output_file)
        #print "[+] Writing " + filename + " title Done"
        LOGGER.log(LoggingLevel.SUCCESS,"Writing " + filename + " title Done")
    write_200_status("","","","","",filename,choice)
    write_403_status("","","","","",filename,choice)
    while True:
        try:
            with open(json_file,'r') as f:
                json_data = json.load(f)
                #print "[+] Load json file"
                LOGGER.log(LoggingLevel.SUCCESS,"Load json file")
            pattern = '((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'
            url = re.findall(pattern,str(json_data))
            if url[0][-2:]!= "':":
                url = url[0]
            else:
                url = url[0][:-2]
                #print "[+] Writing "+url+"...."
                LOGGER.log(LoggingLevel.SYSINFO,"Writing "+url+"....")
            if preg_url != url: ## step on the next url 扫描下一个url
                preg_url = url
                flag = 0  ## count turn  开始计算回合数
                if url[:7] == "http://":
                    if path != [] and status != [] and length != [] and redirect != []:
                        #print "[+] Writing " + url + " content"
                        LOGGER.log(LoggingLevel.SYSINFO,"Writing " + url + " content")
                        write_content(path,status,length,redirect,filename)
                        #print "[+] Writing " + url + " content Done"
                        LOGGER.log(LoggingLevel.SUCCESS,"Writing " + url + " content Done")
                elif url[:8] == "https://":
                    if path != [] and status != [] and length != [] and redirect != []:
                        #print "[+] Writing " + url + " content"
                        LOGGER.log(LoggingLevel.SYSINFO,"Writing " + url + " content")
                        write_content(path,status,length,redirect,filename)
                        #print "[+] Writing " + url + " content Done"
                        LOGGER.log(LoggingLevel.SUCCESS,"Writing " + url + " content Done")
                output_file.close()
            else:  ## Scan url 扫描url
                flag = flag + 1  ## turn + 1 回合加一
                path = []
                status = []
                length = []
                redirect = []
                json_data = json_data[url]
                if getallcontent(url,json_data) != "waf":
                    path,status,length,redirect = getallcontent(url,json_data)
                #print "[+] Waiting, No." + str(flag) + " turn"
                LOGGER.log(LoggingLevel.SYSINFO,"Waiting, No." + str(flag) + " turn")
            time.sleep(20)
            if flag == 100 and preg_url == url:  ## Write the final url content
                if url[:7] == "http://":
                    if path != [] and status != [] and length != [] and redirect != []:
                            #print "[+] Writing " + url + " content"
                            LOGGER.log(LoggingLevel.SYSINFO,"Writing " + url + " content")
                            write_content(path,status,length,redirect,filename)
                            #print "[+] Writing " + url + " content Done"
                            LOGGER.log(LoggingLevel.SUCCESS,"Writing " + url + " content Done")
                elif url[:8] == "https://":
                    if path != [] and status != [] and length != [] and redirect != []:
                        #print "[+] Writing " + url + " content"
                        LOGGER.log(LoggingLevel.SYSINFO,"Writing " + url + " content")
                        write_content(path,status,length,redirect,filename)
                        #print "[+] Writing " + url + " content Done"
                        LOGGER.log(LoggingLevel.SUCCESS,"Writing " + url + " content Done")
                break
        except Exception as e:
            #print "[-] Something wrong"
            #print "[-] " + str(e)
            LOGGER.log(LoggingLevel.WARNING,str(e))
            time.sleep(10)
            pass
    #print "[+] Task Done"
    LOGGER.log(LoggingLevel.SUCCESS,"Task Done")
	
if __name__ == '__main__':
    main()