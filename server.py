#!/usr/bin/env python
#! coding: utf-8

import os
import sys
import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.websocket


class Hello(tornado.web.RequestHandler):
    def get(self):
        self.write("<h1><a href=\"http://malu.me\">This is test for websocket.</a></h1>")

# app = tornado.web.Application([
#     (r"/", Hello),
#     (r"/static/(.*)", tornado.web.StaticFileHandler, {"path":"html/static"})
# ])

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", Hello),
			(r'/message/(.+)', MessageHandler),
			(r"/static/(.*)", tornado.web.StaticFileHandler, {"path":"static"})
		]
		settings = {}
		tornado.web.Application.__init__(self, handlers, **settings)

class MessageHandler(tornado.websocket.WebSocketHandler):
	waiters = set()

	def check_origin(self, origin):
		return True

	def open(self,id):
		val = id.split('&')
		if(val[0]==''):
			return
		self.id = val[0]
		self.name = ''
		if (len(val) > 1):
			self.name = val[1]
		MessageHandler.waiters.add(self)
		self.broadcast('{"u":"getall"}')
		self.broadcast('{"u":"'+self.id+'","msg":"Hi,'+self.id+' 欢迎来到IM.malu.me 您可以开始聊天了!","img":"img/f-1.png","user":"ADMIN"}')

	def on_close(self):
#		tmpStr = 'php /var/www/html-app/webcallcenter/artisan queue:off --name=' + self.name
#		os.system(tmpStr)
		MessageHandler.waiters.remove(self)
		self.broadcast('{"u":"getall"}')

	@classmethod
	def broadcast(cls,msg):
		reload(sys)
		sys.setdefaultencoding('utf-8')
		try:
			parsed = tornado.escape.json_decode(msg)
			ids = parsed['u']
		except:
			return
		if(ids == 'getall'):
			wats = []
			for waiter in cls.waiters:
				wats.append(waiter.id+":"+waiter.name)
			wats = list(set(wats))
		for waiter in cls.waiters:
			try:
				if(ids == 'all'):
					waiter.write_message(msg)
				elif(ids == 'getall'):
					waiter.write_message(tornado.escape.json_encode(wats))
				elif(ids.count(',') > 0):
					userid = ids.split(',')
					if waiter.id in userid:
						waiter.write_message(msg)
				#elif(int(ids) == int(waiter.id)):
				elif(ids == waiter.id):
					waiter.write_message(msg)
			except:
				pass

	def on_message(self, msg):
		#parsed = tornado.escape.json_decode(msg)
		self.broadcast(msg)

# Return the interface we need to bind to.
def get_bind_interface():
    ipaddr = os.getenv("OPENSHIFT_PYTHON_IP")
    return ipaddr if ipaddr else "0.0.0.0"


def get_bind_interface_port():
    port = os.getenv("OPENSHIFT_PYTHON_PORT")
    try:
        port = int(port)
    except TypeError:
        port = 5000
    return port

# Server main.
def start_tornado():
    # Tornado server address and port number.
    tornado.options.define("address", default=get_bind_interface(),
                           help="network address/interface to bind to")
    tornado.options.define("port", default=get_bind_interface_port(),
                           help="port number to bind to", type=int)
    tornado.options.parse_command_line()

    zoptions = tornado.options.options
#    zserver = tornado.httpserver.HTTPServer(app)
    zserver = Application()
    zserver.listen(zoptions.port, zoptions.address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    start_tornado()
