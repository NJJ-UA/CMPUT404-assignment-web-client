#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

URL_RE=re.compile("^http://(?P<HOST>[A-Za-z0-9\-\.]+)(?P<PORT>:[0-9]+)?(?P<PATH>.*)$")

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return "CODE:----------\n  %s\nBODY:----------\n  %s" % (self.code, self.body)
    
class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        return client

    def handle_url(self,url):
        if not url.startswith("http://"):
            url = "http://" + url
            
        re_obj=re.search(URL_RE,url)
        host=re_obj.group('HOST')
        port_str=re_obj.group('PORT')
        path=re_obj.group('PATH')

        if not port_str:
            port=80
        else:
            port=int(port_str[1:])
            
        if path=='':
            path='/'

        return host,port,path

  
        
    def get_code(self, data):
        code = int((data.split('\r\n\r\n')[0]).split(' ')[1])
        return code

    def get_headers(self,data):
        header = data.split('\r\n\r\n')[0]
        return header

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    
    def GET(self, url, args=None):

        host,port,path=self.handle_url(url)
        try:
            client=self.connect(host,port)
        except socket.gaierror as e:
            return HTTPResponse(404, e)
        http_req = "GET %s HTTP/1.1\r\n" % path
        http_req += "Host: %s:%d \r\n" %(host,port)
        http_req += "Connection: close \r\n"
        http_req += "Accept:*/* \r\n\r\n"
        client.sendall(http_req)
        #print(http_req)
        response=self.recvall(client)

    
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        body=""
        host,port,path=self.handle_url(url)
        try:
            client=self.connect(host,port)
        except socket.gaierror as e:
            return HTTPResponse(404, e)

        if args:
            body = urllib.urlencode(args)
        http_req = "POST %s HTTP/1.1\r\n" % path
        http_req += "Host: %s:%d \r\n" %(host,port)
        http_req += "Connection: close \r\n"
        http_req += "Content-Type: application/x-www-form-urlencoded \r\n"
        http_req += "Content-Length: %d \r\n" % len(body)
        http_req += "Accept:*/* \r\n\r\n"
        client.sendall(http_req)
        client.sendall(body)
        
        
        print(http_req)
        response=self.recvall(client)

        
        
        code = self.get_code(response)
        body = self.get_body(response)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
