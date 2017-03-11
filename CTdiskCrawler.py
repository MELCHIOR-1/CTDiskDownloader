# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 22:26:27 2017

@author: x
"""
from __future__ import print_function   # 兼容python2,3,为了打印出多个 strings，防止 Py2 把它解释成一个元组，需要写在文件首
from httptester import HttpTester
import re
import json
import os
from sys import argv
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import sys


def downloadFile(url,filepath):
    ht = HttpTester()
    ht.download(url,filepath)

def formatSize(fileSizeStr):
    item = fileSizeStr.strip().split(' ')
#    print(item)
    sizeType = item[1]
    typeDict ={'GB':1024.0,'MB':1.0,'KB':0.0009765625,'B':9.5367431640625e-07}
    factor = typeDict[sizeType]
    return float(item[0].replace(',','').strip())*factor

def isFileLink(url):
    res = re.findall(r'/i/(.+)/f',url)
    return True if len(res)>0 else False 

def getSource(baseUrl,href,folder='',dl_flag = False):
    totalSize = 0.0
    TRY_TIME = 10    
    if isFileLink(href):
        for i in range(TRY_TIME):
            try:
                ht = HttpTester()
                ht.addCookiejar()        
                unique_id = re.findall(r'/i/(.+)/f',href)[0]               
                f1page = ht.get(url=baseUrl+href,headers = {'Cookie':'d2b01ebc66d798dcd779c868dea4e212=1; unique_id=%s; renturn_url=%s'%(unique_id,baseUrl+href)})
                fileSizeStr = re.findall(r'<small>(.+)</small>',f1page)[0]
                fileName = re.findall(r'<h3>([\s\S\u4e00-\u9fa5]+)<small>',f1page)[0]
                fileSize = formatSize(fileSizeStr)
                if dl_flag:                
                    file_id = re.findall(r'<input type="hidden" id="file_id" name="file_id" value="(.+)"/>',f1page)[0]
                    print(folder,fileName,fileSizeStr)
                    p = re.compile(r"[^A-Za-z0-9 ]")
                    subpage = re.findall(r'<html>([\s\S]+)</html>',f1page)[0]
                    
                    temp_page = p.sub('',subpage)
                    compressed_page = temp_page.replace(' ','+')
                    page = ht.post(baseUrl+r'/guest_loginV3.php',{'file_id':file_id,'page_content':compressed_page})
                    link = re.findall(r"free_down_action\('(.+)', ",page)[1] +r'&mtd=1'
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    filePath = os.path.join(folder,fileName)
                    if os.path.exists(filePath):
                        size = os.path.getsize(filePath)/1024.0/1024.0  # 转换成MB
                        if size < 0.9 * fileSize: downloadFile(link,filePath)
                    else:
                        downloadFile(link,filePath)
            except Exception as e:
                print(e)
                print('Time out, the %d st time try again!' %(i+1))
                if i == TRY_TIME-1: return 0
                continue
            else:
                break
        return fileSize
    else:
        for i in range(TRY_TIME):
            try:
                ht = HttpTester()
                ht.addCookiejar()
                html = ht.get(url = baseUrl+href, headers = {'Cookie':'ab89c6824df20e143bfe6f619837441d=1',})
                data_href = re.findall(r'"sAjaxSource": "(.+)"',html)[0]
                resp = ht.get(baseUrl + data_href)
            except Exception as e:
                print(e)
                print('Time out, the %d time try again!' %(i+1))
                if i == TRY_TIME-1: return 0
                continue
            else:
                break
        data = json.loads(resp)
        for item in data['aaData']:           
            itemType = re.findall(r'id="(.+?)"',item[0])[0]
            alabel = re.findall(r'<a.+a>',item[1])[0]
#            alabel = alabel.decode('gbk')
            tree = ET.fromstring(alabel.replace('&','&amp;'))
            ahref = tree.get('href')
#            print(tree.text,ahref)
            afolder = os.path.join(folder,tree.text) if itemType == 'folder_ids' else folder
            totalSize = totalSize + getSource(baseUrl,ahref,afolder,dl_flag)
        return totalSize
            

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
#    Url = r"https://dayo1982.ctfile.com/shared/folder_7093330_a1e15a5d/16591250/"
#    folder = './'   
#    temp = Url.split('ctfile.com')
#    if len(temp) != 2:
#        print('Url input error, please check!')
#        exit(0)
#    baseUrl  = temp[0] + 'ctfile.com'
#    href = temp[1]
#    totalSize = getSource(baseUrl,href,folder,True)
#    print(totalSize)
#    
    if len(argv) == 3:
        Url = argv[1]
        folder = argv[2]       
        temp = Url.split('ctfile.com')
        if len(temp) != 2:
            print('Url input error, please check!')
            exit(0)
        baseUrl  = temp[0] + 'ctfile.com'
        href = temp[1]
        totalSize = getSource(baseUrl,href,folder,True)
        print(totalSize)
    else:
        print('Input parameter error, Usage：python CTdiskCrawler.py url folder')
