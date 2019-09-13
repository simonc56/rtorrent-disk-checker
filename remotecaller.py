#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from config import scgi

try:
        import xmlrpclib, socket
        import urllib, urlparse
except:
        import xmlrpc.client as xmlrpclib, socket
        from urllib import parse as urllib

class SCGIRequest(object):
        def __init__(self, url):
                self.url = url

        def __send(self, scgireq):

                try:
                        host, port = self.url.split(':')
                        addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                        sock = socket.socket(*addrinfo[0][:3])
                        sock.connect(addrinfo[0][4])
                except:
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        sock.connect(self.url)

                sock.send(scgireq.encode())
                sfile = sock.makefile()
                response = ''

                while True:
                        data = sfile.read(1024)

                        if not data:
                                break

                        response += data

                sock.close()
                return urllib.unquote(response)

        def send(self, data):
                "Send data over scgi to url and get response"
                scgiresp = self.__send(self.add_required_scgi_headers(data))
                return ''.join(scgiresp.split('\n')[4:])

        @staticmethod
        def encode_netstring(string):
                "Encode string as netstring"
                return '%d:%s,' % (len(string), string)

        @staticmethod
        def make_headers(headers):
                "Make scgi header list"
                return '\x00'.join(['%s\x00%s' % t for t in headers]) + '\x00'

        @staticmethod
        def add_required_scgi_headers(data, headers = []):
                "Wrap data in an scgi request,\nsee spec at: http://python.ca/scgi/protocol.txt"
                headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data))), ('SCGI', '1'),] + headers)
                enc_headers = SCGIRequest.encode_netstring(headers)
                return enc_headers + data

def xmlrpc(methodname, params):
        xmlreq = xmlrpclib.dumps(params, methodname)
        xmlresp = SCGIRequest(scgi).send(xmlreq)
        return xmlrpclib.loads(xmlresp)[0][0]

if __name__ == "__main__" and sys.argv[1] == "setup":
        path = sys.argv[0].rsplit('/',1)[0]
        try:
                xmlrpc("method.set_key", ("","event.download.inserted_new", "checker", "branch=((and,((not,((d.is_meta)))),((d.state)))),((stpcheck))"))
                xmlrpc("method.insert", ("","stpcheck", "simple", "d.stop=", "execute.throw.bg=python," + path + "/checker.py,$d.name=,$d.custom1=,$d.hash=,$d.directory=,$d.size_bytes="))
                #xmlrpc('method.get',('','stpcheck'))
                #xmlrpc('method.get',('',"event.download.inserted_new"))
        except:
                print('SCGI address not configured properly. Please adjust it in your config.py file before continuing.')
        sys.exit()
        