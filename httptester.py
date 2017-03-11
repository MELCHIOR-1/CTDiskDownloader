# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 19:28:15 2017

@author: x
"""
from __future__ import print_function
import sys  
#import gzip 
import zlib
import socket
from future.moves.urllib import request
from future.standard_library import hooks
with hooks():
    import urllib.parse
    import urllib.error  
    import http.cookiejar
   
class HttpTester:  
    def __init__(self, timeout=10, addHeaders=True):  
        socket.setdefaulttimeout(timeout)   # 设置超时时间  
        self.__perLen = 0
   
        self.__opener = request.build_opener()  
        request.install_opener(self.__opener)  
   
        if addHeaders: self.__addHeaders()  
   
    def __error(self, e):  
        '''''错误处理,打印，并抛给上级程序处理'''  
        print(e)
        raise Exception(e)
   
    def __addHeaders(self):  
        '''''添加默认的 headers.'''  
        self.__opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'),  
                                    ('Connection', 'keep-alive'),
                                    ('Cache-Control', 'no-cache'),
                                    ('Accept-Encoding', 'gzip, deflate'),  
                                    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]  
   
    def __decode(self, webPage, charset):  
        '''''gzip解压，并根据指定的编码解码网页'''  
        if webPage.startswith(b'\x1f\x8b'):
            return zlib.decompress(webPage, 16+zlib.MAX_WBITS)
         #   return gzip.decompress(webPage).decode(charset)  
        else:  
            return webPage.decode(charset)  
   
#    def addHeader(self,paraCuple):
#        '''添加特定的header '''
#        self.__opener.addheaders.append(paraCuple)
        
    def addCookiejar(self):  
        '''''为 self.__opener 添加 cookiejar handler。'''  
        cj = http.cookiejar.CookieJar()  
        self.__opener.add_handler(request.HTTPCookieProcessor(cj))  
   
    def addProxy(self, host, type='http'):  
        '''''设置代理'''  
        proxy = request.ProxyHandler({type: host})  
        self.__opener.add_handler(proxy)  
   
    def addAuth(self, url, user, pwd):  
        '''''添加认证'''  
        pwdMsg = request.HTTPPasswordMgrWithDefaultRealm()  
        pwdMsg.add_password(None, url, user, pwd)  
        auth = request.HTTPBasicAuthHandler(pwdMsg)  
        self.__opener.add_handler(auth)  
   
    def get(self, url, params={}, headers={}, charset='UTF-8'):  
        '''''HTTP GET 方法'''  
        if params: url += '?' + urllib.parse.urlencode(params)  
        req = request.Request(url)  
        for k,v in headers.items(): req.add_header(k, v)    # 为特定的 request 添加指定的 headers  
   
        try:  
            response = request.urlopen(req)  
        except urllib.error.HTTPError as e:  
            self.__error(e)  
        else:  
            return self.__decode(response.read(), charset)  
   
    def post(self, url, params={}, headers={}, charset='UTF-8'):  
        '''''HTTP POST 方法'''  
        params = urllib.parse.urlencode(params)  
        req = request.Request(url, data=params.encode(charset))  # 带 data 参数的 request 被认为是 POST 方法。  
        for k,v in headers.items(): req.add_header(k, v)  
   
        try:  
            response = request.urlopen(req)
            data = self.__decode(response.read(), charset)
        except Exception as e:  
            self.__error(e)  
        else:  
            return data 
   
    def download(self, url, savefile, is_display = False):  
        '''''下载文件或网页'''  
        header_gzip = None  
   
        for header in self.__opener.addheaders:     # 移除支持 gzip 压缩的 header  
            if 'Accept-Encoding' in header:  
                header_gzip = header  
                self.__opener.addheaders.remove(header)  
   
        self.__perLen = 0  
        def reporthook(a, b, c):    # a:已经下载的数据大小; b:数据大小; c:远程文件大小;  
            if c > 1000000:  
                #nonlocal __perLen
                #global __perLen
                per = (100.0 * a * b) / c  
                if per>100: per=100  
                per = '{:.2f}%'.format(per)  
                print('\b'*self.__perLen, per, end='')     # 打印下载进度百分比  
                sys.stdout.flush()  
                self.__perLen = len(per)+1  
   
         
        try: 
            if is_display:
                print('--> {}\t'.format(url), end='')
                request.urlretrieve(url, savefile, reporthook)   # reporthook 为回调钩子函数，用于显示下载进度 
            else:
                request.urlretrieve(url, savefile) 
        except urllib.error.HTTPError as e:  
            self.__error(e)  
        finally:  
            self.__opener.addheaders.append(header_gzip)  
            print()  
