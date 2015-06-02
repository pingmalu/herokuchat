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
USERCON = 0
initial_value = 0
list_len = 10
mlist = [initial_value]*list_len
# print mlist
# sample_list ==[0,0,0,0,0]

class Hello(tornado.web.RequestHandler):
    def get(self):
        self.write('<h1><a href="http://im.malu.me">This is webserver for websocket.</a></h1>')
class status(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
    def get(self):
	global USERCON
        self.write(str(USERCON))
class history(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
    def get(self):
	global mlist
        self.write(tornado.escape.json_encode(mlist))

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", Hello),
			(r"/stat", status),
			(r"/stat/", status),
			(r"/history", history),
			(r"/history/", history),
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
		#self.id = enreplace_html(val[0])
		self.id = val[0]
		self.name = ''
		if (len(val) > 1):
			#self.name = enreplace_html(val[1])
			self.name = val[1]
		if (ck_login(self.id)):
			self.on_close(self)
			return
		MessageHandler.waiters.add(self)
		self.broadcast('{"u":"getall"}')
		self.broadcast('{"u":"'+self.id+'","msg":"Hi '+self.id+',欢迎来到 IM.malu.me 您可以开始聊天了!","img":"http://www.malu.me/im/img/f-1.png","user":"ADMIN"}')

	def on_close(self):
#		tmpStr = 'php /var/www/html/a.php queue:off --name=' + self.name
#		os.system(tmpStr)
		MessageHandler.waiters.remove(self)
		self.broadcast('{"u":"getall"}')

	@classmethod
	def broadcast(cls,msg):
		global USERCON
		global mlist
		global list_len
		reload(sys)
		sys.setdefaultencoding('utf-8')
		try:
			parsed = tornado.escape.json_decode(msg)
			ids = parsed['u']
		except:
			return
		if(ids == 'getall'):
			wats = []
			USERCON = 0
			for waiter in cls.waiters:
				wats.append(waiter.id+":"+waiter.name)
				USERCON = USERCON+1
			wats = list(set(wats))
		if(ids== 'all'):
			for i in range(0, list_len-1):
				mlist[i] = mlist[i+1]
			mlist[list_len - 1] = msg
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

# Server main.
def ck_login(s):
    has = False
    if '&' in s:
	has = True
    if '"' in s:
	has = True
    if '<' in s:
	has = True
    if '>' in s:
	has = True
    if( len(s) > 20 ):
	has = True
    return has
def start_tornado():
    zserver = Application()
    port = int(os.environ.get("PORT", 8000))
    zserver.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    start_tornado()

