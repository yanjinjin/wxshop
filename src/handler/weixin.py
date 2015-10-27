#!/usr/bin/env python
#coding=utf8

import logging
import hashlib
from tornado.web import HTTPError
from handler import BaseHandler
from lib.route import route
from model import Oauth, User, UserVcode, Page, Apply, Shop, Ad
import xml.etree.ElementTree as ET
import time
import urllib2
import json

def get_openid(self,code):
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
        self.settings['weixin_appid'], self.settings['weixin_secret'], code)
        result = urllib2.urlopen(url).read()
        return json.loads(result).get('openid')
def get_code(self):
	url='https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base#wechat_redirect' % (
       	self.settings['weixin_appid'], self.settings['weixin_url']+'/signup')
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2')
        reader= urllib2.urlopen(request).read()
		
@route(r'/weixin', name='weixin_index')
class indexHandler(BaseHandler):
    def get_access_token(self):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
        self.settings['weixin_appid'], self.settings['weixin_secret'])
        result = urllib2.urlopen(url).read()
        self.settings['access_token'] = json.loads(result).get('access_token')
        print 'access_token===%s' % self.settings['access_token']
   
    def createMenu(self):
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % self.settings['access_token']
        data = {
           "button":[ 
            {    
               "type":"view",  
               "name":"购物车",
               "url":self.settings['weixin_url']+'/order'
                }, 
            {
               "name":"会员中心",
               "sub_button":[
               {    
                   "type":"view",
                   "name":"登录/注册",
                   "url":self.settings['weixin_url']+'/signup'
                },
                {    
                   "type":"view",
                   "name":"个人信息",
                   "url":self.settings['weixin_url']+'/user/profile'
                },
               {    
                   "type":"view",
                   "name":"我的订单",
                   "url":self.settings['weixin_url']+'/user'
                },
               {    
                   "type":"view",
                   "name":"我的积分",
                   "url":self.settings['weixin_url']+'/user/credits'
                },
               {    
                   "type":"view",
                   "name":"分享",
                   "url":self.settings['weixin_url']+"/share"
                }]
            }, 
            {    
               "type":"view",  
               "name":"微商城",
               "url":self.settings['weixin_url']
                }]			
        }
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('encoding', 'utf-8')
        response = urllib2.urlopen(req, json.dumps(data,ensure_ascii=False))
        result = response.read()	
    def message(self , body):
	data = ET.fromstring(body)
        tousername = data.find('ToUserName').text
        fromusername = data.find('FromUserName').text
        createtime = data.find('CreateTime').text
        msgtype = data.find('MsgType').text
        content = data.find('Content').text
        msgid = data.find('MsgId').text
	textTpl = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            </xml>"""
        out = textTpl % (fromusername, tousername, str(int(time.time())), msgtype, content)
        self.write(out)

    def get(self):
        token=self.settings['weixin_token']
        signature = self.get_argument("signature")
        timeStamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
		
        tmp = [token, timeStamp, nonce]
        tmp.sort()
        raw = ''.join(tmp).encode()
        sha1Str = hashlib.sha1(raw).hexdigest()
        print sha1Str
        print signature
	if sha1Str == signature:
	    echostr = self.get_argument("echostr", "default")
            if echostr != "default":
                self.write(echostr)
	    else:
		pass
    def post(self):
        signature = self.get_argument("signature")
        timeStamp = self.get_argument("timestamp")
	body = self.request.body
	self.message(body)
        self.get_access_token()
        self.createMenu()
